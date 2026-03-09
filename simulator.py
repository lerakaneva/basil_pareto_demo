import numpy as np
import pandas as pd

from schema import ExperimentSchema

# Normalization bounds (must match schema domains)
_T_MIN, _T_RANGE = 50.0, 40.0
_PH_MIN, _PH_RANGE = 4.0, 4.0
_C_MIN, _C_RANGE = 1, 4
_S_MIN, _S_RANGE = 100, 300

# Experimental noise (std dev)
_YIELD_NOISE_STD = 1.5
_PURITY_NOISE_STD = 1.0

# Output clipping bounds
_YIELD_CLIP = (0.0, 99.0)
_PURITY_CLIP = (0.0, 99.0)

# Result precision
_RESULT_DECIMALS = 2

_CATALYST_YIELD_EFFECTS = {
    "A": {"yield_boost": 0.15, "T_opt": 0.7},
    "B": {"yield_boost": -0.05, "T_opt": 0.4},
    "C": {"yield_boost": 0.05, "T_opt": 0.55},
}

_CATALYST_PURITY_EFFECTS = {
    "A": {"purity_penalty": -0.12},
    "B": {"purity_penalty": 0.15},
    "C": {"purity_penalty": 0.02},
}


def _normalize(T, p, c, s):
    return (
        (T - _T_MIN) / _T_RANGE,
        (p - _PH_MIN) / _PH_RANGE,
        (c - _C_MIN) / _C_RANGE,
        (s - _S_MIN) / _S_RANGE,
    )


def _yield_contributions(T, p, c, s, t) -> dict:
    T_norm, p_norm, c_norm, s_norm = _normalize(T, p, c, s)
    cat = _CATALYST_YIELD_EFFECTS[t]
    return {
        "base": 55,
        "temperature": 30 * T_norm,
        "pH": 10 * (1 - 4 * (p_norm - 0.625) ** 2),
        "catalyst_amount": 8 * np.sqrt(c_norm),
        "stirring": 5 * (1 - 2 * (s_norm - 0.67) ** 2),
        "catalyst_type": cat["yield_boost"] * 20,
        "temp_catalyst_interaction": -8 * (T_norm - cat["T_opt"]) ** 2,
    }


def _purity_contributions(T, p, c, s, t) -> dict:
    T_norm, p_norm, c_norm, s_norm = _normalize(T, p, c, s)
    cat = _CATALYST_PURITY_EFFECTS[t]
    return {
        "base": 88,
        "temperature": -12 * T_norm,
        "pH": 8 * (1 - 3 * (p_norm - 0.375) ** 2),
        "catalyst_amount": 6 * (1 - 4 * (c_norm - 0.5) ** 2),
        "stirring": 5 * (1 - s_norm),
        "catalyst_type": cat["purity_penalty"] * 15,
        "impurity_penalty": -10 * (T_norm - 0.6) if (t == "A" and T_norm > 0.6) else 0,
    }


def chemical_reaction_objectives(
    T, p, c, s, t, add_noise=True, return_contributions=False
):
    yield_contrib = _yield_contributions(T, p, c, s, t)
    purity_contrib = _purity_contributions(T, p, c, s, t)

    yield_pct = sum(yield_contrib.values())
    purity_pct = sum(purity_contrib.values())

    if add_noise:
        yield_pct += np.random.normal(0, _YIELD_NOISE_STD)
        purity_pct += np.random.normal(0, _PURITY_NOISE_STD)

    yield_pct = float(np.clip(yield_pct, *_YIELD_CLIP))
    purity_pct = float(np.clip(purity_pct, *_PURITY_CLIP))

    if return_contributions:
        return yield_pct, purity_pct, yield_contrib, purity_contrib
    return yield_pct, purity_pct


def fill_df(df: pd.DataFrame) -> pd.DataFrame:
    for idx, row in df.iterrows():
        T, p, c, s, t = (
            row["Temperature"],
            row["pH"],
            int(row["Catalyst amount"]),
            int(row["Stirring speed"]),
            row["Catalyst type"],
        )
        y, pur = chemical_reaction_objectives(T, p, c, s, t, add_noise=True)
        df.at[idx, "Yield"] = round(y, _RESULT_DECIMALS)
        df.at[idx, "Purity"] = round(pur, _RESULT_DECIMALS)
        print(f"Exp {idx + 1}: T={T:.1f}, pH={p:.1f}, c={c}, s={s}, t={t} -> Yield={y:.2f}%, Purity={pur:.2f}%")
    return df


def fill_experiments(
    schema: ExperimentSchema, input_csv: str, output_csv: str, seed: int | None = None
) -> pd.DataFrame:
    if seed is not None:
        np.random.seed(seed)

    df = pd.read_csv(input_csv)
    schema.validate(df)
    df = fill_df(df)

    df.to_csv(output_csv, index=False)
    print(f"\nResults saved to: {output_csv}")
    return df
