"""Plot decoded cached aggregates; this is not a Power BI Desktop screenshot."""
from pathlib import Path
import csv
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    with (ROOT / "reports/cached_monthly_actuals.csv").open(encoding="utf-8", newline="") as source:
        actuals = list(csv.DictReader(source))
    with (ROOT / "reports/monthly_budget_normalized.csv").open(encoding="utf-8", newline="") as source:
        budgets = list(csv.DictReader(source))
    dates = [datetime.strptime(r["YearMonth"], "%Y-%m") for r in actuals]
    revenue = [float(r["NetSalesAmount"])/1e6 for r in actuals]
    profit = [float(r["GrossProfitAmount"])/1e6 for r in actuals]
    figure, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    axes[0].plot(dates, revenue, label="Cached actual revenue", color="#2b6cb0")
    axes[0].plot([datetime.strptime(r["BudgetMonth"], "%Y-%m-%d") for r in budgets],
                 [float(r["BudgetAmount"])/1e6 for r in budgets], label="Synthetic budget", color="#718096", linestyle="--")
    axes[0].set_ylabel("Amount (millions)")
    axes[0].legend(frameon=False)
    axes[1].plot(dates, [100*p/r if r else 0 for p, r in zip(profit, revenue)], color="#2f855a")
    axes[1].set_ylabel("Cached gross margin (%)")
    axes[1].set_xlabel("Month")
    for axis in axes:
        axis.grid(alpha=.2)
    figure.suptitle("Fictitious distributor | cached sales and synthetic planning")
    figure.text(.5, .015, "Python chart from recovered aggregates | actuals end May 2016 | Power BI refresh/save remains outstanding", ha="center", fontsize=9)
    figure.tight_layout(rect=(0, .04, 1, .95))
    figure.savefig(ROOT / "reports/recovered_aggregate_preview.png", dpi=150)
    plt.close(figure)
    print("Wrote reports/recovered_aggregate_preview.png")


if __name__ == "__main__":
    main()
