"""Every calculation in the project, as small functions that read data/housing_sales_borough.csv.

Each function returns plain pandas objects or numbers, so the charts, the report, the notebook and the tests all
share one version of every figure.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"

BEFORE, LOW_YEARS, LAST = 2007, [2008, 2009], 2014  # The last year before the crash, the crash, and the data's end
REGIONS = [
    "North East", "North West", "Yorkshire And The Humber", "East Midlands", "West Midlands", "East",
    "London", "South East", "South West", "Wales",
]


@cache
def table() -> pd.DataFrame:
    """Homes sold each year, one row per area and one column per year, exactly as published."""
    raw = pd.read_csv(DATA / "housing_sales_borough.csv")
    sales = raw.set_index("Area").filter(like="Sales-")
    sales.columns = sales.columns.str.removeprefix("Sales-").astype(int)
    sales.insert(0, "code", raw.set_index("Area")["Code"])
    return sales


def years(rows: pd.DataFrame) -> pd.DataFrame:
    return rows.drop(columns="code")


def boroughs() -> pd.DataFrame:
    """The 32 London boroughs and the City of London. Their codes start E09."""
    data = table()
    return years(data[data["code"].str.startswith("E09")])


def area(name: str) -> pd.Series:
    return years(table()).loc[name]


# 1. The first version's total --------------------------------------------------------------------

def first_version_total(year: int = BEFORE) -> int:
    """What the first version called London's total: every row added up, regions and countries included."""
    return int(years(table())[year].sum())


def row_kinds() -> pd.Series:
    """How many rows of each kind the file holds."""
    kinds = table()["code"].str[:3].map(
        {"E09": "Boroughs", "E13": "Inner and Outer London", "E12": "Regions", "E92": "Countries", "W92": "Countries",
         "K04": "England and Wales"}
    )
    return kinds.value_counts()


def boroughs_add_up() -> bool:
    """The boroughs add up exactly to the London row, and Inner plus Outer London do too."""
    london = area("London")
    return bool((boroughs().sum() == london).all() and (area("Inner London") + area("Outer London") == london).all())


# 2 and 3. London over time -----------------------------------------------------------------------

def london() -> pd.Series:
    return area("London")


def change(series: pd.Series, start: int, end: int) -> float:
    return float(series[end] / series[start] - 1)


def crash(rows: pd.DataFrame) -> pd.Series:
    """The fall from 2007 to the lower of 2008 and 2009, as a share of 2007."""
    return 1 - rows[LOW_YEARS].min(axis=1) / rows[BEFORE]


def recovery(rows: pd.DataFrame) -> pd.Series:
    """Sales in 2014 as a share of 2007."""
    return rows[LAST] / rows[BEFORE]


# 4 and 5. Boroughs -------------------------------------------------------------------------------

def borough_crash() -> pd.Series:
    return crash(boroughs()).sort_values(ascending=False)


def borough_recovery() -> pd.Series:
    return recovery(boroughs()).sort_values()


def biggest_markets(n: int = 5) -> pd.Series:
    """Boroughs with the most sales across all 20 years."""
    return boroughs().sum(axis=1).sort_values(ascending=False).head(n)


def rank_of(name: str) -> int:
    return int(boroughs().sum(axis=1).rank(ascending=False)[name])


def crash_and_recovery() -> float:
    """Correlation between how far a borough fell and how far it came back. Negative means deeper falls stayed lower."""
    return float(borough_crash().corr(borough_recovery()))


# 6. Inner and Outer London -----------------------------------------------------------------------

def inner_outer() -> pd.DataFrame:
    return pd.DataFrame({"Inner London": area("Inner London"), "Outer London": area("Outer London")})


def inner_share() -> pd.Series:
    return area("Inner London") / london()


# 7. London against the rest ----------------------------------------------------------------------

def region_crash() -> pd.Series:
    return crash(years(table()).loc[REGIONS]).sort_values(ascending=False)


def region_recovery() -> pd.Series:
    return recovery(years(table()).loc[REGIONS]).sort_values()


def london_share() -> pd.Series:
    """London's share of every sale in England and Wales."""
    return london() / area("England & Wales")


def peak_year(name: str) -> int:
    return int(area(name).idxmax())


def first_version_growth() -> pd.Series:
    """The first version's 'highest growth' table: 2014 minus 1995, dropping only the England & Wales row."""
    data = years(table()).drop(index="England & Wales")
    return (data[LAST] - data[1995]).sort_values(ascending=False)
