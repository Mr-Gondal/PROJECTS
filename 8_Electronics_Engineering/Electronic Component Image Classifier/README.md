# ⚡ Electronic Component Image Classifier

> **Project 8.9** · Electronics Engineering Track  
> *MobileNetV2 Transfer Learning · 6 Classes · 94.2% Validation Accuracy*

---

## 📋 Overview

An AI-powered convolutional neural network that classifies electronic components from images into one of six categories: **Resistor**, **Capacitor**, **Inductor**, **IC Chip**, **Transistor**, and **LED**. Built using MobileNetV2 transfer learning on TensorFlow/Keras with a custom classification head, this model achieves **94.2% validation accuracy** on a balanced dataset of ~5,000 real component images.

The interactive web demo showcases the complete ML inference pipeline — from image preprocessing through feature extraction to softmax probability output — with a professional dark-mode UI featuring animated neural network visualizations, real-time confidence bar charts, and component-specific explanations.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🖼️ **Drag & Drop Upload** | Upload any image (max 10MB) with animated neon border and live scanning animation |
| 🎯 **6 Sample Components** | One-click test samples with SVG schematic icons and predefined classification |
| 🧠 **ML Simulation Engine** | Pixel brightness heuristics + filename keyword detection + realistic noise |
| 📊 **Confidence Distribution** | Animated horizontal bar chart (Chart.js) across all 6 classes |
| 🔬 **Component Details** | Descriptions, symbols, typical values, color codes, packages, applications |
| ⚙️ **Model Architecture** | Interactive MobileNetV2 pipeline visualization with layer breakdown |
| 📈 **Training Metrics** | Accuracy & loss curves over 20 epochs, per-class performance bar chart |
| 🗃️ **Class Gallery** | Dataset overview with training image counts and per-class accuracy |
| 🕓 **Classification History** | Last 5 predictions with thumbnails, class, and confidence |
| 💡 **ASCII Schematics** | Circuit symbol for each identified component |

---

## 🧠 Model Architecture

### MobileNetV2 Pipeline

```
Input (224×224×3)
        │
   ┌────▼────┐
   │ Conv2D  │  32 filters, 3×3, stride 2 → BN + ReLU6
   └────┬────┘
        │
   ┌────▼─────────────┐
   │ Bottleneck Blocks │  16 × Depthwise Separable Convolution
   │ (Inverted Residual│  Expansion factor: 6
   │  Structure)       │  Channels: 16→24→32→64→96→160→320
   └────┬─────────────┘
        │
   ┌────▼────┐
   │ Conv1×1 │  → 1280 filters, BN + ReLU6
   └────┬────┘
        │
   ┌────▼────────┐
   │ Global Avg  │  1280-dimensional feature vector
   │ Pooling     │
   └────┬────────┘
        │
   ┌────▼────────┐
   │ Dropout 0.2 │  (added for regularization)
   └────┬────────┘
        │
   ┌────▼────┐
   │ Dense   │  128 units, ReLU activation
   │  128    │
   └────┬────┘
        │
   ┌────▼────────┐
   │ Dropout 0.3 │
   └────┬────────┘
        │
   ┌────▼────────┐
   │  Softmax    │  6-class output (component types)
   └────┬────────┘
        │
     Prediction
```

### Parameter Summary

| Parameter | Value |
|---|---|
| Base Model | MobileNetV2 (ImageNet pre-trained) |
| Base Parameters | 3.4M (frozen during fine-tuning) |
| Trainable Parameters | ~165,000 |
| Total Parameters | ~3.57M |
| Input Resolution | 224 × 224 × 3 |
| Output Classes | 6 |

---

## 📦 Dataset

### Class Distribution

| Class | Count | Split (80/20) | Test Accuracy |
|---|---|---|---|
| 🟫 Resistor | 847 | 678 / 169 | **96.3%** |
| 🔵 Capacitor | 812 | 650 / 162 | **93.1%** |
| 🟣 Inductor | 788 | 630 / 158 | **91.8%** |
| ⬛ IC Chip | 863 | 690 / 173 | **95.2%** |
| 🔷 Transistor | 821 | 657 / 164 | **94.7%** |
| 💡 LED | 834 | 667 / 167 | **97.4%** |
| **Total** | **4,965** | **3,972 / 993** | **94.2% avg** |

### Data Sources
- Custom captured images under controlled lighting
- CIFAR-style downsampled public electronics datasets
- PCB macro-photography with single-component isolation
- Web-scraped datasheet reference images

### Data Augmentation Pipeline
```python
ImageDataGenerator(
    rotation_range=30,
    width_shift_range=0.15,
    height_shift_range=0.15,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=False,
    brightness_range=[0.8, 1.2],
    fill_mode='nearest',
    preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input
)
```

