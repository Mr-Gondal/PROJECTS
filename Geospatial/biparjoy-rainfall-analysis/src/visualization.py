"""Visualization helpers for maps and rainfall figures."""

import matplotlib.pyplot as plt


def apply_publication_style():
    """Apply a clean Matplotlib style for exported portfolio figures."""
    plt.rcParams.update({
        "figure.dpi": 140,
        "savefig.dpi": 300,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 10,
    })


def save_figure(fig, path):
    """Save a Matplotlib figure with tight layout."""
    fig.savefig(path, bbox_inches="tight")