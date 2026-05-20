from __future__ import annotations

import sys
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import markdown


PROJECT_NAME = "科研实习工作记录"
TIMEZONE = "Asia/Shanghai"
REPORTS_DIR = "reports"
WEEKLY_DIR = "weekly"
PAPER_NOTES_DIR = "paper-notes"
MILESTONES_FILE = "milestones.md"
FEEDBACK_FILE = "feedback/feedback-log.md"
RECENT_REPORT_LIMIT = 10
SITE_URL = "https://georgeorange-crypto.github.io/Research-Record/"
FEEDBACK_ISSUES_URL = "https://github.com/georgeorange-crypto/Research-Record/issues?q=is%3Aissue%20label%3Apage-feedback"
NEW_FEEDBACK_URL = "https://github.com/georgeorange-crypto/Research-Record/issues/new?template=feedback.yml"


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_now() -> datetime:
    try:
        timezone = ZoneInfo(TIMEZONE)
    except ZoneInfoNotFoundError as exc:
        raise RuntimeError(f"无法加载时区 {TIMEZONE}，请确认 Python 环境包含 tzdata。") from exc
    return datetime.now(timezone)


def get_today(now: datetime | None = None) -> str:
    current = now or get_now()
    return current.strftime("%Y-%m-%d")


def load_markdown(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"读取 Markdown 文件失败：{path}") from exc


def render_markdown(markdown_text: str) -> str:
    return markdown.markdown(
        markdown_text,
        extensions=["extra", "tables", "fenced_code", "sane_lists", "toc"],
        output_format="html5",
    )


def extract_title(path: Path, fallback: str) -> str:
    text = load_markdown(path)
    if not text:
        return fallback
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def parse_date_from_stem(stem: str) -> datetime | None:
    for pattern in ("%Y-%m-%d", "%Y-W%W", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(stem, pattern)
        except ValueError:
            continue
    return None


def list_markdown_entries(directory: Path, href_prefix: str) -> list[dict[str, str]]:
    if not directory.exists() or not directory.is_dir():
        return []

    entries: list[dict[str, str]] = []
    for path in directory.glob("*.md"):
        sort_date = parse_date_from_stem(path.stem)
        sort_key = sort_date.strftime("%Y-%m-%d") if sort_date else path.stem
        title = extract_title(path, f"{path.stem} 记录")
        entries.append(
            {
                "date": path.stem,
                "title": title,
                "href": f"{href_prefix}/{path.name}",
                "sort_key": sort_key,
                "path": str(path),
            }
        )

    return sorted(entries, key=lambda item: item["sort_key"], reverse=True)


def list_recent_reports(reports_dir: Path, limit: int = RECENT_REPORT_LIMIT) -> list[dict[str, str]]:
    return list_markdown_entries(reports_dir, REPORTS_DIR)[:limit]


def get_latest_entry(entries: list[dict[str, str]]) -> dict[str, str] | None:
    return entries[0] if entries else None


def build_report_list(entries: list[dict[str, str]], empty_text: str) -> str:
    if not entries:
        return f'<p class="empty-note">{escape(empty_text)}</p>'

    items = "\n".join(
        f'<li><a href="{escape(entry["href"])}">{escape(entry["title"])}</a>'
        f'<time datetime="{escape(entry["date"])}">{escape(entry["date"])}</time></li>'
        for entry in entries
    )
    return f'<ul class="entry-list">\n{items}\n</ul>'


def build_stat_cards(
    reports: list[dict[str, str]],
    weekly_reports: list[dict[str, str]],
    generated_at: str,
    today: str,
) -> str:
    current_month = today[:7]
    month_count = sum(1 for report in reports if report["date"].startswith(current_month))
    latest_weekly = get_latest_entry(weekly_reports)
    latest_weekly_text = latest_weekly["date"] if latest_weekly else "暂无"

    cards = [
        ("已记录日报天数", str(len(reports))),
        ("最近一次更新时间", generated_at),
        ("本月记录数量", str(month_count)),
        ("最近一篇周报", latest_weekly_text),
    ]
    return "\n".join(
        f'<article class="stat-card"><span>{escape(label)}</span><strong>{escape(value)}</strong></article>'
        for label, value in cards
    )


def build_nav(active: str) -> str:
    links = [
        ("index.html", "今日汇报", "index"),
        ("archive.html", "日报归档", "archive"),
        ("weekly.html", "周报", "weekly"),
        ("papers.html", "论文笔记", "papers"),
        ("milestones.html", "阶段性里程碑", "milestones"),
        ("feedback.html", "留言点评", "feedback"),
    ]
    items = "\n".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>'
        for href, label, key in links
    )
    return f'<nav class="site-nav" aria-label="页面导航">{items}</nav>'


