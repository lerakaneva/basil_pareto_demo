from dataclasses import dataclass, field
from typing import Literal
import pandas as pd


ParameterType = Literal["continuous", "discrete", "categorical"]


@dataclass
class Parameter:
    name: str
    type: ParameterType
    # continuous: [min, max]
    # discrete:   [min, max, step]
    # categorical: list of options
    domain: list


@dataclass
class ExperimentSchema:
    parameters: list[Parameter]
    objectives: list[str]

    @property
    def input_columns(self) -> list[str]:
        return [p.name for p in self.parameters]

    @property
    def all_columns(self) -> list[str]:
        return self.input_columns + self.objectives

    def validate(self, df: pd.DataFrame) -> None:
        missing = [c for c in self.all_columns if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        extra = [c for c in df.columns if c not in self.all_columns]
        if extra:
            raise ValueError(f"Unexpected columns: {extra}")


# Concrete schema for the chemical reaction campaign
CHEMICAL_REACTION_SCHEMA = ExperimentSchema(
    parameters=[
        Parameter("Temperature",     "continuous",  [50.0, 90.0]),
        Parameter("pH",              "continuous",  [4.0, 8.0]),
        Parameter("Catalyst amount", "discrete",    [1, 5, 1]),
        Parameter("Stirring speed",  "discrete",    [100, 400, 100]),
        Parameter("Catalyst type",   "categorical", ["A", "B", "C"]),
    ],
    objectives=["Yield", "Purity"],
)
