#!/usr/bin/env python3
"""Generate and validate the reverse-engineering knowledge-base catalog.

The script has no third-party dependencies and is intentionally repository-local.
It keeps the human-curated INDEX.md separate from a generated per-article catalog.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import unquote


GENERATED_MARKDOWN = "CATALOG.md"
GENERATED_JSON = "catalog.json"
ROOT_MARKDOWN = {"AGENTS.md", "INDEX.md", "README.md", GENERATED_MARKDOWN}
EXCLUDED_DIRS = {".git", "__pycache__", "pending", "scripts", "tests"}
LOCAL_LINK_SUFFIXES = {".gif", ".jpeg", ".jpg", ".json", ".md", ".pdf", ".png", ".svg", ".txt"}

TAIL_MARKER_PREFIXES = (
    "下边是广告环节",
    "下面是广告环节",
    "广告环节",
    "研究交流群",
    "以上，每周一篇论文研读",
    "每期论文英文原文发群里",
    "接下来课程会调试分析webkit",
    "小肩膀教育安全逆向教学",
    "小肩膀自营AI Token服务",
    "加入小肩膀",
    "从零开始的浏览器内核教程",
    "国内最早和系统完整的浏览器内核培训教程",
    "如意本人联系方式",
    "关注该公众号",
    "星球主要发高质量文章",
    "立足AI时代，持续输出可直接落地",
    "包纯度（假一赔十）",
)

METADATA_ALIASES = {
    "source": {"source", "来源", "来源项目"},
    "original_date": {"original date", "原始日期", "原始发布时间", "原文日期", "分析日期", "初始分析"},
    "archive_date": {"archive date", "归档日期"},
    "category": {"category", "分类"},
}

CATEGORY_METADATA_ALIASES = {
    "anti-detection": {"anti-detection", "反检测", "反检测/风控对抗"},
    "mobile-app-reverse": {"mobile-app-reverse", "移动 App 逆向"},
    "native-analysis": {"native-analysis", "Native 分析", "Native SO 分析"},
    "packing-bypass": {"packing-bypass", "加固绕过", "加固/混淆绕过"},
    "protocols": {"protocols", "协议", "协议分析"},
    "signature-algorithms": {"signature-algorithms", "签名算法"},
    "web-reverse": {"web-reverse", "Web 逆向"},
}


@dataclass(frozen=True)
class LoadedText:
    path: Path
    text: str
    bom: bool
    newline: str
    final_newline: bool


def load_text(path: Path) -> LoadedText:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = text.count("\r\n")
    bare_lf = text.count("\n") - crlf
    newline = "\r\n" if crlf > bare_lf else "\n"
    return LoadedText(path=path, text=text, bom=bom, newline=newline, final_newline=text.endswith(("\n", "\r")))


def write_preserving(source: LoadedText, text: str) -> None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.rstrip("\n")
    if source.final_newline:
        normalized += "\n"
    if source.newline == "\r\n":
        normalized = normalized.replace("\n", "\r\n")
    payload = normalized.encode("utf-8")
    if source.bom:
        payload = b"\xef\xbb\xbf" + payload
    source.path.write_bytes(payload)


def write_generated(path: Path, text: str) -> None:
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8", newline="\n")


def iter_article_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*.md"):
        rel = path.relative_to(root)
        if len(rel.parts) == 1 and path.name in ROOT_MARKDOWN:
            continue
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        paths.append(path)
    return sorted(paths, key=lambda item: item.relative_to(root).as_posix())


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def strip_inline_markdown(value: str) -> str:
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("`", "").replace("**", "").replace("__", "")
    return normalize_space(value)


def extract_title(text: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return strip_inline_markdown(match.group(1))
    return ""


def extract_headings(text: str) -> list[str]:
    headings: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^#{2,3}\s+(.+?)\s*$", line)
        if match:
            headings.append(strip_inline_markdown(match.group(1)))
    return headings


def metadata_key(raw_key: str) -> str | None:
    key = normalize_space(raw_key).lower()
    for canonical, aliases in METADATA_ALIASES.items():
        if key in aliases:
            return canonical
    return None


def parse_metadata(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in text.splitlines()[:40]:
        if not line.startswith(">"):
            continue
        content = line[1:].strip()
        match = re.match(r"^([^:：]{1,24})[:：]\s*(.+?)\s*$", content)
        if not match:
            continue
        key = metadata_key(match.group(1))
        if key and key not in metadata:
            metadata[key] = normalize_space(match.group(2))
    return metadata


def category_metadata_matches(value: str, directory: str) -> bool:
    prefix = re.split(r"\s+[—–-]\s+", normalize_space(value), maxsplit=1)[0]
    accepted = CATEGORY_METADATA_ALIASES.get(directory, {directory})
    return prefix.casefold() in {item.casefold() for item in accepted}


def extract_summary(text: str) -> str:
    lines = text.splitlines()
    in_fence = False
    paragraph: list[str] = []
    for line in lines[1:]:
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not stripped:
            if paragraph:
                candidate = strip_inline_markdown(" ".join(paragraph))
                if len(candidate) >= 24:
                    return candidate[:320]
                paragraph = []
            continue
        if stripped.startswith("#") or stripped.startswith("|") or re.match(r"^[-*+]\s+", stripped):
            if paragraph:
                candidate = strip_inline_markdown(" ".join(paragraph))
                if len(candidate) >= 24:
                    return candidate[:320]
                paragraph = []
            continue
        if stripped.startswith(">"):
            content = stripped[1:].strip()
            if re.match(r"^[^:：]{1,24}[:：]", content):
                continue
            paragraph.append(content)
        else:
            paragraph.append(stripped)
    if paragraph:
        return strip_inline_markdown(" ".join(paragraph))[:320]
    return ""


def date_from_filename(path: Path) -> str:
    match = re.search(r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)", path.stem)
    if not match:
        return ""
    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"


def parse_index(root: Path) -> tuple[set[str], dict[str, dict[str, object]]]:
    text = load_text(root / "INDEX.md").text
    links: set[str] = set()
    for target in re.findall(r"\[[^\]]+\]\((\./[^)]+\.md(?:#[^)]+)?)\)", text):
        normalized = target[2:].split("#", 1)[0].replace("\\", "/")
        if normalized in ROOT_MARKDOWN:
            continue
        links.add(normalized)
    details: dict[str, dict[str, object]] = {}
    row_pattern = re.compile(
        r"^\|\s*\[[^\]]+\]\((\./[^)]+\.md)\)\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*(.*?)\|\s*$",
        re.MULTILINE,
    )
    for match in row_pattern.finditer(text):
        path = match.group(1)[2:].replace("\\", "/")
        details[path] = {
            "source_project": normalize_space(match.group(2)),
            "keywords": re.findall(r"`([^`]+)`", match.group(3)),
            "index_summary": normalize_space(match.group(4)),
        }
    return links, details


def parent_path(root: Path, rel: Path) -> str | None:
    if len(rel.parts) <= 2:
        return None
    candidate = Path(rel.parts[0]) / f"{rel.parts[1]}.md"
    return candidate.as_posix() if (root / candidate).is_file() else None


def build_records(root: Path) -> list[dict[str, object]]:
    _, index_details = parse_index(root)
    records: list[dict[str, object]] = []
    for path in iter_article_paths(root):
        loaded = load_text(path)
        rel = path.relative_to(root)
        rel_posix = rel.as_posix()
        metadata = parse_metadata(loaded.text)
        original_date = metadata.get("original_date", "") or date_from_filename(path)
        index_entry = index_details.get(rel_posix, {})
        source = metadata.get("source", "") or str(index_entry.get("source_project", ""))
        kind = "canonical" if len(rel.parts) == 2 else "nested"
        record = {
            "path": rel_posix,
            "kind": kind,
            "category": rel.parts[0],
            "parent": parent_path(root, rel),
            "title": extract_title(loaded.text),
            "source": source,
            "original_date": original_date,
            "archive_date": metadata.get("archive_date", ""),
            "summary": extract_summary(loaded.text) or str(index_entry.get("index_summary", "")),
            "keywords": list(index_entry.get("keywords", [])),
            "headings": extract_headings(loaded.text),
            "bytes": len(path.read_bytes()),
            "lines": len(loaded.text.splitlines()),
            "content_sha256": hashlib.sha256(loaded.text.encode("utf-8")).hexdigest(),
        }
        records.append(record)
    return records


def markdown_escape(value: object) -> str:
    return normalize_space(str(value)).replace("|", "\\|")


def render_catalog_markdown(records: Sequence[dict[str, object]]) -> str:
    category_stats: dict[str, Counter[str]] = defaultdict(Counter)
    title_by_path = {str(item["path"]): str(item["title"]) for item in records}
    for record in records:
        category_stats[str(record["category"])][str(record["kind"])] += 1

    lines = [
        "# 逆向知识库详细目录",
        "",
        "> 由 `scripts/kb_catalog.py` 根据文章内容生成，请勿手工编辑。",
        ">",
        "> canonical 导航与技术标签仍以 [INDEX.md](./INDEX.md) 为准；本文件用于逐篇检索合集子文章。",
        "",
        "## 统计",
        "",
        "| 分类 | canonical | 子文章 | 合计 |",
        "|------|----------:|-------:|-----:|",
    ]
    for category in sorted(category_stats):
        stats = category_stats[category]
        total = stats["canonical"] + stats["nested"]
        lines.append(f"| `{category}` | {stats['canonical']} | {stats['nested']} | {total} |")
    lines.extend(["", f"文章总数：{len(records)}。", "", "## 逐篇目录", ""])

    for category in sorted(category_stats):
        lines.extend(
            [
                f"### `{category}`",
                "",
                "| 类型 | 日期 | 文章 | 父合集 | 关键标题 |",
                "|------|------|------|--------|----------|",
            ]
        )
        category_records = [record for record in records if record["category"] == category]
        category_records.sort(key=lambda item: (0 if item["kind"] == "canonical" else 1, str(item["path"])))
        for record in category_records:
            path = str(record["path"])
            title = markdown_escape(record["title"] or Path(path).name)
            kind = "主文" if record["kind"] == "canonical" else "子文"
            date = markdown_escape(record["original_date"] or record["archive_date"] or "—")
            parent = record["parent"]
            if parent:
                parent_title = markdown_escape(title_by_path.get(str(parent), str(parent)))
                parent_cell = f"[{parent_title}](./{parent})"
            else:
                parent_cell = "—"
            headings = record.get("headings", [])
            heading_cell = " / ".join(markdown_escape(item) for item in list(headings)[:4]) or "—"
            lines.append(f"| {kind} | {date} | [{title}](./{path}) | {parent_cell} | {heading_cell} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_catalog_json(records: Sequence[dict[str, object]]) -> str:
    category_counts = Counter(str(record["category"]) for record in records)
    payload = {
        "schema_version": 1,
        "article_count": len(records),
        "category_counts": dict(sorted(category_counts.items())),
        "records": list(records),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def expected_generated(root: Path) -> tuple[str, str, list[dict[str, object]]]:
    records = build_records(root)
    return render_catalog_markdown(records), render_catalog_json(records), records


def generate(root: Path) -> dict[str, object]:
    markdown, payload, records = expected_generated(root)
    write_generated(root / GENERATED_MARKDOWN, markdown)
    write_generated(root / GENERATED_JSON, payload)
    return {
        "article_count": len(records),
        "catalog_markdown": str(root / GENERATED_MARKDOWN),
        "catalog_json": str(root / GENERATED_JSON),
    }


def marker_name(line: str) -> str | None:
    candidate = line.strip().lstrip(">*- ").replace("**", "").strip()
    for marker in TAIL_MARKER_PREFIXES:
        if candidate.startswith(marker):
            return marker
    return None


def find_tail_marker(text: str) -> tuple[int, str] | None:
    in_fence = False
    for index, line in enumerate(text.splitlines()):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        marker = marker_name(line)
        if marker:
            return index, marker
    return None


def decorative_line(line: str) -> bool:
    stripped = line.strip()
    return not stripped or bool(re.fullmatch(r"[*_~`\-\s]+", stripped))


def sanitize(root: Path, apply: bool) -> dict[str, object]:
    changes: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    for path in iter_article_paths(root):
        loaded = load_text(path)
        marker = find_tail_marker(loaded.text)
        if marker is None:
            continue
        index, name = marker
        lines = loaded.text.splitlines()
        kept = lines[:index]
        while kept and decorative_line(kept[-1]):
            kept.pop()
        meaningful = [line for line in kept if line.strip() and not line.lstrip().startswith(">")]
        if len(meaningful) < 3 or not any(line.startswith("# ") for line in kept):
            skipped.append({"path": path.relative_to(root).as_posix(), "line": index + 1, "marker": name})
            continue
        cleaned = "\n".join(kept)
        if apply:
            write_preserving(loaded, cleaned)
        changes.append(
            {
                "path": path.relative_to(root).as_posix(),
                "line": index + 1,
                "marker": name,
                "removed_lines": len(lines) - len(kept),
            }
        )
    return {"apply": apply, "changed_count": len(changes), "skipped_count": len(skipped), "changes": changes, "skipped": skipped}


def markdown_links(text: str) -> Iterable[str]:
    in_fence = False
    inline_code = re.compile(r"`[^`]*`")
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        cleaned = inline_code.sub("", line)
        yield from re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", cleaned)
        yield from re.findall(r"!\[[^\]]*\]\(([^)]+)\)", cleaned)


def audit(root: Path, check_generated: bool = True) -> dict[str, object]:
    markdown, payload, records = expected_generated(root)
    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    record_by_path = {str(record["path"]): record for record in records}
    canonical = {path for path, record in record_by_path.items() if record["kind"] == "canonical"}
    nested = {path for path, record in record_by_path.items() if record["kind"] == "nested"}
    index_links, _ = parse_index(root)

    for path in sorted(canonical - index_links):
        errors.append({"code": "canonical_not_indexed", "path": path})
    for path in sorted(index_links - set(record_by_path)):
        errors.append({"code": "index_target_missing", "path": path})

    parent_text_cache: dict[str, str] = {}
    for path in sorted(nested):
        record = record_by_path[path]
        parent = record["parent"]
        if not parent:
            errors.append({"code": "nested_parent_missing", "path": path})
            continue
        if str(parent) not in parent_text_cache:
            parent_text_cache[str(parent)] = load_text(root / str(parent)).text
        target_from_parent = Path(path).relative_to(Path(str(parent)).parent).as_posix()
        parent_targets = {target.split("#", 1)[0].replace("\\", "/") for target in markdown_links(parent_text_cache[str(parent)])}
        if target_from_parent not in parent_targets:
            errors.append({"code": "nested_not_linked", "path": path, "parent": parent})

    title_groups: dict[str, list[str]] = defaultdict(list)
    hash_groups: dict[str, list[str]] = defaultdict(list)
    for record in records:
        path = str(record["path"])
        title = str(record["title"])
        if not title:
            errors.append({"code": "missing_h1", "path": path})
        else:
            title_groups[title].append(path)
        hash_groups[str(record["content_sha256"])].append(path)
        if record["kind"] == "canonical":
            loaded = load_text(root / path)
            metadata = parse_metadata(loaded.text)
            for field in ("source", "archive_date", "category"):
                if not metadata.get(field):
                    errors.append({"code": "canonical_metadata_missing", "path": path, "field": field})
            if metadata.get("category") and not category_metadata_matches(
                metadata["category"], str(record["category"])
            ):
                errors.append(
                    {
                        "code": "category_metadata_mismatch",
                        "path": path,
                        "metadata": metadata["category"],
                        "directory": record["category"],
                    }
                )
            if not metadata.get("original_date"):
                warnings.append({"code": "canonical_original_date_missing", "path": path})

    for title, paths in sorted(title_groups.items()):
        if len(paths) > 1:
            errors.append({"code": "duplicate_h1", "title": title, "paths": paths})
    for digest, paths in sorted(hash_groups.items()):
        if len(paths) > 1:
            errors.append({"code": "duplicate_content", "sha256": digest, "paths": paths})

    for path in iter_article_paths(root):
        loaded = load_text(path)
        marker = find_tail_marker(loaded.text)
        if marker:
            errors.append(
                {
                    "code": "high_confidence_tail_noise",
                    "path": path.relative_to(root).as_posix(),
                    "line": marker[0] + 1,
                    "marker": marker[1],
                }
            )
        for target in markdown_links(loaded.text):
            clean = unquote(target.strip().split("#", 1)[0])
            if not clean or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", clean):
                continue
            suffix = Path(clean).suffix.lower()
            if suffix not in LOCAL_LINK_SUFFIXES:
                continue
            resolved = (path.parent / clean).resolve()
            if not resolved.exists():
                errors.append(
                    {
                        "code": "local_link_missing",
                        "path": path.relative_to(root).as_posix(),
                        "target": target,
                    }
                )

    if check_generated:
        generated_md = root / GENERATED_MARKDOWN
        generated_json = root / GENERATED_JSON
        if not generated_md.is_file() or load_text(generated_md).text != markdown:
            errors.append({"code": "catalog_markdown_stale", "path": GENERATED_MARKDOWN})
        if not generated_json.is_file() or load_text(generated_json).text != payload:
            errors.append({"code": "catalog_json_stale", "path": GENERATED_JSON})

    return {
        "ok": not errors,
        "article_count": len(records),
        "canonical_count": len(canonical),
        "nested_count": len(nested),
        "category_counts": dict(sorted(Counter(str(record["category"]) for record in records).items())),
        "errors": errors,
        "warnings": warnings,
    }


def write_report(report: dict[str, object], path: Path | None) -> None:
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="article repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="regenerate CATALOG.md and catalog.json")
    generate_parser.add_argument("--report", type=Path)

    check_parser = subparsers.add_parser("check", help="validate structure, metadata, links, noise, and generated files")
    check_parser.add_argument("--report", type=Path)

    sanitize_parser = subparsers.add_parser("sanitize", help="truncate high-confidence source-platform or promotion tails")
    sanitize_parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
    sanitize_parser.add_argument("--report", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    if not (root / "INDEX.md").is_file():
        raise SystemExit(f"article root is invalid: {root}")

    if args.command == "generate":
        report = generate(root)
        write_report(report, args.report)
        return 0
    if args.command == "sanitize":
        report = sanitize(root, apply=args.apply)
        write_report(report, args.report)
        return 0 if not report["skipped_count"] else 2
    if args.command == "check":
        report = audit(root, check_generated=True)
        write_report(report, args.report)
        return 0 if report["ok"] else 1
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
