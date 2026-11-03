"""Every chart in the project, drawn with bezel-charts (https://pypi.org/project/bezel-charts/).

Each function returns a chart, which shows up in a notebook and saves as an SVG.
"""

from __future__ import annotations

import pandas as pd

import bezel_charts as bc

try:
    from . import analysis as an
except ImportError:
    import analysis as an

# One look for the whole repo: light, in the bezel frame, with near-square corners
LOOK = {"theme": "light", "corners": 4}
WIDE = {**LOOK, "width": 700}
TILE = {**LOOK, "width": 345, "height": 120}

# Paul Tol's high-contrast palette, readable with every common kind of colour blindness and in greyscale
NAVY, OCHRE, ROSE = "#004488", "#DDAA33", "#BB5566"

REGION_NAMES = {"Yorkshire And The Humber": "Yorkshire and the Humber"}


def thousands(series: pd.Series) -> pd.Series:
    out = (series / 1000).round(1)
    out.index = out.index.astype(str)
    return out


def counted_twice():
    year = an.BEFORE
    return bc.bars(
        pd.Series(
            {
                "First version: all 47 rows": an.first_version_total(year),
                "England and Wales": int(an.area("England & Wales")[year]),
                "London": int(an.london()[year]),
            }
        ),
        heading=f"Homes sold in {year}, as the first version counted London and as published",
        horizontal=True, stat="none", show_values=True, color=[ROSE, OCHRE, NAVY], highlight="none", **WIDE,
    )


def london_sales():
    return bc.line(
        thousands(an.london()).rename("London"),
        heading="Homes sold in London each year, thousands",
        color=NAVY, height=240, decimals=0, zero=True, **WIDE,
    )


def borough_crash():
    falls = (an.borough_crash() * 100).round(0)
    return bc.bars(
        falls,
        heading="How far sales fell in each borough, 2007 to the 2008–09 low",
        horizontal=True, stat="none", show_values=True, suffix="%", decimals=0, color=NAVY, highlight="none",
        goal=round(an.crash(an.years(an.table()).loc[["London"]]).iloc[0] * 100), goal_label="London", **WIDE,
    )


def borough_recovery():
    back = (an.borough_recovery() * 100).round(0)
    ends = pd.concat([back.tail(5)[::-1], back.head(5)[::-1]])
    return bc.bars(
        ends,
        heading="Sales in 2014 as a share of 2007: the five strongest and five weakest boroughs",
        horizontal=True, stat="none", show_values=True, suffix="%", decimals=0,
        color=[NAVY] * 5 + [OCHRE] * 5, highlight="none", goal=100, goal_label="Back to 2007", **WIDE,
    )


def inner_outer():
    table = an.inner_outer() / 1000
    table.index = table.index.astype(str)
    return bc.line(
        table.round(1),
        heading="Homes sold each year, thousands",
        color=[NAVY, OCHRE], height=240, decimals=0, zero=True, **WIDE,
    )


def regions():
    back = (an.region_recovery() * 100).round(0)
    back.index = [REGION_NAMES.get(name, name) for name in back.index]
    return bc.bars(
        back,
        heading="Sales in 2014 as a share of 2007, by region",
        horizontal=True, stat="none", show_values=True, suffix="%", decimals=0,
        color=[ROSE if name == "London" else NAVY for name in back.index], highlight="none", **WIDE,
    )


# Headline tiles ------------------------------------------------------------------------------------

def tile_crash():
    fall = -an.change(an.london(), an.BEFORE, 2009) * 100
    return bc.gauge(round(fall), label="fewer sales, 2007 to 2009", heading="The crash", suffix="%", color=ROSE, **TILE)


def tile_london():
    return bc.spark(
        thousands(an.london()), heading=f"London sales in {an.LAST}", delta="none", suffix="k", decimals=0, color=NAVY,
        **{**TILE, "height": 76},  # A spark's big number takes more room, so this matches the gauge tile's height
    )


ALL = {
    "counted-twice": counted_twice,
    "london-sales": london_sales,
    "borough-crash": borough_crash,
    "borough-recovery": borough_recovery,
    "inner-outer": inner_outer,
    "regions": regions,
    "tile-crash": tile_crash,
    "tile-london": tile_london,
}
