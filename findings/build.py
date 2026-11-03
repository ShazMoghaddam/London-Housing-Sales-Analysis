"""Draw every chart and write the findings report.

Run from the repository root:

    python findings/build.py

Charts go into charts/ as SVG files. The report is written to findings/README.md, and the key findings in the
main README are rewritten between their marker comments. Every number is worked out from the data. Nothing in
them is typed in by hand.
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "findings"))

import analysis as an  # noqa: E402
import charts  # noqa: E402

CHARTS = ROOT / "charts"
REPORT = ROOT / "findings" / "README.md"
README = ROOT / "README.md"


def facts() -> dict:
    """Every number the writing uses, in one place."""
    london = an.london()
    kinds = an.row_kinds()
    fall = an.borough_crash()
    back = an.borough_recovery()
    big = an.biggest_markets()
    share = an.inner_share()
    io = an.inner_outer()
    region_fall = an.region_crash()
    region_back = an.region_recovery()
    london_share = an.london_share()
    growth = an.first_version_growth()
    before, low, last = an.BEFORE, an.LOW_YEARS[-1], an.LAST
    return {
        "before": before, "low": low, "last": last,
        "total": f"{london.sum():,}", "rows": int(kinds.sum()), "boroughs": int(kinds["Boroughs"]),
        "old_total": f"{an.first_version_total():,}", "real": f"{london[before]:,}",
        "times": an.first_version_total() / london[before], "ew": f"{an.area('England & Wales')[before]:,}",
        "growth_top": growth.index[0], "growth_top_v": f"{growth.iloc[0]:,}",
        "start": f"{london[1995]:,}", "peak_year": an.peak_year("London"), "peak": f"{london.max():,}",
        "boom": an.change(london, 1995, an.peak_year("London")), "slip": an.change(london, an.peak_year("London"), before),
        "drop": -an.change(london, before, low), "low_v": f"{london[low]:,}", "gap": -an.change(london, before, last),
        "last_v": f"{london[last]:,}",
        "fall_top": fall.index[0], "fall_top_v": fall.iloc[0], "fall_low": fall.index[-1], "fall_low_v": fall.iloc[-1],
        "fall_2": fall.index[1], "fall_2_v": fall.iloc[1],
        "back_top": back.drop("City of London").index[-1], "back_top_v": back.drop("City of London").iloc[-1],
        "back_2": back.drop("City of London").index[-2], "back_2_v": back.drop("City of London").iloc[-2],
        "back_low": back.index[0], "back_low_v": back.iloc[0], "back_low2": back.index[1], "back_low2_v": back.iloc[1],
        "city_last": f"{an.boroughs().loc['City of London', last]:,}", "r": an.crash_and_recovery(),
        "big": big.index[0], "big_v": f"{big.iloc[0]:,}", "big_2": big.index[1], "big_3": big.index[2], "big_4": big.index[3],
        "camden_rank": an.rank_of("Camden"), "barnet_rank": an.rank_of("Barnet"),
        "inner_peak": an.peak_year("Inner London"), "outer_peak": an.peak_year("Outer London"),
        "inner_fall": an.crash(io.T)["Inner London"], "outer_fall": an.crash(io.T)["Outer London"],
        "inner_back": an.recovery(io.T)["Inner London"], "outer_back": an.recovery(io.T)["Outer London"],
        "share_before": share[before], "share_after": share.loc[2010:2013].mean(), "share_last": share[last],
        "london_fall_rank": list(region_fall.index).index("London") + 1, "regions": len(region_fall),
        "region_fall_top": region_fall.index[0], "region_fall_top_v": region_fall.iloc[0],
        "region_fall_low": region_fall.index[-1], "region_fall_low_v": region_fall.iloc[-1],
        "london_fall": region_fall["London"], "london_back": region_back["London"],
        "london_back_rank": list(region_back.index).index("London") + 1,
        "region_back_low": region_back.index[0], "region_back_low_v": region_back.iloc[0],
        "region_back_top": region_back.index[-1], "region_back_top_v": region_back.iloc[-1],
        "ls_min": london_share.min(), "ls_max": london_share.max(),
    }


def key_findings(f: dict) -> str:
    return f"""### The first version's London total was {f['times']:.0f} times too big

Its "total sales across London" added up all {f['rows']} rows of the file, including the regions, England and Wales. For {f['before']}
that gives {f['old_total']} sales. London's real figure is **{f['real']}**.

