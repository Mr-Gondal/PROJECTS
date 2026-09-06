/* ============================================================================
   SeismoTrack Pakistan — application script
   ----------------------------------------------------------------------------
   Security notes (portfolio-relevant):
   - ALL USGS-sourced strings (place, url, id) are HTML-escaped before being
     interpolated into templates (DOM-XSS prevention), and link targets are
     scheme-validated (http/https only) with rel="noopener noreferrer".
   - No inline event handlers — listeners are attached here and dynamic lists
     use event delegation, which allows a strict CSP without 'unsafe-inline'.
   ========================================================================== */

// ==========================================
// CONFIGURATION & CONSTANTS
// ==========================================
const CONFIG = {
  API_BASE: 'https://earthquake.usgs.gov/fdsnws/event/1/query',
  PARAMS: {
    format: 'geojson',
    minlatitude: 23,
    maxlatitude: 38,
    minlongitude: 60,
    maxlongitude: 80,
    orderby: 'time',
    limit: 500 // USGS cap — the "1Y" view shows the most recent 500 events
  },
  LOOKBACK_DAYS: 365,
  MAP_CENTER: [30.3753, 69.3451],
  MAP_ZOOM: 5,
  REFRESH_INTERVAL: 60, // seconds
};

const CITIES = [
  { name: "Karachi",   lat: 24.8607, lon: 67.0011, pop: "16.1M" },
  { name: "Lahore",    lat: 31.5204, lon: 74.3587, pop: "13.5M" },
  { name: "Islamabad", lat: 33.6844, lon: 73.0479, pop: "1.2M"  },
  { name: "Peshawar",  lat: 34.0151, lon: 71.5249, pop: "2.3M"  },
  { name: "Quetta",    lat: 30.1798, lon: 66.9750, pop: "1.1M"  }
];

// Tectonic fault lines (simplified schematic coordinates)
const FAULT_LINES = {
  chaman: {
    name: "Chaman Fault",
    color: "#ef4444",
    coords: [
      [28.0, 65.5], [28.8, 66.0], [29.5, 66.3], [30.2, 66.8],
      [30.9, 67.1], [31.5, 67.6], [32.0, 68.0], [32.5, 68.4],
      [33.0, 68.8], [33.5, 69.2], [34.0, 69.5], [34.5, 69.8]
    ]
  },
  mbt: {
    name: "Main Boundary Thrust",
    color: "#a855f7",
    coords: [
      [33.0, 70.0], [33.5, 71.0], [33.8, 72.0], [34.0, 72.5],
      [34.2, 73.0], [34.5, 73.5], [34.8, 74.0], [35.0, 74.5],
      [35.3, 75.0], [35.5, 75.5], [35.8, 76.0], [36.0, 76.5]
    ]
  },
  makran: {
    name: "Makran Subduction Zone",
    color: "#06b6d4",
    coords: [
      [24.5, 57.5], [24.8, 59.0], [25.0, 60.5], [25.2, 62.0],
      [25.3, 63.5], [25.2, 65.0], [25.0, 66.0], [24.8, 67.0],
      [24.6, 68.0]
    ]
  }
};

// ==========================================
// STATE
// ==========================================
let allQuakes = [];
let filteredQuakes = [];
let map, markersLayer, heatLayer, faultLinesLayer;
let magChart, timeChart, depthChart;
let autoRefreshEnabled = false;
let autoRefreshTimer = null;
let refreshCountdown = CONFIG.REFRESH_INTERVAL;
let markerMap = {};

// Filter state
const filters = {
  minMagnitude: 0,
  depthCategory: 'all',
  timeDays: 'all'
};

// Impact-alert modal: shown once per quake id (not once per session),
// so a NEW significant event always triggers a fresh alert.
const shownAlertIds = new Set();

// ==========================================
// HTML ESCAPING (XSS prevention)
// ==========================================
function esc(value) {
  if (value === null || value === undefined) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function safeUrl(url) {
  // Only allow http(s) links through (blocks javascript:, data:, vbscript:)
  const u = String(url || '');
  return /^https?:\/\//i.test(u) ? u : '#';
}

// ==========================================
// HAVERSINE DISTANCE
// ==========================================
function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) ** 2 +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}

