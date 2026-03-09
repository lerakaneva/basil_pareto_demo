import numpy as np
import pandas as pd

from schema import ExperimentSchema, ParameterType

_DECIMALS = 2


def generate_experiments(schema: ExperimentSchema, n: int, seed: int | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = {}

    for param in schema.parameters:
        lo, hi = param.domain[0], param.domain[-1]
        if param.type == "continuous":
            rows[param.name] = np.round(rng.uniform(lo, hi, n), _DECIMALS)
        elif param.type == "discrete":
            lo, hi, step = param.domain
            values = np.arange(lo, hi + step, step)
            rows[param.name] = rng.choice(values, n).astype(float)
        elif param.type == "categorical":
            rows[param.name] = rng.choice(param.domain, n)

    for obj in schema.objectives:
        rows[obj] = None

    return pd.DataFrame(rows)
