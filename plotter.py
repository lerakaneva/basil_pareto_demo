import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Colors for up to 5 datasets: neutral -> warm progression
_COLORS = ["#7f8c8d", "#3498db", "#2ecc71", "#e67e22", "#e74c3c"]
_ALPHA = 0.6
_MARKER_SIZE = 60


def plot_objectives(config_path: str, output: str | None = None) -> None:
    with open(config_path) as f:
        config = json.load(f)

    x_col = config.get("x", "Yield")
    y_col = config.get("y", "Purity")
    datasets = config["datasets"]

    fig, ax = plt.subplots(figsize=(7, 6))

    for i, ds in enumerate(datasets):
        path = Path(ds["file"])
        if not path.exists():
            print(f"Skipping '{path}' (file not found)")
            continue

        df = pd.read_csv(path)
        color = _COLORS[i % len(_COLORS)]
        ax.scatter(
            df[x_col], df[y_col],
            label=ds["label"],
            color=color,
            alpha=_ALPHA,
            s=_MARKER_SIZE,
            edgecolors="white",
            linewidths=0.5,
        )

    ax.set_xlabel(x_col, fontsize=12)
    ax.set_ylabel(y_col, fontsize=12)
    ax.legend(framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()

    if output:
        fig.savefig(output, dpi=150)
        print(f"Plot saved to: {output}")
    else:
        plt.show()