function getClosestCity(lat, lon) {
  let closest = null;
  let minDist = Infinity;
  CITIES.forEach(city => {
    const d = haversine(lat, lon, city.lat, city.lon);
    if (d < minDist) { minDist = d; closest = city; }
  });
  return { city: closest, distance: minDist };
}

// ==========================================
// MAP INITIALIZATION
// ==========================================
function initMap() {
  map = L.map('map', {
    zoomControl: true,
    attributionControl: false
  }).setView(CONFIG.MAP_CENTER, CONFIG.MAP_ZOOM);

  const darkTile = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    maxZoom: 19
  });
  darkTile.addTo(map);

  markersLayer = L.layerGroup().addTo(map);
  heatLayer = L.heatLayer([], {
    radius: 25,
    blur: 20,
    maxZoom: 10,
    max: 1.0,
    gradient: {
      0.2: '#10b981',
      0.4: '#f59e0b',
      0.6: '#f97316',
      0.8: '#ef4444',
      1.0: '#f43f5e'
    }
  });

  // Fault lines
  faultLinesLayer = L.layerGroup();
  Object.values(FAULT_LINES).forEach(fault => {
    L.polyline(fault.coords, {
      color: fault.color,
      weight: 2.5,
      opacity: 0.7,
      dashArray: '8, 6',
      className: 'fault-line'
    }).bindPopup(`<div class="eq-popup"><h3 style="color:${fault.color}">${esc(fault.name)}</h3><p style="font-size:12px;color:#94a3b8;">Major tectonic boundary</p></div>`)
    .addTo(faultLinesLayer);
  });
  faultLinesLayer.addTo(map);

  // City markers
  CITIES.forEach(city => {
    const icon = L.divIcon({
      className: '',
      html: `<div style="display:flex;align-items:center;gap:4px;white-space:nowrap;">
        <div style="width:8px;height:8px;background:#3b82f6;border-radius:50%;border:2px solid #1e3a5f;box-shadow:0 0 6px rgba(59,130,246,0.5);"></div>
        <span style="font-size:10px;color:#94a3b8;font-weight:600;text-shadow:0 1px 3px rgba(0,0,0,0.8);font-family:'Inter',sans-serif;">${esc(city.name)}</span>
      </div>`,
      iconSize: [80, 16],
      iconAnchor: [4, 8]
    });
    L.marker([city.lat, city.lon], { icon, interactive: false }).addTo(map);
  });

  const overlays = {
    "🔴 Epicenters": markersLayer,
    "🌡️ Heatmap": heatLayer,
    "📐 Fault Lines": faultLinesLayer
  };
  L.control.layers(null, overlays, { position: 'topright', collapsed: true }).addTo(map);

  L.control.attribution({ position: 'bottomright', prefix: false })
    .addAttribution('USGS | OpenStreetMap | CARTO')
    .addTo(map);

  map.on('mousemove', (e) => {
    document.getElementById('coordLat').textContent = e.latlng.lat.toFixed(4) + '°N';
    document.getElementById('coordLon').textContent = e.latlng.lng.toFixed(4) + '°E';
  });
}

// ==========================================
// MARKER STYLING
// ==========================================
function getMarkerColor(depth) {
  if (depth < 70) return '#f43f5e';
  if (depth < 300) return '#f59e0b';
  return '#10b981';
}

function getMarkerRadius(mag) {
  return Math.max(4, Math.pow(Math.max(0, mag), 1.8) * 1.5);
}

function getMarkerOpacity(mag) {
  return Math.min(0.9, 0.4 + Math.max(0, mag) * 0.08);
}

