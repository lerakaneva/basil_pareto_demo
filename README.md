# BASIL Pareto Demo

Synthetic data generation for ML-guided experimental design (BASIL).

## Setup

Dependencies are declared in `pyproject.toml` (`numpy`, `pandas`, Python ≥ 3.11).

Install with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Then run scripts with `uv run python main.py ...`.

## Modes

### `generate` — Generate preliminary experiments

Reads the campaign template to validate the expected schema, then generates `n` experiments by sampling parameters uniformly from their domains. Objectives (Yield, Purity) are left empty.

**Parameters**

| Argument | Default | Description |
|---|---|---|
| `--template` | `campaign_data_template.csv` | Template file (used for schema validation) |
| `--n` | required | Number of experiments to generate |
| `--output` | `campaign_data.csv` | Output file |
| `--seed` | None | Random seed for reproducibility |

**Example — generate 20 preliminary experiments:**

```bash
uv run python main.py generate --n 20
```

Output `campaign_data.csv`:
```
Temperature,pH,Catalyst amount,Stirring speed,Catalyst type,Yield,Purity
72.4,6.1,3.0,200.0,A,,
58.9,5.3,5.0,300.0,C,,
...
```

### `run` — Run experiments (fill objectives)

Takes a CSV with empty Yield/Purity columns and fills them using the synthetic simulator.

**Parameters**

| Argument | Default | Description |
|---|---|---|
| `--input` | `experiments.csv` | Input file with empty objectives |
| `--output` | `experiments_filled.csv` | Output file with filled objectives |
| `--seed` | None | Random seed for reproducibility |

**Example:**

```bash
uv run python main.py run --input "Chemical Multi-Objective Optimization_run_2.csv" --output "run_2_filled.csv"
```

### `plot` — Plot objectives across datasets

Overlays multiple experiment datasets on a single Yield vs Purity scatter plot. Each dataset gets a distinct color (semi-transparent to show overlap). Datasets are defined in a JSON config file.

**Parameters**

| Argument | Default | Description |
|---|---|---|
| `--config` | `plot_config.json` | Config file with dataset list and axis settings |
| `--output` | None | Save plot to file (PNG/PDF); if omitted, opens interactive window |

**Config format (`plot_config.json`):**

```json
{
    "x": "Yield",
    "y": "Purity",
    "datasets": [
        {"file": "campaign_data_1.csv",  "label": "Original data"},
        {"file": "campaign_data_2.csv",  "label": "Batch + 30 random"},
        {"file": "run_2_filled.csv",     "label": "Batch 1 BO (+10)"}
    ]
}
```

Missing files are skipped with a warning — safe to include future batches in the config in advance.

**Examples:**

```bash
# Show interactive window
uv run python main.py plot

# Save to file
uv run python main.py plot --output results.png
```
