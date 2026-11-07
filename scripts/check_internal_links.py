#!/usr/bin/env python3
"""检查 Markdown 内部链接和标题锚点。

脚本只读本地文件，不请求外部网址。
结果通过，只说明仓库内部链接和锚点可用。
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
import urllib.parse
from pathlib import Path

PUNCTUATION = re.compile(r"[\u2000-\u206F\u2E00-\u2E7F\\'\"!#$%&()*+,./:;<=>?@\[\]^`{|}~]")
HEADING = re.compile(r"^(#{1,6})\s+(\S.*)$")
REF_DEF = re.compile(r"^\[([^\]]+)\]:\s+(\S+)", re.MULTILINE)
HTML_HREF = re.compile(
    r"<a\s[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
HTML_ID = re.compile(r"\sid=[\"']([^\"']+)[\"']", re.IGNORECASE)
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
GENERIC_TEXT = {
    "这里",
    "点这里",
    "点击这里",
    "此链接",
    "链接",
    "详情",
    "更多",
    "here",
    "click here",
    "link",
    "read more",
}


def strip_ignored(text: str) -> str:
    text = COMMENT.sub("", text)
    parts = text.split("```")
    kept: list[str] = []
    for index, part in enumerate(parts):
        if index % 2 == 0:
            kept.append(part)
        else:
            kept.append("\n")
    return "".join(kept)


def slugify(text: str) -> str:
    text = text.replace("**", "").replace("__", "")
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = text.replace("*", "").replace("_", "")
    text = PUNCTUATION.sub("", text)
    text = text.lower().strip()
    text = re.sub(r"\s+", "-", text)
    return text


def heading_slugs(text: str) -> set[str]:
    occurrences: dict[str, int] = {}
    found: set[str] = set()
    for match in HTML_ID.finditer(text):
        found.add(match.group(1).strip().lower())
    for line in text.splitlines():
        mark = HEADING.match(line.strip())
        if not mark:
            continue
        base = slugify(mark.group(2).strip())
        if not base:
            continue
        slug = base
        original = slug
        while slug in occurrences:
            occurrences[original] = occurrences.get(original, 0) + 1
            slug = f"{original}-{occurrences[original]}"
        occurrences[slug] = 0
        found.add(slug)
    return found


def inline_links(text: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    index = 0
    length = len(text)
    while index < length:
        if text[index] != "[":
            index += 1
            continue
        depth = 1
        cursor = index + 1
        while cursor < length and depth:
            if text[cursor] == "[":
                depth += 1
            elif text[cursor] == "]":
                depth -= 1
            if depth:
                cursor += 1
        if cursor >= length or text[cursor] != "]":
            index += 1
            continue
        label = text[index + 1 : cursor].strip()
        if cursor + 1 < length and text[cursor + 1] == "(":
            end = cursor + 2
            depth = 1
            while end < length and depth:
                if text[end] == "(":
                    depth += 1
                elif text[end] == ")":
                    depth -= 1
                if depth:
                    end += 1
            if end < length and text[end] == ")":
                target = text[cursor + 2 : end].strip().split()[0] if text[cursor + 2 : end].strip() else ""
                links.append((label, target))
                index = end + 1
                continue
        if cursor + 1 < length and text[cursor + 1] == "[":
            end = text.find("]", cursor + 2)
            if end != -1:
                ref = text[cursor + 2 : end].strip() or label
                links.append((label, f"ref:{ref}"))
                index = end + 1
                continue
        index = cursor + 1
    for match in HTML_HREF.finditer(text):
        label = re.sub(r"<[^>]+>", "", match.group(2))
        label = re.sub(r"\s+", " ", label).strip()
        links.append((label, match.group(1).strip()))
    return links


def resolve_refs(text: str, links: list[tuple[str, str]]) -> list[tuple[str, str]]:
    refs = {name.strip().lower(): target for name, target in REF_DEF.findall(text)}
    resolved: list[tuple[str, str]] = []
    for label, target in links:
        if target.startswith("ref:"):
            key = target[4:].strip().lower()
            if key not in refs:
                resolved.append((label, f"missing-ref:{key}"))
            else:
                resolved.append((label, refs[key]))
        else:
            resolved.append((label, target))
    return resolved


def is_external(target: str) -> bool:
    lowered = target.lower()
    return lowered.startswith(("http://", "https://", "mailto:", "tel:"))


def check_tree(root: Path) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    external: list[str] = []
    files = sorted(path for path in root.rglob("*.md") if ".git" not in path.parts)
    for path in files:
        original = path.read_text(encoding="utf-8")
        visible = strip_ignored(original)
        own_slugs = heading_slugs(visible)
        links = resolve_refs(visible, inline_links(visible))
        for label, target in links:
            location = path.relative_to(root).as_posix()
            if not target or target.startswith("missing-ref:"):
                failures.append(f"失败 {location}：「{label or '空链接文字'}」没有可用的目标。")
                continue
            normalized = re.sub(r"\s+", " ", label).strip().lower()
            if not label.strip():
                failures.append(f"失败 {location}：有一条空链接文字，目标是 {target}。")
                continue
            if normalized in GENERIC_TEXT:
                failures.append(
                    f"失败 {location}：链接文字「{label}」没有说明去向。请写成能单独听懂的文字。"
                )
            if is_external(target):
                external.append(target)
                continue
            parsed = urllib.parse.urlparse(target)
            if parsed.scheme:
                failures.append(f"失败 {location}：「{label}」使用了不支持的地址 {target}。")
                continue
            if target.startswith("/"):
                failures.append(
                    f"失败 {location}：「{label}」使用了以斜杠开头的路径 {target}。请改成相对路径。"
                )
                continue
            fragment = urllib.parse.unquote(parsed.fragment).strip().lower()
            file_part = urllib.parse.unquote(parsed.path)
            if not file_part:
                destination = path
                slugs = own_slugs
            else:
                destination = (path.parent / file_part).resolve()
                try:
                    destination.relative_to(root.resolve())
                except ValueError:
                    failures.append(f"失败 {location}：「{label}」指向仓库外的 {target}。")
                    continue
                if not destination.is_file():
                    failures.append(f"失败 {location}：「{label}」指向不存在的文件 {target}。")
                    continue
                if destination.suffix.lower() == ".md":
                    slugs = heading_slugs(strip_ignored(destination.read_text(encoding="utf-8")))
                else:
                    slugs = set()
            if fragment and destination.suffix.lower() == ".md" and fragment not in slugs:
                failures.append(
                    f"失败 {location}：「{label}」的锚点 #{fragment} 在目标页面不存在。"
                )
    return failures, external


def run_self_test() -> list[str]:
    problems: list[str] = []
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        docs = root / "docs"
        docs.mkdir()
        (docs / "好的页面.md").write_text(
            "\n".join(
                [
                    "# 好的页面",
                    "",
                    "## 第一节",
                    "",
                    "参见 [第一节](#第一节)。",
                    "",
                    "```",
                    "[坏链接](不存在.md)",
                    "```",
                    "",
                    "外部说明见 [OpenAI 帮助页示例](https://example.com/help)。",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / "README.md").write_text(
            "\n".join(
                [
                    "# 首页",
                    "",
                    "阅读 [好的页面](docs/好的页面.md)。",
                    "",
                    "跳到 [第一节](docs/好的页面.md#第一节)。",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        failures, external = check_tree(root)
        if failures:
            problems.append("自测预期通过，但出现失败：" + " ".join(failures))
        if external != ["https://example.com/help"]:
            problems.append(f"自测外部链接记录不符：{external}")

        (root / "README.md").write_text(
            "\n".join(
                [
                    "# 首页",
                    "",
                    "阅读 [好的页面](docs/好的页面.md)。",
                    "",
                    "这是 [点击这里](docs/好的页面.md)。",
                    "",
                    "缺文件 [维护规范](docs/没有.md)。",
                    "",
                    "缺锚点 [不存在的节](docs/好的页面.md#没有这节)。",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        failures, _external = check_tree(root)
        joined = "\n".join(failures)
        for expected in ("点击这里", "不存在的文件", "锚点"):
            if expected not in joined:
                problems.append(f"自测没有检出：{expected}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 Markdown 内部链接和锚点")
    parser.add_argument("--self-test", action="store_true", help="运行内置样例")
    parser.add_argument("--root", default=".", help="仓库根目录")
    parser.add_argument("--list-external", action="store_true", help="列出外部链接，仍然不请求它们")
    args = parser.parse_args()
    if args.self_test:
        problems = run_self_test()
        if problems:
            print("自测失败")
            for problem in problems:
                print(problem)
            return 1
        print("自测通过：存在的内部链接和锚点被接受，坏链接、空泛链接文字和代码块中的假链接按预期处理。")
        return 0

    root = Path(args.root).resolve()
    failures, external = check_tree(root)
    if failures:
        print(f"失败：发现 {len(failures)} 个内部链接问题。")
        for failure in failures:
            print(failure)
        print(f"外部链接 {len(external)} 条。脚本没有请求它们，因此这次结果不能用来声称外链正文有效。")
        return 1
    print(f"通过：内部链接和锚点可用。外部链接 {len(external)} 条，脚本没有请求它们。")
    if args.list_external:
        for url in sorted(set(external)):
            print(f"外部 {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