// ==========================================
// DATA FETCHING
// ==========================================
async function fetchEarthquakes() {
  const refreshBtn = document.getElementById('refreshBtn');
  refreshBtn.innerHTML = '<div class="spinner" style="width:14px;height:14px;border-width:2px;"></div><span>Loading...</span>';

  try {
    // Recompute the start time on EVERY fetch so a long-open tab never
    // keeps sliding further into the past.
    const params = new URLSearchParams({
      ...CONFIG.PARAMS,
      starttime: new Date(Date.now() - CONFIG.LOOKBACK_DAYS * 24 * 60 * 60 * 1000)
        .toISOString().split('T')[0]
    });
    const response = await fetch(`${CONFIG.API_BASE}?${params}`);

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const data = await response.json();
    allQuakes = data.features.map(f => ({
      id: f.id,
      mag: f.properties.mag || 0,
      place: f.properties.place || 'Unknown',
      time: f.properties.time,
      depth: f.geometry.coordinates[2] || 0,
      lat: f.geometry.coordinates[1],
      lon: f.geometry.coordinates[0],
      url: f.properties.url,
      felt: f.properties.felt,
      tsunami: f.properties.tsunami,
      type: f.properties.type,
      title: f.properties.title
    }));

    allQuakes.sort((a, b) => b.time - a.time);

    applyFilters();
    updateLastUpdated();
    checkImpactAlerts();

    document.getElementById('fetchError').classList.add('hidden');

  } catch (err) {
    console.error('Fetch error:', err);
    refreshBtn.innerHTML = '<i data-lucide="alert-circle" class="w-3.5 h-3.5"></i><span>Error - Retry</span>';
    lucide.createIcons();
    document.getElementById('fetchError').classList.remove('hidden');
    document.getElementById('eqList').innerHTML = `
      <div class="flex flex-col items-center justify-center h-full text-slate-500 text-xs">
        <i data-lucide="wifi-off" class="w-8 h-8 mb-2 opacity-50"></i>
        <p>Connection failed</p>
        <p class="text-[10px] text-slate-600 mt-1">Click "Refresh Data" to retry</p>
      </div>`;
    lucide.createIcons();
    return;
  }

  refreshBtn.innerHTML = '<i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i><span>Refresh Data</span>';
  lucide.createIcons();
}

// ==========================================
// FILTERS
// ==========================================
function updateFilters() {
  filters.minMagnitude = parseFloat(document.getElementById('magSlider').value);
  document.getElementById('magValue').textContent = filters.minMagnitude.toFixed(1);
  applyFilters();
}

function setDepthFilter(value) {
  filters.depthCategory = value;
  document.querySelectorAll('.depth-btn').forEach(btn => {
    const active = btn.dataset.depth === value;
    btn.classList.toggle('active', active);
    btn.style.borderColor = active ? '#f43f5e' : '#334155';
    btn.style.background = active ? '#f43f5e15' : '#1e293b';
    btn.style.color = active ? '#f43f5e' : '#e2e8f0';
  });
  applyFilters();
}

function setTimeFilter(value) {
  filters.timeDays = value;
  document.querySelectorAll('.time-btn').forEach(btn => {
    const active = String(btn.dataset.time) === String(value);
    btn.classList.toggle('active', active);
    btn.style.borderColor = active ? '#f43f5e' : '#334155';
    btn.style.background = active ? '#f43f5e15' : '#1e293b';
    btn.style.color = active ? '#f43f5e' : '#e2e8f0';
  });
  applyFilters();
}

function applyFilters() {
  const now = Date.now();
  filteredQuakes = allQuakes.filter(q => {
    if (q.mag < filters.minMagnitude) return false;

    if (filters.depthCategory === 'shallow' && q.depth >= 70) return false;
    if (filters.depthCategory === 'intermediate' && (q.depth < 70 || q.depth >= 300)) return false;
    if (filters.depthCategory === 'deep' && q.depth < 300) return false;

    if (filters.timeDays !== 'all') {
      const cutoff = now - filters.timeDays * 24 * 60 * 60 * 1000;
      if (q.time < cutoff) return false;
    }

    return true;
  });

  updateMap();
  updateList();
  updateStats();
  updateCharts();
  updateCityProximity();
}

