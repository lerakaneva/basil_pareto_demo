import argparse
import pandas as pd

from schema import CHEMICAL_REACTION_SCHEMA
from generator import generate_experiments
from simulator import fill_df, fill_experiments
from plotter import plot_objectives


def generate_prelim_data(template: str, n: int, output: str, seed: int | None = None) -> None:
    template_df = pd.read_csv(template, nrows=0)
    CHEMICAL_REACTION_SCHEMA.validate(template_df)

    df = generate_experiments(CHEMICAL_REACTION_SCHEMA, n, seed=seed)
    df = fill_df(df)
    df.to_csv(output, index=False)
    print(f"\nGenerated {n} experiments with results -> '{output}'")


def run_experiments(input_file: str, output: str, seed: int | None = None) -> None:
    fill_experiments(CHEMICAL_REACTION_SCHEMA, input_file, output, seed=seed)


def main():
    parser = argparse.ArgumentParser(description="BASIL data generation demo")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    gen = subparsers.add_parser("generate", help="Generate preliminary experiment data")
    gen.add_argument("--template", default="campaign_data_template.csv")
    gen.add_argument("--n", type=int, required=True, help="Number of preliminary experiments")
    gen.add_argument("--output", default="campaign_data.csv")
    gen.add_argument("--seed", type=int, default=None)

    run = subparsers.add_parser("run", help="Run experiments and fill results")
    run.add_argument("--input", default="experiments.csv")
    run.add_argument("--output", default="experiments_filled.csv")
    run.add_argument("--seed", type=int, default=None)

    plot = subparsers.add_parser("plot", help="Plot objectives across datasets")
    plot.add_argument("--config", default="plot_config.json")
    plot.add_argument("--output", default=None, help="Save to file instead of showing")

    args = parser.parse_args()

    if args.mode == "generate":
        generate_prelim_data(args.template, args.n, args.output, seed=args.seed)
    elif args.mode == "run":
        run_experiments(args.input, args.output, seed=args.seed)
    elif args.mode == "plot":
        plot_objectives(args.config, args.output)


if __name__ == "__main__":
    main()
