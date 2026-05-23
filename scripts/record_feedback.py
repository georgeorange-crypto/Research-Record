from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


LABEL = "page-feedback"
OUTPUT_PATH = Path("feedback") / "feedback-log.md"
TIMEZONE = "Asia/Shanghai"


def request_json(url: str, token: str) -> object:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "record-feedback",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_all(url: str, token: str) -> list[dict]:
    results: list[dict] = []
    page = 1
    while True:
        separator = "&" if "?" in url else "?"
        page_url = f"{url}{separator}per_page=100&page={page}"
        data = request_json(page_url, token)
        if not isinstance(data, list) or not data:
            return results
        results.extend(data)
        page += 1


def clean_body(text: str | None) -> str:
    if not text:
        return "_未填写正文_"
    return text.strip()


def blockquote(text: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())


def format_time(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return value


def build_log(repository: str, token: str) -> str:
    encoded_label = urllib.parse.quote(LABEL)
    issues_url = f"https://api.github.com/repos/{repository}/issues?state=all&labels={encoded_label}&sort=updated&direction=desc"
    issues = [item for item in fetch_all(issues_url, token) if "pull_request" not in item]

    now = datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 留言点评归档",
        "",
        f"> 自动生成时间：{now}（{TIMEZONE}）",
        "",
    ]

    if not issues:
        lines.extend(["暂无留言点评记录。", ""])
        return "\n".join(lines)

    for issue in issues:
        number = issue["number"]
        title = issue.get("title") or f"Feedback #{number}"
        author = issue.get("user", {}).get("login", "unknown")
        created_at = format_time(issue.get("created_at", ""))
        updated_at = format_time(issue.get("updated_at", ""))
        state = issue.get("state", "")
        html_url = issue.get("html_url", "")

        lines.extend(
            [
                f"## #{number} {title}",
                "",
                f"- 提交人：{author}",
                f"- 状态：{state}",
                f"- 创建时间：{created_at}",
                f"- 最近更新：{updated_at}",
                f"- 原始链接：{html_url}",
                "",
                "### 原始留言",
                "",
                blockquote(clean_body(issue.get("body"))),
                "",
            ]
        )

        comments_url = issue.get("comments_url")
        comments = fetch_all(comments_url, token) if comments_url else []
        if comments:
            lines.extend(["### 后续回复", ""])
            for comment in comments:
                commenter = comment.get("user", {}).get("login", "unknown")
                comment_time = format_time(comment.get("created_at", ""))
                lines.extend(
                    [
                        f"#### {commenter} / {comment_time}",
                        "",
                        blockquote(clean_body(comment.get("body"))),
                        "",
                    ]
                )

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    try:
        repository = os.environ["GITHUB_REPOSITORY"]
        token = os.environ["GITHUB_TOKEN"]
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(build_log(repository, token), encoding="utf-8")
        print(f"已更新 {OUTPUT_PATH}")
        return 0
    except Exception as exc:
        print(f"生成留言点评归档失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