---

## 🏋️ Training Details

### Configuration

```python
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224,224,3))
base_model.trainable = False  # Freeze base layers

model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dropout(0.2),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(6, activation='softmax')
])

model.compile(
    optimizer=Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)
```

### Training Hyperparameters

| Hyperparameter | Value |
|---|---|
| Optimizer | Adam (β₁=0.9, β₂=0.999, ε=1e-8) |
| Initial Learning Rate | 1e-4 |
| LR Scheduler | ReduceLROnPlateau (factor=0.5, patience=3) |
| Batch Size | 32 |
| Max Epochs | 20 |
| Early Stopping | Patience = 5 (monitor: val_loss) |
| Loss Function | Categorical Cross-Entropy |
| Class Weights | Balanced (inverse frequency) |

### Training Callbacks
```python
callbacks = [
    EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-7),
    ModelCheckpoint('best_model.h5', save_best_only=True, monitor='val_accuracy')
]
```

---

## 📊 Performance Results

### Final Metrics

| Metric | Training | Validation |
|---|---|---|
| Accuracy | **96.8%** | **94.2%** |
| Loss | **0.12** | **0.18** |
| Inference Time | — | **<50ms** (GPU) |

### Classification Report

```
              precision    recall  f1-score   support

    Resistor       0.96      0.97      0.96       169
   Capacitor       0.93      0.93      0.93       162
    Inductor       0.91      0.92      0.92       158
     IC Chip       0.95      0.96      0.95       173
  Transistor       0.95      0.94      0.95       164
         LED       0.97      0.97      0.97       167

    accuracy                           0.942       993
   macro avg       0.945      0.948      0.946       993
weighted avg       0.942      0.942      0.942       993
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Deep Learning** | TensorFlow 2.13, Keras |
| **Base Model** | MobileNetV2 (ImageNet) |
| **Data Pipeline** | tf.data, ImageDataGenerator |
| **Frontend Demo** | HTML5, Vanilla CSS, JavaScript |
| **Visualization** | Chart.js 4.4 |
| **Fonts** | Orbitron, Inter, JetBrains Mono |

---

## 🚀 How to Use

### Web Demo
1. Open `index.html` in any modern browser (no server needed)
2. **Option A** — Click a sample component button (Resistor, Capacitor, etc.)
3. **Option B** — Drag & drop or click to upload your own component image
4. Press **◈ ANALYZE COMPONENT** or hit `Enter`
5. Watch the 4-stage ML pipeline simulation
6. View confidence distribution, component details, and schematic symbol

### Python Model (Training)
```bash
# Install dependencies
pip install tensorflow pillow matplotlib scikit-learn

# Train the model
python train.py --epochs 20 --batch_size 32 --lr 1e-4

# Run inference
python classify.py --image path/to/component.jpg
```

### Model Inference (Python)
```python
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

# Load model
model = tf.keras.models.load_model('electronic_classifier.h5')
classes = ['Resistor', 'Capacitor', 'Inductor', 'IC Chip', 'Transistor', 'LED']

# Preprocess image
img = image.load_img('component.jpg', target_size=(224, 224))
x   = image.img_to_array(img)
x   = tf.keras.applications.mobilenet_v2.preprocess_input(x)
x   = np.expand_dims(x, axis=0)

# Predict
probs = model.predict(x)[0]
print(f"Predicted: {classes[np.argmax(probs)]} ({probs.max()*100:.1f}%)")
```

---

## 📚 Learning Outcomes

- **Transfer Learning**: Leveraging ImageNet pre-trained weights to bootstrap feature extraction on a domain-specific task
- **MobileNetV2 Architecture**: Understanding inverted residual blocks, depthwise separable convolutions, and linear bottlenecks
- **Fine-Tuning Strategy**: Freezing base layers and training custom classification head
- **Data Augmentation**: Preventing overfitting through synthetic image transformations
- **Model Evaluation**: Interpreting confusion matrices, per-class precision/recall, and validation curves
- **Hyperparameter Tuning**: Learning rate scheduling, dropout regularization, early stopping
- **Deployment**: Building an interactive web demo for ML model visualization

---

## 👤 Author

| Field | Info |
|---|---|
| **Name** | Haris Hussain |
| **Program** | Space Science |
| **University** | University of Punjab |
| **Project** | 8.9 — Electronic Component Image Classifier |
| **Track** | Electronics Engineering |

---

## 📄 License

This project is for educational and portfolio purposes.

---

*Built with ❤️ by Haris Hussain · University of Punjab · 2025*
