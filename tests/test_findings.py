"""Checks that the data is sound and the findings hold up. Run from the repository root with `pytest`."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "findings"))

import analysis as an  # noqa: E402
import build  # noqa: E402
import charts  # noqa: E402


def test_file_has_every_row_and_year():
    data = an.table()
    assert len(data) == 47
    assert list(an.years(data).columns) == list(range(1995, 2015))
    assert not data.isna().any().any()


def test_boroughs_add_up_to_london():
    assert len(an.boroughs()) == 33
    assert an.boroughs_add_up()


def test_regions_and_wales_add_up_to_england_and_wales():
    rows = an.years(an.table())
    assert (rows.loc[an.REGIONS].sum() == rows.loc["England & Wales"]).all()


def test_first_version_total_mixes_in_every_row():
    total = an.first_version_total()
    assert total == an.years(an.table())[an.BEFORE].sum()
    assert total > an.area("England & Wales")[an.BEFORE] > an.london()[an.BEFORE]


def test_first_version_growth_top_is_not_a_borough():
    assert an.first_version_growth().index[0] not in an.boroughs().index


def test_london_peaked_before_the_crash():
    assert an.peak_year("London") < an.BEFORE
    assert an.change(an.london(), an.BEFORE, 2009) < -0.5


def test_every_borough_fell():
    falls = an.borough_crash()
    assert (falls > 0.3).all()
    assert falls.index[0] == "Barking and Dagenham"


def test_recovery_runs_from_weakest_to_strongest():
    back = an.borough_recovery()
    assert back.is_monotonic_increasing
    assert back.index[0] == "Barking and Dagenham"


def test_inner_london_recovered_better():
    io = an.inner_outer().T
    assert an.recovery(io)["Inner London"] > an.recovery(io)["Outer London"]
    assert an.inner_share().loc[2010:2013].mean() > an.inner_share()[an.BEFORE]


def test_london_recovered_less_than_the_south():
    back = an.region_recovery()
    assert back["London"] < back["South East"]
    assert set(back.index[:3]) == {"North East", "North West", "Yorkshire And The Humber"}


def test_every_chart_draws_in_the_house_style():
    for name, draw in charts.ALL.items():
        svg = draw()._repr_svg_()
        width = 345 if name.startswith("tile-") else 700
        assert f'width="{width}"' in svg, name
        assert 'rx="4"' in svg, name


def test_tiles_match_in_height():
    heights = {re.search(r'height="(\d+)"', draw()._repr_svg_()).group(1)
               for name, draw in charts.ALL.items() if name.startswith("tile-")}
    assert len(heights) == 1


def test_line_charts_start_at_zero():
    for draw in (charts.london_sales, charts.inner_outer):
        assert re.search(r">0<", draw()._repr_svg_())


def test_report_has_no_unfilled_placeholders():
    text = build.report(build.facts()) + build.key_findings(build.facts())
    assert not re.search(r"\{[a-z_]+\}|\bnan\b|\[Insert", text)


def test_readme_links_to_charts_that_exist():
    readme = (ROOT / "README.md").read_text(encoding="utf-8") + (ROOT / "findings" / "README.md").read_text(encoding="utf-8")
    for path in re.findall(r"charts/([a-z-]+\.svg)", readme):
        assert (ROOT / "charts" / path).exists(), path
