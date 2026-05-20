from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


TIMEZONE = "Asia/Shanghai"
REPORTS_DIR = "reports"


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_now() -> datetime:
    try:
        timezone = ZoneInfo(TIMEZONE)
    except ZoneInfoNotFoundError as exc:
        raise RuntimeError(f"无法加载时区 {TIMEZONE}，请确认运行环境包含时区数据。") from exc
    return datetime.now(timezone)


def get_today(now: datetime | None = None) -> str:
    current = now or get_now()
    return current.strftime("%Y-%m-%d")


def build_report_template(date_text: str) -> str:
    return f"""# {date_text} 工作汇报

## 今日目标

- 

## 今日完成

- 

## 事务缘由

- 

## 遇到的问题

- 

## 明日计划

- 

## 思考与总结


"""


def ensure_today_report(root: Path, today: str) -> Path | None:
    reports_dir = root / REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_path = reports_dir / f"{today}.md"
    if report_path.exists():
        print(f"当日日报已存在：{report_path}")
        return None

    report_path.write_text(build_report_template(today), encoding="utf-8")
    print(f"已创建当日日报模板：{report_path}")
    return report_path


def main() -> int:
    try:
        root = get_project_root()
        today = get_today()
        ensure_today_report(root, today)
        return 0
    except Exception as exc:
        print(f"检查或创建当日日报失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