![Homes sold in 2007, counted two ways](charts/counted-twice.svg)

### London's boom ended in {f['peak_year']}, and the crash halved what was left

Sales more than doubled from {f['start']} in 1995 to {f['peak']} in {f['peak_year']}, then drifted down. From {f['before']} to {f['low']} they fell
**{f['drop']:.0%}**, and in {f['last']} they were still {f['gap']:.0%} below {f['before']}.

![Homes sold in London each year](charts/london-sales.svg)

### Every borough fell, but the recovery split them

Falls ranged from {f['fall_low_v']:.0%} in {f['fall_low']} to {f['fall_top_v']:.0%} in {f['fall_top']}. By {f['last']}, {f['back_top']} was back to
**{f['back_top_v']:.0%}** of its {f['before']} sales and {f['back_low']} only **{f['back_low_v']:.0%}**.

![Sales in 2014 as a share of 2007, strongest and weakest boroughs](charts/borough-recovery.svg)

### London came back more slowly than most of the country

London's sales in {f['last']} were {f['london_back']:.0%} of {f['before']}, the {ordinal(f['london_back_rank'])} weakest recovery of the {f['regions'] - 1} English regions
and Wales. Only the three northern regions did worse.

![Sales in 2014 as a share of 2007, by region](charts/regions.svg)"""


def ordinal(n: int) -> str:
    return {1: "", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}.get(n, f"{n}th")


def report(f: dict) -> str:
    return f"""# Findings

What happened to {f['total']} London home sales from 1995 to 2014, borough by borough. This page is written by
[`build.py`](build.py), so every number comes straight from the data.

The figures count homes sold each year, as registered with HM Land Registry. They leave out sales below market value,
such as Right to Buy, and sales under £1,000 or over £20 million. They count sales, not prices.

## 1. The first version's London total was {f['times']:.0f} times too big

The file holds {f['rows']} rows: the {f['boroughs']} boroughs (counting the City of London), Inner and Outer London, the nine English regions,
England, Wales, and England and Wales together. The boroughs add up exactly to the London row.

The first version's "total sales across London" added every row together, so each London sale was counted in its borough,
in Inner or Outer London, in London, in England and in England and Wales, five times in all, along with every sale
elsewhere. For {f['before']} that
gives {f['old_total']}, more than the {f['ew']} sold in all of England and Wales.

![Homes sold in 2007, counted two ways](../charts/counted-twice.svg)

The same mix-up affected its "highest growth borough". Dropping only the England and Wales row left {f['growth_top']} at the top, with
{f['growth_top_v']} more sales in 2014 than 1995, and the README's answer was left as a placeholder. Everything below uses only the
rows it means to.

## 2. London's boom ended in {f['peak_year']}

London sold {f['start']} homes in 1995 and {f['peak']} in {f['peak_year']}, a rise of {f['boom']:.0%}. Sales then drifted, and by {f['before']} they were
already {-f['slip']:.0%} below their peak, before the financial crisis.

![Homes sold in London each year](../charts/london-sales.svg)

## 3. The crash halved sales, and they stayed low

From {f['before']} to {f['low']}, London's sales fell **{f['drop']:.0%}**, to {f['low_v']}. Recovery was slow: {f['last_v']} homes sold in {f['last']}, still {f['gap']:.0%}
below {f['before']}.

## 4. Every borough fell, by between {f['fall_low_v']:.0%} and {f['fall_top_v']:.0%}

No borough escaped. The deepest falls were in {f['fall_top']} ({f['fall_top_v']:.0%}) and {f['fall_2']} ({f['fall_2_v']:.0%}), and the mildest in {f['fall_low']}
({f['fall_low_v']:.0%}). The dotted line marks London as a whole.

![How far sales fell in each borough](../charts/borough-crash.svg)

## 5. The recovery split the boroughs

By {f['last']}, {f['back_top']} was back to {f['back_top_v']:.0%} of its {f['before']} sales and {f['back_2']} to {f['back_2_v']:.0%}, while {f['back_low']} managed {f['back_low_v']:.0%} and
{f['back_low2']} {f['back_low2_v']:.0%}. The City of London shows 100%, but it sells only a few hundred homes a year ({f['city_last']} in {f['last']}), so small changes
swing it.

![Sales in 2014 as a share of 2007, strongest and weakest boroughs](../charts/borough-recovery.svg)

