"""Small API example for MingLi-Bench chart utilities.

Run from repository root:

    python examples/chart_api_example.py
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mingli_bench.calendar import hour_branch, parse_bazi_pillars
from mingli_bench.charts import get_chart_summary


def main() -> None:
    print("Hour branch for 23:00:", hour_branch(23))

    bazi = parse_bazi_pillars("甲寅 戊辰 己亥 壬申")
    print("Day master:", bazi["day_master"])
    print("Five elements:", bazi["five_elements_summary"])

    chart = get_chart_summary("case_1")
    print("Case:", chart["case_id"])
    print("Bazi:", chart["bazi"]["chinese_date"])
    print("First Ziwei palace:", chart["ziwei"]["palaces"][0])


if __name__ == "__main__":
    main()