def build_page(
    *,
    title: str,
    subtitle: str,
    active: str,
    generated_at: str,
    content: str,
    extra_header: str = "",
) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} | {escape(PROJECT_NAME)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #eef2f6;
      --panel: #ffffff;
      --text: #1f2937;
      --muted: #64748b;
      --border: #d8dee8;
      --accent: #0f766e;
      --accent-dark: #115e59;
      --accent-soft: #e6f4f1;
      --code-bg: #f6f8fa;
      --shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "Microsoft YaHei", sans-serif;
      line-height: 1.7;
    }}

    .page {{
      width: min(100% - 32px, 900px);
      margin: 0 auto;
      padding: 34px 0 28px;
    }}

    .hero,
    .card,
    .stat-card {{
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }}

    .hero {{
      margin-bottom: 16px;
      padding: 26px 30px;
    }}

    .eyebrow {{
      margin: 0 0 8px;
      color: var(--accent);
      font-size: 0.92rem;
      font-weight: 700;
    }}

    h1 {{
      margin: 0;
      color: #0f172a;
      font-size: clamp(1.85rem, 3vw, 2.48rem);
      line-height: 1.25;
    }}

    .subtitle {{
      margin: 10px 0 0;
      color: var(--muted);
    }}

    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px 18px;
      margin-top: 16px;
      color: var(--muted);
      font-size: 0.95rem;
    }}

    .site-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 0 0 16px;
    }}

    .site-nav a {{
      padding: 7px 11px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--panel);
      color: #334155;
      text-decoration: none;
      font-size: 0.94rem;
      font-weight: 650;
    }}

    .site-nav a.active,
    .site-nav a:hover {{
      border-color: var(--accent);
      background: var(--accent-soft);
      color: var(--accent-dark);
    }}

    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }}

    .stat-card {{
      min-height: 96px;
      padding: 16px;
    }}

    .stat-card span {{
      display: block;
      color: var(--muted);
      font-size: 0.9rem;
    }}

    .stat-card strong {{
      display: block;
      margin-top: 8px;
      color: #0f172a;
      font-size: 1.18rem;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }}

    .card {{
      padding: 30px;
    }}

    .notice {{
      margin: 0 0 18px;
      padding: 12px 14px;
      border: 1px solid #b7d8d2;
      border-radius: 8px;
      background: var(--accent-soft);
      color: #164e49;
      font-weight: 650;
    }}

    .quick-links {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin: 0 0 22px;
    }}

    .quick-links a {{
      display: block;
      padding: 13px 14px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fbfdff;
      color: #0f766e;
      text-decoration: none;
      font-weight: 700;
    }}

    .quick-links a:hover {{
      border-color: var(--accent);
      background: var(--accent-soft);
    }}

    .link-panel {{
      margin: 0 0 18px;
      padding: 14px 16px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fbfdff;
      color: var(--muted);
    }}

    .link-panel strong {{
      display: block;
      color: #0f172a;
      margin-bottom: 4px;
    }}

    .action-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 16px 0 22px;
    }}

    .action-row a {{
      display: inline-block;
      padding: 9px 13px;
      border: 1px solid var(--accent);
      border-radius: 8px;
      background: var(--accent-soft);
      color: var(--accent-dark);
      text-decoration: none;
      font-weight: 700;
    }}

    .report-content > :first-child,
    .content-body > :first-child,
    .empty-state > :first-child,
    .section > :first-child {{
      margin-top: 0;
    }}

    h2 {{
      margin-top: 1.7em;
      margin-bottom: 0.65em;
      color: #111827;
      font-size: 1.32rem;
      line-height: 1.35;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.28em;
    }}

    h3 {{
      margin-top: 1.4em;
      color: #1f2937;
    }}

    p {{
      margin: 0.85em 0;
    }}

    ul,
    ol {{
      padding-left: 1.35em;
    }}

    li + li {{
      margin-top: 0.28em;
    }}

    a {{
      color: var(--accent);
      text-decoration: none;
      font-weight: 650;
    }}

    a:hover {{
      text-decoration: underline;
    }}

    code {{
      padding: 0.14em 0.34em;
      border-radius: 5px;
      background: var(--code-bg);
      color: #0f172a;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      font-size: 0.92em;
    }}

    pre {{
      overflow-x: auto;
      padding: 16px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--code-bg);
    }}

    pre code {{
      padding: 0;
      background: transparent;
    }}

    blockquote {{
      margin: 1.2em 0;
      padding: 0.5em 1em;
      border-left: 4px solid var(--accent);
      background: var(--accent-soft);
      color: #334155;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1.2em 0;
      font-size: 0.96rem;
    }}

    th,
    td {{
      border: 1px solid var(--border);
      padding: 10px 12px;
      text-align: left;
      vertical-align: top;
    }}

    th {{
      background: #f8fafc;
      color: #0f172a;
    }}

    .empty-state {{
      padding: 20px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fbfdff;
    }}

    .empty-state h2 {{
      border-bottom: 0;
      padding-bottom: 0;
    }}

    .section {{
      margin-top: 26px;
    }}

    .entry-list {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}

    .entry-list li {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      padding: 12px 0;
      border-bottom: 1px solid var(--border);
    }}

    .entry-list time,
    .empty-note {{
      color: var(--muted);
    }}

    footer {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.92rem;
      text-align: center;
    }}

    @media (max-width: 780px) {{
      .stats-grid,
      .quick-links {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 640px) {{
      .page {{
        width: min(100% - 20px, 900px);
        padding-top: 18px;
      }}

      .hero,
      .card {{
        padding: 20px;
      }}

      .stats-grid,
      .quick-links {{
        grid-template-columns: 1fr;
      }}

      .entry-list li {{
        display: block;
      }}

      .entry-list time {{
        display: block;
        margin-top: 4px;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    {build_nav(active)}
    <header class="hero">
      <p class="eyebrow">{escape(PROJECT_NAME)}</p>
      <h1>{escape(title)}</h1>
      <p class="subtitle">{escape(subtitle)}</p>
      <div class="meta">
        <span>自动生成时间：{escape(generated_at)}</span>
        <span>时区：{escape(TIMEZONE)}</span>
      </div>
    </header>
    {extra_header}
    <section class="card">
      {content}
    </section>
    <footer>
      <div>Generated by automation workflow</div>
      <div>Last updated: {escape(generated_at)}</div>
    </footer>
  </main>
</body>
</html>
"""


def build_index_page(
    root: Path,
    today: str,
    generated_at: str,
    reports: list[dict[str, str]],
    weekly_reports: list[dict[str, str]],
) -> str:
    today_path = root / REPORTS_DIR / f"{today}.md"
    today_text = load_markdown(today_path)
    notice = ""
    display_title = f"{today} 工作汇报"

    if today_text:
        report_html = render_markdown(today_text)
    else:
        latest_report = get_latest_entry(reports)
        if latest_report:
            latest_path = Path(latest_report["path"])
            latest_text = load_markdown(latest_path) or ""
            report_html = render_markdown(latest_text)
            display_title = latest_report["title"]
            notice = '<div class="notice">今日暂无记录，当前展示最近一次工作记录。</div>'
        else:
            report_html = """
            <section class="empty-state">
              <h2>今日暂无工作记录</h2>
              <p>当前没有找到任何日报。请在 <code>reports/</code> 下新增 <code>YYYY-MM-DD.md</code> 后重新运行生成脚本。</p>
            </section>
            """

    quick_links = """
    <div class="quick-links" aria-label="快捷入口">
      <a href="archive.html">日报归档</a>
      <a href="weekly.html">最近周报</a>
      <a href="papers.html">论文阅读笔记</a>
      <a href="milestones.html">阶段性里程碑</a>
      <a href="feedback.html">留言点评</a>
    </div>
    """
    site_link = f"""
    <section class="link-panel">
      <strong>在线访问地址</strong>
      <a href="{escape(SITE_URL)}">{escape(SITE_URL)}</a>
    </section>
    """
    stats = f'<section class="stats-grid">{build_stat_cards(reports, weekly_reports, generated_at, today)}</section>'
    recent = f"""
    <section class="section">
      <h2>最近工作记录</h2>
      {build_report_list(reports[:RECENT_REPORT_LIMIT], "reports 目录下还没有可展示的历史记录。")}
    </section>
    """
    content = f'{site_link}{quick_links}{notice}<article class="report-content">{report_html}</article>{recent}'

    return build_page(
        title=display_title,
        subtitle=f"今日日期：{today}",
        active="index",
        generated_at=generated_at,
        extra_header=stats,
        content=content,
    )


def build_archive_page(reports: list[dict[str, str]], generated_at: str) -> str:
    content = f"""
    <section class="content-body">
      <h2>全部日报</h2>
      {build_report_list(reports, "reports 目录下还没有日报记录。")}
    </section>
    """
    return build_page(
        title="日报归档",
        subtitle="按时间倒序汇总全部 Markdown 日报。",
        active="archive",
        generated_at=generated_at,
        content=content,
    )


def build_latest_markdown_page(
    *,
    title: str,
    subtitle: str,
    active: str,
    generated_at: str,
    entries: list[dict[str, str]],
    empty_text: str,
    list_heading: str,
) -> str:
    latest = get_latest_entry(entries)
    if latest:
        latest_text = load_markdown(Path(latest["path"])) or ""
        latest_html = render_markdown(latest_text)
        main = f'<article class="report-content">{latest_html}</article>'
    else:
        main = f"""
        <section class="empty-state">
          <h2>暂无内容</h2>
          <p>{escape(empty_text)}</p>
        </section>
        """

    content = f"""
    {main}
    <section class="section">
      <h2>{escape(list_heading)}</h2>
      {build_report_list(entries, empty_text)}
    </section>
    """
    return build_page(
        title=title,
        subtitle=subtitle,
        active=active,
        generated_at=generated_at,
        content=content,
    )


def build_milestones_page(root: Path, generated_at: str) -> str:
    milestones_path = root / MILESTONES_FILE
    text = load_markdown(milestones_path)
    if text:
        content = f'<article class="content-body">{render_markdown(text)}</article>'
    else:
        content = """
        <section class="empty-state">
          <h2>暂无阶段性里程碑</h2>
          <p>当前没有找到 <code>milestones.md</code>。新增该文件后，页面会自动展示阶段性进展、成果和关键节点。</p>
        </section>
        """
    return build_page(
        title="阶段性里程碑",
        subtitle="记录实习期间的重要节点、阶段成果和可复盘事项。",
        active="milestones",
        generated_at=generated_at,
        content=content,
    )


def build_feedback_page(root: Path, generated_at: str) -> str:
    feedback_path = root / FEEDBACK_FILE
    text = load_markdown(feedback_path)
    if text:
        log_html = render_markdown(text)
    else:
        log_html = """
        <section class="empty-state">
          <h2>暂无留言点评记录</h2>
          <p>当前还没有归档的留言或点评。可以通过下方入口提交反馈，自动化流程会将反馈记录到案。</p>
        </section>
        """

    content = f"""
    <section class="content-body">
      <h2>留言与点评入口</h2>
      <p>本页面用于收集查看者对工作记录的意见、问题和阶段性建议。提交后，自动化流程会整理为 Markdown 留痕文件。</p>
      <div class="action-row">
        <a href="{escape(NEW_FEEDBACK_URL)}">提交新的留言点评</a>
        <a href="{escape(FEEDBACK_ISSUES_URL)}">查看原始留言区</a>
      </div>
      <h2>归档记录</h2>
      {log_html}
    </section>
    """
    return build_page(
        title="留言点评",
        subtitle="收集查看者反馈，并自动归档为可追溯记录。",
        active="feedback",
        generated_at=generated_at,
        content=content,
    )


def write_page(root: Path, filename: str, html: str) -> None:
    output_path = root / filename
    output_path.write_text(html, encoding="utf-8")
    print(f"成功生成 {output_path}")


def main() -> int:
    try:
        root = get_project_root()
        now = get_now()
        today = get_today(now)
        generated_at = now.strftime("%Y-%m-%d %H:%M:%S %Z")

        reports = list_markdown_entries(root / REPORTS_DIR, REPORTS_DIR)
        weekly_reports = list_markdown_entries(root / WEEKLY_DIR, WEEKLY_DIR)
        paper_notes = list_markdown_entries(root / PAPER_NOTES_DIR, PAPER_NOTES_DIR)

        pages = {
            "index.html": build_index_page(root, today, generated_at, reports, weekly_reports),
            "archive.html": build_archive_page(reports, generated_at),
            "weekly.html": build_latest_markdown_page(
                title="最近周报",
                subtitle="展示最近一篇周报，并保留历史周报入口。",
                active="weekly",
                generated_at=generated_at,
                entries=weekly_reports,
                empty_text="weekly 目录下还没有周报。可以新增 weekly/YYYY-WW.md 或 weekly/YYYY-MM-DD.md。",
                list_heading="历史周报",
            ),
            "papers.html": build_latest_markdown_page(
                title="论文阅读笔记",
                subtitle="汇总实习期间的论文阅读记录、方法理解和问题整理。",
                active="papers",
                generated_at=generated_at,
                entries=paper_notes,
                empty_text="paper-notes 目录下还没有论文阅读笔记。可以新增 paper-notes/论文名或日期.md。",
                list_heading="全部论文笔记",
            ),
            "milestones.html": build_milestones_page(root, generated_at),
            "feedback.html": build_feedback_page(root, generated_at),
        }

        for filename, html in pages.items():
            write_page(root, filename, html)
        return 0
    except Exception as exc:
        print(f"生成静态页面失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