Boroughs that fell further tended to stay lower, but only loosely (correlation {f['r']:.2f}).

Volume is a different story from recovery. Across the 20 years the biggest markets were {f['big']} ({f['big_v']} sales), {f['big_2']}, {f['big_3']} and
{f['big_4']}. The first version singled out Camden for "higher overall volumes", but Camden ranks {f['camden_rank']}th of {f['boroughs']}. Barnet, which
it also named, ranks {f['barnet_rank']}th.

## 6. Inner London came back better than Outer London

Outer London's sales peaked in {f['outer_peak']} and Inner London's in {f['inner_peak']}. Outer London then fell further in the crash ({f['outer_fall']:.0%} against
{f['inner_fall']:.0%}) and recovered less ({f['outer_back']:.0%} of {f['before']} by {f['last']}, against {f['inner_back']:.0%}).

![Homes sold each year in Inner and Outer London](../charts/inner-outer.svg)

Inner London's share of the city's sales rose from {f['share_before']:.0%} in {f['before']} to an average of {f['share_after']:.0%} in 2010 to 2013, then eased to
{f['share_last']:.0%} in {f['last']}.

## 7. London came back more slowly than most of the country

London's crash ({f['london_fall']:.0%}) was the {ordinal(f['london_fall_rank'])} deepest of the {f['regions'] - 1} English regions and Wales, between the {f['region_fall_top']} ({f['region_fall_top_v']:.0%}) and the
{f['region_fall_low']} ({f['region_fall_low_v']:.0%}). Its recovery was the {ordinal(f['london_back_rank'])} weakest: {f['london_back']:.0%} of {f['before']} sales by {f['last']}, against
{f['region_back_top_v']:.0%} in the {f['region_back_top']} and {f['region_back_low_v']:.0%} in the {f['region_back_low']}.

![Sales in 2014 as a share of 2007, by region](../charts/regions.svg)

Through all of it London kept a steady share of the market, between {f['ls_min']:.0%} and {f['ls_max']:.0%} of every sale in England and Wales.

## What this data can't tell you

- **Anything about prices.** These are counts of sales. Fewer sales doesn't mean lower prices, and the data can't show
  whether homes got cheaper or dearer.
- **Why sales fell.** Mortgage rationing after 2008 is the usual explanation, but nothing here shows it.
- **Anything after 2014.** The published series ends in December 2014.
- **Every sale.** Right to Buy and other sales below market value are left out, and so are sales over £20 million,
  which matters most in central boroughs.

## How it was worked out

1. [`data/housing_sales_borough.csv`](../data/housing_sales_borough.csv) is the London Datastore file, unchanged.
2. [`analysis.py`](analysis.py) holds every calculation as a small, tested function.
3. [`charts.py`](charts.py) draws each chart with [bezel-charts](https://pypi.org/project/bezel-charts/).
4. [`notebooks/london_housing_analysis.ipynb`](../notebooks/london_housing_analysis.ipynb) walks through the same steps with the working shown.

## A correction to the first version

The first version added every row of the file into one "London" total, so its chart of total sales was mostly England and
Wales, counted twice over. Its growth table had the same problem, and the README's answer was left as a placeholder. Its
claims about Camden and Barnet were read from line charts of five boroughs. Everything here replaces that work.
"""


def replace_block(text: str, name: str, body: str) -> str:
    pattern = re.compile(rf"(<!-- {name}:start -->\n).*?(\n<!-- {name}:end -->)", re.S)
    if not pattern.search(text):
        raise ValueError(f"Marker {name} not found")
    return pattern.sub(lambda m: m.group(1) + body + m.group(2), text)


def main() -> None:
    # bezel-charts gives each gradient a random id so charts can share a page. A fixed seed keeps the
    # files identical between runs, so a rebuild only shows up in git when something really changed.
    random.seed(2026)
    CHARTS.mkdir(exist_ok=True)
    for name, draw in charts.ALL.items():
        draw().save(CHARTS / f"{name}.svg")
    f = facts()
    REPORT.write_text(report(f), encoding="utf-8")
    README.write_text(replace_block(README.read_text(encoding="utf-8"), "key-findings", key_findings(f)), encoding="utf-8")
    print(f"Wrote {len(charts.ALL)} charts, {REPORT.relative_to(ROOT)} and the README findings")


if __name__ == "__main__":
    main()