// ==========================================
// MAP UPDATE
// ==========================================
function updateMap() {
  markersLayer.clearLayers();
  markerMap = {};

  const heatData = [];

  filteredQuakes.forEach((q, idx) => {
    const color = getMarkerColor(q.depth);
    const radius = getMarkerRadius(q.mag);
    const isRecent = idx === 0;

    const marker = L.circleMarker([q.lat, q.lon], {
      radius: radius,
      fillColor: color,
      color: color,
      weight: isRecent ? 3 : 1.5,
      opacity: isRecent ? 1 : 0.7,
      fillOpacity: getMarkerOpacity(q.mag),
      className: isRecent ? 'pulse-marker' : 'custom-marker'
    });

    const closest = getClosestCity(q.lat, q.lon);
    const timeStr = new Date(q.time).toLocaleString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });

    const magColor = q.mag >= 5 ? '#f43f5e' : q.mag >= 4 ? '#f59e0b' : '#10b981';

    // NOTE: every USGS-sourced value below is escaped via esc()/safeUrl()
    marker.bindPopup(`
      <div class="eq-popup">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
          <div style="width:42px;height:42px;border-radius:10px;background:${magColor}15;border:1px solid ${magColor}40;display:flex;align-items:center;justify-content:center;">
            <span style="font-size:18px;font-weight:900;color:${magColor};font-family:'JetBrains Mono',monospace;">${q.mag.toFixed(1)}</span>
          </div>
          <div>
            <h3 style="margin:0;font-size:13px;line-height:1.3;">${esc(q.place)}</h3>
            <p style="font-size:10px;color:#64748b;margin:0;">${timeStr}</p>
          </div>
        </div>
        <div class="stat"><span class="stat-label">Depth</span><span class="stat-value" style="color:${color}">${q.depth.toFixed(1)} km</span></div>
        <div class="stat"><span class="stat-label">Coordinates</span><span class="stat-value">${q.lat.toFixed(3)}°, ${q.lon.toFixed(3)}°</span></div>
        <div class="stat"><span class="stat-label">Nearest City</span><span class="stat-value">${esc(closest.city.name)} (${closest.distance.toFixed(0)} km)</span></div>
        ${q.felt ? `<div class="stat"><span class="stat-label">Felt Reports</span><span class="stat-value">${Number(q.felt).toLocaleString()}</span></div>` : ''}
        ${q.tsunami ? `<div class="stat"><span class="stat-label">Tsunami</span><span class="stat-value" style="color:#f43f5e;">⚠ Alert</span></div>` : ''}
        <a href="${esc(safeUrl(q.url))}" target="_blank" rel="noopener noreferrer" style="display:block;text-align:center;margin-top:8px;padding:6px;background:#334155;border-radius:6px;color:#94a3b8;text-decoration:none;font-size:11px;font-weight:600;">View on USGS →</a>
      </div>
    `, { maxWidth: 300, className: '' });

    marker.addTo(markersLayer);
    markerMap[q.id] = marker;

    // Heatmap intensity: clamp negatives (USGS can report small negative
    // magnitudes) so intensity never goes negative.
    heatData.push([q.lat, q.lon, Math.max(0, q.mag) / 9]);
  });

  heatLayer.setLatLngs(heatData);
}

