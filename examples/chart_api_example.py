"""Small API example for MingLi-Bench chart utilities.

Run from repository root:

    python examples/chart_api_example.py
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mingli_bench.bazi import bazi_from_birth_info, bazi_from_gregorian
from mingli_bench.calendar import hour_branch, parse_bazi_pillars
from mingli_bench.charts import get_chart_summary
from mingli_bench.lunar import lunar_from_solar_date, parse_chinese_lunar_date


def main() -> None:
    print("Hour branch for 23:00:", hour_branch(23))

    bazi_chart = bazi_from_gregorian("1974-04-28", hour=16, minute=40)
    print("Bazi:", bazi_chart)

    birth_info_chart = bazi_from_birth_info(
        {
            "raw": "女命：西历1978年04月05日17：00-19：00酉时  台湾生",
            "gender": "女",
            "year": 1978,
            "month": 4,
            "day": 5,
            "hour": 18,
            "minute": 0,
            "country": "中国",
            "location": "台湾",
            "calendar_type": "solar",
        }
    )
    print("Bazi from birth_info:", birth_info_chart["timezone"], birth_info_chart["month_pillar"])
    print("Parsed lunar date:", parse_chinese_lunar_date("一九八四年闰十月十七").as_dict())
    print("Fixture lunar lookup:", lunar_from_solar_date("1978-04-05"))

    bazi = parse_bazi_pillars("甲寅 戊辰 己亥 壬申")
    print("Day master:", bazi["day_master"])
    print("Five elements:", bazi["five_elements_summary"])

    chart = get_chart_summary("case_1")
    print("Case:", chart["case_id"])
    print("Bazi:", chart["bazi"]["chinese_date"])
    print("First Ziwei palace:", chart["ziwei"]["palaces"][0])


if __name__ == "__main__":
    main()