// ==========================================
// EARTHQUAKE LIST
// ==========================================
function updateList() {
  const container = document.getElementById('eqList');
  document.getElementById('eventCounter').textContent = filteredQuakes.length;

  if (filteredQuakes.length === 0) {
    container.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full text-slate-500 text-xs">
        <i data-lucide="search-x" class="w-8 h-8 mb-2 opacity-50"></i>
        <p>No earthquakes match filters</p>
        <p class="text-[10px] text-slate-600 mt-1">Try lowering the magnitude slider or expanding the time range</p>
      </div>`;
    lucide.createIcons();
    return;
  }

  const html = filteredQuakes.slice(0, 100).map((q, i) => {
    const color = getMarkerColor(q.depth);
    const magColor = q.mag >= 5 ? '#f43f5e' : q.mag >= 4 ? '#f59e0b' : '#10b981';
    const timeAgo = getTimeAgo(q.time);
    const isRecent = i === 0;

    // data-quake-id + delegation replaces the old inline onclick
    return `
      <div class="eq-item flex items-center gap-3 p-2.5 rounded-lg border border-transparent ${isRecent ? 'border-[#f43f5e]/30 bg-[#f43f5e]/5' : ''}"
           data-quake-id="${esc(q.id)}" style="animation-delay:${i * 30}ms">
        <div class="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center"
             style="background:${magColor}15;border:1px solid ${magColor}30;">
          <span class="text-sm font-black font-mono" style="color:${magColor}">${q.mag.toFixed(1)}</span>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-[11px] font-semibold truncate leading-tight">${esc(q.place)}</p>
          <div class="flex items-center gap-2 mt-0.5">
            <span class="text-[9px] text-slate-500">${timeAgo}</span>
            <span class="w-1 h-1 rounded-full bg-slate-600"></span>
            <span class="text-[9px] font-mono" style="color:${color}">${q.depth.toFixed(0)}km</span>
          </div>
        </div>
        ${isRecent ? '<span class="flex-shrink-0 w-2 h-2 rounded-full bg-[#f43f5e] animate-pulse"></span>' : ''}
      </div>`;
  }).join('');

  container.innerHTML = html;
}

function flyToQuake(id) {
  const q = allQuakes.find(eq => eq.id === id);
  if (!q) return;
  map.flyTo([q.lat, q.lon], 8, { duration: 1.2 });
  setTimeout(() => {
    if (markerMap[id]) markerMap[id].openPopup();
  }, 1300);
}

function getTimeAgo(timestamp) {
  const diff = Date.now() - timestamp;
  const mins = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 30) return `${days}d ago`;
  return `${Math.floor(days/30)}mo ago`;
}

// ==========================================
// STATISTICS
// ==========================================
function updateStats() {
  const total = filteredQuakes.length;
  const maxMag = total ? Math.max(...filteredQuakes.map(q => q.mag)) : 0;
  const avgDepth = total ? filteredQuakes.reduce((s, q) => s + q.depth, 0) / total : 0;
  const shallow = filteredQuakes.filter(q => q.depth < 70).length;
  const significant = filteredQuakes.filter(q => q.mag >= 5).length;

  animateNumber('statTotal', total);
  document.getElementById('statMaxMag').textContent = maxMag.toFixed(1);
  document.getElementById('statAvgDepth').textContent = avgDepth.toFixed(0) + 'km';
  document.getElementById('statShallow').textContent = shallow;
  document.getElementById('statSignificant').textContent = significant;
}

function animateNumber(id, target) {
  const el = document.getElementById(id);
  const current = parseInt(el.textContent) || 0;
  if (current === target) return;
  const step = Math.ceil(Math.abs(target - current) / 20);
  let val = current;
  const timer = setInterval(() => {
    val += val < target ? step : -step;
    if ((step > 0 && val >= target) || (step < 0 && val <= target)) {
      val = target;
      clearInterval(timer);
    }
    el.textContent = val;
  }, 30);
}

// ==========================================
// CHARTS
// ==========================================
function initCharts() {
  const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
    },
    scales: {
      x: {
        ticks: { color: '#64748b', font: { size: 10, family: 'JetBrains Mono' } },
        grid: { color: '#1e293b', drawBorder: false }
      },
      y: {
        ticks: { color: '#64748b', font: { size: 10, family: 'JetBrains Mono' } },
        grid: { color: '#1e293b', drawBorder: false }
      }
    }
  };

  magChart = new Chart(document.getElementById('magChart'), {
    type: 'bar',
    data: {
      labels: ['0-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7+'],
      datasets: [{
        data: [0, 0, 0, 0, 0, 0, 0],
        backgroundColor: ['#10b98150', '#10b98180', '#f59e0b60', '#f59e0b90', '#f43f5e70', '#f43f5ea0', '#f43f5e'],
        borderColor: ['#10b981', '#10b981', '#f59e0b', '#f59e0b', '#f43f5e', '#f43f5e', '#f43f5e'],
        borderWidth: 1,
        borderRadius: 4,
        barThickness: 20
      }]
    },
    options: {
      ...chartDefaults,
      plugins: {
        ...chartDefaults.plugins,
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#e2e8f0',
          bodyColor: '#94a3b8',
          borderColor: '#334155',
          borderWidth: 1,
          cornerRadius: 8,
          padding: 10,
          titleFont: { family: 'Inter', weight: '600' },
          bodyFont: { family: 'JetBrains Mono' }
        }
      }
    }
  });

  timeChart = new Chart(document.getElementById('timeChart'), {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        data: [],
        borderColor: '#f43f5e',
        backgroundColor: 'rgba(244, 63, 94, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointBackgroundColor: '#f43f5e',
        pointBorderColor: '#f43f5e',
        pointHoverRadius: 6
      }]
    },
    options: {
      ...chartDefaults,
      plugins: {
        ...chartDefaults.plugins,
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#e2e8f0',
          bodyColor: '#94a3b8',
          borderColor: '#334155',
          borderWidth: 1,
          cornerRadius: 8,
          padding: 10
        }
      }
    }
  });

  depthChart = new Chart(document.getElementById('depthChart'), {
    type: 'doughnut',
    data: {
      labels: ['Shallow (<70km)', 'Intermediate', 'Deep (>300km)'],
      datasets: [{
        data: [0, 0, 0],
        backgroundColor: ['#f43f5e40', '#f59e0b40', '#10b98140'],
        borderColor: ['#f43f5e', '#f59e0b', '#10b981'],
        borderWidth: 2,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#94a3b8',
            font: { size: 10, family: 'Inter' },
            padding: 12,
            usePointStyle: true,
            pointStyleWidth: 8
          }
        },
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#e2e8f0',
          bodyColor: '#94a3b8',
          borderColor: '#334155',
          borderWidth: 1,
          cornerRadius: 8
        }
      }
    }
  });
}

function updateCharts() {
  const magBins = [0, 0, 0, 0, 0, 0, 0];
  filteredQuakes.forEach(q => {
    if (q.mag < 2) magBins[0]++;
    else if (q.mag < 3) magBins[1]++;
    else if (q.mag < 4) magBins[2]++;
    else if (q.mag < 5) magBins[3]++;
    else if (q.mag < 6) magBins[4]++;
    else if (q.mag < 7) magBins[5]++;
    else magBins[6]++;
  });
  magChart.data.datasets[0].data = magBins;
  magChart.update('none');

  const monthMap = {};
  filteredQuakes.forEach(q => {
    const d = new Date(q.time);
    const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;
    monthMap[key] = (monthMap[key] || 0) + 1;
  });
  const sortedMonths = Object.keys(monthMap).sort();
  timeChart.data.labels = sortedMonths.map(m => {
    const [y, mo] = m.split('-');
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    return months[parseInt(mo)-1] + ' ' + y.slice(2);
  });
  timeChart.data.datasets[0].data = sortedMonths.map(m => monthMap[m]);
  timeChart.update('none');

  const shallow = filteredQuakes.filter(q => q.depth < 70).length;
  const intermediate = filteredQuakes.filter(q => q.depth >= 70 && q.depth < 300).length;
  const deep = filteredQuakes.filter(q => q.depth >= 300).length;
  depthChart.data.datasets[0].data = [shallow, intermediate, deep];
  depthChart.update('none');
}

// ==========================================
// CITY PROXIMITY ANALYSIS
// ==========================================
function updateCityProximity() {
  const container = document.getElementById('cityProximity');

  if (filteredQuakes.length === 0) {
    container.innerHTML = '<p class="text-xs text-slate-500 text-center py-4">No data available</p>';
    return;
  }

  const cityStats = CITIES.map(city => {
    let minDist = Infinity;
    let nearby = 0;

    filteredQuakes.forEach(q => {
      const d = haversine(q.lat, q.lon, city.lat, city.lon);
      if (d < minDist) minDist = d;
      if (d <= 200) nearby++;
    });

    return { ...city, minDist, nearby };
  });

  container.innerHTML = cityStats.map(cs => {
    const riskColor = cs.minDist < 50 ? '#f43f5e' : cs.minDist < 150 ? '#f59e0b' : '#10b981';
    const barWidth = Math.min(100, Math.max(5, (1 - cs.minDist / 500) * 100));

    return `
      <div class="flex items-center gap-3 p-2 rounded-lg bg-[#0f172a] border border-[#1e293b]">
        <div class="flex-shrink-0 w-8 h-8 rounded-md flex items-center justify-center" style="background:${riskColor}15;border:1px solid ${riskColor}30;">
          <span class="text-[10px] font-bold" style="color:${riskColor}">${cs.nearby}</span>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold">${esc(cs.name)}</span>
            <span class="text-[10px] font-mono" style="color:${riskColor}">${cs.minDist.toFixed(0)}km</span>
          </div>
          <div class="w-full h-1 bg-[#1e293b] rounded-full mt-1 overflow-hidden">
            <div class="h-full rounded-full transition-all duration-500" style="width:${barWidth}%;background:${riskColor}"></div>
          </div>
          <p class="text-[8px] text-slate-600 mt-0.5">${cs.nearby} events within 200km</p>
        </div>
      </div>`;
  }).join('');
}

// ==========================================
// IMPACT ALERTS
// ==========================================
function checkImpactAlerts() {
  const alerts = [];

  filteredQuakes.forEach(q => {
    if (q.mag >= 5.0) {
      CITIES.forEach(city => {
        const dist = haversine(q.lat, q.lon, city.lat, city.lon);
        if (dist <= 100) {
          alerts.push({ quake: q, city: city, distance: dist });
        }
      });
    }
  });

  const section = document.getElementById('alertsSection');
  const list = document.getElementById('alertsList');
  const count = document.getElementById('alertCount');

  if (alerts.length > 0) {
    section.classList.remove('hidden');
    count.textContent = alerts.length;

    list.innerHTML = alerts.slice(0, 10).map(a => `
      <div class="flex items-center gap-2 p-2 rounded-md bg-[#f43f5e]/5 border border-[#f43f5e]/20 cursor-pointer eq-item"
           data-quake-id="${esc(a.quake.id)}">
        <div class="flex-shrink-0 w-7 h-7 rounded-md bg-[#f43f5e]/20 flex items-center justify-center">
          <span class="text-[10px] font-black text-[#f43f5e] font-mono">${a.quake.mag.toFixed(1)}</span>
        </div>
        <div class="min-w-0 flex-1">
          <p class="text-[10px] font-semibold text-[#f43f5e] truncate">M${a.quake.mag.toFixed(1)} near ${esc(a.city.name)}</p>
          <p class="text-[8px] text-slate-500">${a.distance.toFixed(0)}km from city center</p>
        </div>
      </div>`
    ).join('');

    // Show the modal for the most significant alert that has NOT been
    // acknowledged yet (per-quake, not once-per-session: a new significant
    // event must always alert the user).
    const unacknowledged = alerts
      .slice()
      .sort((a, b) => b.quake.mag - a.quake.mag)
      .find(a => !shownAlertIds.has(a.quake.id));

    if (unacknowledged) {
      const top = unacknowledged;
      const modal = document.getElementById('alertModal');
      document.getElementById('alertContent').innerHTML = `
        <p><strong class="text-white">Magnitude ${top.quake.mag.toFixed(1)}</strong> earthquake detected
        <strong class="text-[#f59e0b]">${top.distance.toFixed(0)}km</strong> from
        <strong class="text-white">${esc(top.city.name)}</strong> (pop. ${esc(top.city.pop)}).</p>
        <p class="text-slate-400">${esc(top.quake.place)}</p>
        <p class="text-slate-400 text-xs mt-1">${new Date(top.quake.time).toLocaleString()}</p>
      `;
      modal.classList.remove('hidden');
      modal.classList.add('flex');
    }
  } else {
    section.classList.add('hidden');
  }
}

function acknowledgeAlert() {
  // Mark every currently listed quake as seen so the modal only re-opens
  // for genuinely new events.
  document.querySelectorAll('#alertsList [data-quake-id]').forEach(el => {
    shownAlertIds.add(el.dataset.quakeId);
  });
  const modal = document.getElementById('alertModal');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}

// ==========================================
// AUTO REFRESH
// ==========================================
function toggleAutoRefresh() {
  autoRefreshEnabled = !autoRefreshEnabled;
  const btn = document.getElementById('autoRefreshBtn');
  const label = document.getElementById('autoRefreshLabel');

  if (autoRefreshEnabled) {
    btn.style.borderColor = '#10b981';
    btn.style.background = '#10b98115';
    label.textContent = 'ON';
    label.style.color = '#10b981';
    startAutoRefresh();
  } else {
    btn.style.borderColor = '#334155';
    btn.style.background = '#1e293b';
    label.textContent = 'Auto';
    label.style.color = '#e2e8f0';
    stopAutoRefresh();
  }
}

function startAutoRefresh() {
  refreshCountdown = CONFIG.REFRESH_INTERVAL;
  const progressBar = document.getElementById('refreshProgress');

  if (autoRefreshTimer) clearInterval(autoRefreshTimer);

  autoRefreshTimer = setInterval(() => {
    // Skip work (and reset the countdown) while the tab is hidden.
    if (document.hidden) return;

    refreshCountdown--;
    const pct = ((CONFIG.REFRESH_INTERVAL - refreshCountdown) / CONFIG.REFRESH_INTERVAL) * 100;
    progressBar.style.width = pct + '%';

    if (refreshCountdown <= 0) {
      fetchEarthquakes();
      refreshCountdown = CONFIG.REFRESH_INTERVAL;
    }
  }, 1000);
}

function stopAutoRefresh() {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer);
    autoRefreshTimer = null;
  }
  document.getElementById('refreshProgress').style.width = '0%';
}

function toggleRightSidebar() {
  const sidebar = document.querySelector('.right-sidebar');
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  sidebar.classList.toggle('open');
  toggleBtn.classList.toggle('open', sidebar.classList.contains('open'));
}

function updateLastUpdated() {
  const now = new Date();
  document.getElementById('lastUpdated').textContent = now.toLocaleTimeString('en-US', { hour12: false });
}

// ==========================================
// GEOJSON EXPORT
// ==========================================
function exportGeoJSON() {
  const geojson = {
    type: "FeatureCollection",
    metadata: {
      title: "SeismoTrack Pakistan - Filtered Earthquake Data",
      generated: new Date().toISOString(),
      count: filteredQuakes.length
    },
    features: filteredQuakes.map(q => ({
      type: "Feature",
      properties: {
        mag: q.mag,
        place: q.place,
        time: q.time,
        depth: q.depth,
        url: q.url,
        felt: q.felt,
        tsunami: q.tsunami
      },
      geometry: {
        type: "Point",
        coordinates: [q.lon, q.lat, q.depth]
      }
    }))
  };

  const blob = new Blob([JSON.stringify(geojson, null, 2)], { type: 'application/geo+json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `seismotrack-pakistan-${new Date().toISOString().split('T')[0]}.geojson`;
  document.body.appendChild(a);   // Firefox requires the anchor in the DOM
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ==========================================
// EVENT WIRING (no inline handlers — CSP-safe)
// ==========================================
function wireEvents() {
  document.getElementById('refreshBtn').addEventListener('click', fetchEarthquakes);
  document.getElementById('autoRefreshBtn').addEventListener('click', toggleAutoRefresh);
  document.getElementById('magSlider').addEventListener('input', updateFilters);

  document.querySelectorAll('.depth-btn').forEach(btn =>
    btn.addEventListener('click', () => setDepthFilter(btn.dataset.depth)));

  document.querySelectorAll('.time-btn').forEach(btn =>
    btn.addEventListener('click', () => setTimeFilter(btn.dataset.time)));

  document.getElementById('exportBtn').addEventListener('click', exportGeoJSON);
  document.getElementById('sidebarToggleBtn').addEventListener('click', toggleRightSidebar);
  document.getElementById('alertAckBtn').addEventListener('click', acknowledgeAlert);

  const mobileToggle = document.querySelector('.mobile-toggle');
  if (mobileToggle) {
    mobileToggle.addEventListener('click', () =>
      document.querySelector('.left-sidebar').classList.toggle('open'));
  }

  const sidebarClose = document.querySelector('.sidebar-close');
  if (sidebarClose) {
    sidebarClose.addEventListener('click', toggleRightSidebar);
  }

  // Event delegation for dynamically rendered quake lists
  document.getElementById('eqList').addEventListener('click', (e) => {
    const item = e.target.closest('[data-quake-id]');
    if (item) flyToQuake(item.dataset.quakeId);
  });
  document.getElementById('alertsList').addEventListener('click', (e) => {
    const item = e.target.closest('[data-quake-id]');
    if (item) flyToQuake(item.dataset.quakeId);
  });

  // Pause the countdown whenever the tab is hidden
  document.addEventListener('visibilitychange', () => {
    const bar = document.getElementById('refreshProgress');
    if (document.hidden) {
      bar.style.width = '0%';
    }
  });
}

// ==========================================
// LOADING SEQUENCE
// ==========================================
async function initApp() {
  const loadingBar = document.getElementById('loadingBar');
  const loadingText = document.getElementById('loadingText');

  loadingText.textContent = 'Initializing map engine...';
  loadingBar.style.width = '20%';
  await sleep(300);
  initMap();

  loadingText.textContent = 'Calibrating analytics modules...';
  loadingBar.style.width = '40%';
  await sleep(200);
  initCharts();

  loadingText.textContent = 'Connecting to USGS seismic network...';
  loadingBar.style.width = '60%';
  await fetchEarthquakes();

  loadingText.textContent = 'Rendering seismic data...';
  loadingBar.style.width = '85%';
  await sleep(300);

  setDepthFilter('all');
  setTimeFilter('all');

  loadingText.textContent = 'System operational.';
  loadingBar.style.width = '100%';
  await sleep(400);

  const overlay = document.getElementById('loadingOverlay');
  overlay.style.transition = 'opacity 0.5s ease';
  overlay.style.opacity = '0';
  setTimeout(() => overlay.remove(), 500);

  lucide.createIcons();
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ==========================================
// BOOT
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
  wireEvents();
  initApp();
});
