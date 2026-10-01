#!/usr/bin/env python3
"""Generate and validate the reverse-engineering knowledge-base catalog.

YAML v2 metadata uses PyYAML's safe loader (PyYAML >= 6, < 7).
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
from urllib.parse import unquote, urlsplit

try:
    from markdown_it import MarkdownIt
except ImportError:
    MarkdownIt = None

try:
    import yaml
except ImportError:
    yaml = None


GENERATED_MARKDOWN = "CATALOG.md"
GENERATED_JSON = "catalog.json"
ROOT_MARKDOWN = {"AGENTS.md", "INDEX.md", "README.md", GENERATED_MARKDOWN}
EXCLUDED_DIRS = {".git", "__pycache__", "pending", "scripts", "tests", "templates", "docs"}
LOCAL_LINK_SUFFIXES = {".gif", ".jpeg", ".jpg", ".json", ".md", ".pdf", ".png", ".svg", ".txt"}
DOCUMENT_TYPES = {"archive", "reference", "procedure", "case"}
MODULE_NAMES = {"interfaces", "parameters", "request-chain", "risk-control", "validation", "decision-flow"}
EVIDENCE_BASES = {"unknown", "source-report", "static-review", "runtime-observation", "local-parity", "server-accepted"}
RELATION_TYPES = {"derived_from", "supplements", "supersedes", "conflicts_with", "applies_to"}
PROCEDURE_ANCHORS = {"prerequisites", "steps", "outputs", "acceptance", "failure-exits"}
ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


def split_frontmatter(text: str) -> tuple[dict[str, object] | None, str, list[str]]:
    """Parse real YAML safely; legacy articles never require the dependency."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None, text, []
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}, text, ["frontmatter_unclosed"]
    body = "".join(lines[end + 1:])
    if yaml is None:
        return {}, body, ["PyYAML >= 6, < 7 required; install with python -m pip install 'PyYAML>=6,<7'"]

    class StrictSafeLoader(yaml.SafeLoader):
        def compose_node(self, parent, index):
            if self.check_event(yaml.AliasEvent):
                raise yaml.YAMLError("YAML aliases are not supported in knowledge metadata")
            return super().compose_node(parent, index)

        def construct_mapping(self, node, deep=False):
            mapping = {}
            for key_node, value_node in node.value:
                key = self.construct_object(key_node, deep=deep)
                if not isinstance(key, str):
                    raise yaml.YAMLError("metadata keys must be strings")
                if key in mapping:
                    raise yaml.YAMLError(f"duplicate key: {key}")
                mapping[key] = self.construct_object(value_node, deep=deep)
            return mapping

    # Keep date-shaped scalars as text, without changing global SafeLoader state.
    StrictSafeLoader.yaml_implicit_resolvers = {
        key: [(tag, regex) for tag, regex in entries if tag != "tag:yaml.org,2002:timestamp"]
        for key, entries in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }
    try:
        metadata = yaml.load("".join(lines[1:end]), Loader=StrictSafeLoader)
        if not isinstance(metadata, dict):
            return {}, body, ["frontmatter_must_be_mapping"]
        return metadata, body, []
    except (yaml.YAMLError, RecursionError) as exc:
        return {}, body, [f"invalid_yaml: {exc}"]


def markdown_content_lines(text: str) -> Iterable[tuple[int, str]]:
    """Yield non-fenced Markdown with original line indices.

    Match fence character and minimum run length; triple ticks inside a four-tick
    example, or tildes inside backticks, cannot accidentally reopen structure.
    """
    fence: tuple[str, int] | None = None
    for index, line in enumerate(text.splitlines()):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = (marker[1][0], len(marker[1]))
            continue
        yield index, line


def markdown_heading_entries(text: str) -> list[tuple[int, int, int, str]]:
    """(start line, end line, level, inline text), excluding every code form."""
    if MarkdownIt is None:
        raise RuntimeError("markdown-it-py >= 3, < 5 required; install with python -m pip install 'markdown-it-py>=3,<5'")
    tokens = MarkdownIt("commonmark").parse(text)
    return [(token.map[0], token.map[1], int(token.tag[1:]), tokens[index + 1].content)
            for index, token in enumerate(tokens)
            if token.type == "heading_open" and token.map and index + 1 < len(tokens)]


def document_anchors(text: str) -> dict[str, str]:
    """GitHub-style heading IDs plus stable explicit <a id=...> anchors.

    Values are the following section's text, used to reject empty module stubs.
    Code fences do not declare document anchors.
    """
    anchors: dict[str, str] = {}
    counts: Counter[str] = Counter()
    markers: list[tuple[int, str, bool, int]] = []
    lines = text.splitlines()
    heading_entries = markdown_heading_entries(text)
    heading_map = {start: (end, level) for start, end, level, _ in heading_entries}
    for index, line in markdown_content_lines(text):
        for explicit in re.findall(r'<a\s+(?:id|name)=["\x27]([^"\x27]+)["\x27]\s*></a>', line):
            markers.append((index, explicit, True, 7))
    for index, end, level, heading_text in heading_entries:
        title = strip_inline_markdown(heading_text).lower()
        slug = re.sub(r"[^\w\- ]", "", title).replace(" ", "-")
        suffix = f"-{counts[slug]}" if counts[slug] else ""
        counts[slug] += 1
        markers.append((index, slug + suffix, False, level))
    markers.sort(key=lambda item: (item[0], not item[2]))
    sections: list[tuple[int, str, int, int]] = []
    for index, anchor, explicit, level in markers:
        # An explicit anchor immediately before its heading owns that heading's body.
        start = index + 1
        while start < len(lines) and not lines[start].strip():
            start += 1
        if explicit and start in heading_map:
            start, level = heading_map[start]
        elif not explicit and index in heading_map:
            start = heading_map[index][0]
        sections.append((index, anchor, level, start))
    for _, anchor, level, start in sections:
        stop = next((i for i, _, other_level, _ in sections if i >= start and other_level <= level), len(lines))
        content = "\n".join(lines[start:stop]).strip()
        # Child headings/anchors are part of their parent section, but a stack of
        # headings alone is not content. Nonempty fenced examples still count.
        cleaned = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        outside = dict(markdown_content_lines(cleaned))
        substantive = False
        for index, line in enumerate(cleaned.splitlines()):
            if not line.strip() or re.match(r"^ {0,3}(`{3,}|~{3,})", line):
                continue
            if index in outside and (re.match(r"^#{1,6}\s|^<a\s", line) or re.fullmatch(r"\s*[-*_]{3,}\s*", line)):
                continue
            substantive = True
            break
        anchors[anchor] = content if substantive else ""
    return anchors


def validate_frontmatter(metadata: dict[str, object], body: str) -> list[str]:
    issues: list[str] = []

    def nonempty(value: object) -> bool:
        return isinstance(value, str) and bool(value.strip())

    def keys(value: dict, allowed: set[str], context: str) -> None:
        for key in sorted(set(value) - allowed):
            issues.append(f"{context}.unknown_field:{key}")

    keys(metadata, {"schema_version", "id", "document_type", "scope", "sources", "modules", "relations", "tags", "source_completeness", "original_date", "archived_date"}, "metadata")
    for field in ("original_date", "archived_date"):
        if field in metadata and not nonempty(metadata[field]):
            issues.append(f"{field}_must_be_nonempty_string")
    if type(metadata.get("schema_version")) is not int or metadata.get("schema_version") != 2:
        issues.append("schema_version_must_be_2")
    if not isinstance(metadata.get("id"), str) or not ID_PATTERN.fullmatch(metadata["id"]):
        issues.append("invalid_stable_id")
    doc_type = metadata.get("document_type")
    if not isinstance(doc_type, str) or doc_type not in DOCUMENT_TYPES:
        issues.append("invalid_document_type")
    scope = metadata.get("scope")
    if not isinstance(scope, dict):
        issues.append("scope_required")
    else:
        keys(scope, {"targets", "client", "version", "observed_at"}, "scope")
        targets = scope.get("targets")
        if not isinstance(targets, list) or not targets or not all(nonempty(v) for v in targets):
            issues.append("scope.targets_required")
        for field in ("client", "version", "observed_at"):
            if not nonempty(scope.get(field)):
                issues.append(f"scope.{field}_required")
    sources = metadata.get("sources")
    source_map: dict[str, dict] = {}
    if not isinstance(sources, list) or not sources:
        issues.append("sources_required")
    else:
        for source in sources:
            if not isinstance(source, dict):
                issues.append("invalid_source")
                continue
            keys(source, {"id", "ref", "basis", "reason", "citation"}, "source")
            sid = source.get("id")
            if not isinstance(sid, str) or not ID_PATTERN.fullmatch(sid):
                issues.append("invalid_source_id")
            elif sid in source_map:
                issues.append(f"duplicate_source_id:{sid}")
            else:
                source_map[sid] = source
            if "ref" in source and source["ref"] is None:
                if doc_type not in {"archive", "reference", "case"} or (source.get("basis") == "unknown" and doc_type != "archive"):
                    issues.append("nonlocatable_source_document_type_forbidden")
                if not nonempty(source.get("reason")):
                    issues.append("nonlocatable_source_reason_required")
                if source.get("basis") == "source-report":
                    if not nonempty(source.get("citation")):
                        issues.append("nonlocatable_source_citation_required")
                elif source.get("basis") != "unknown":
                    issues.append("nonlocatable_source_basis_unsupported")
                elif "citation" in source:
                    issues.append("unknown_source_cannot_claim_citation")
            elif not nonempty(source.get("ref")):
                issues.append("source.ref_required")
            elif "citation" in source or "reason" in source:
                issues.append("locatable_source_cannot_have_nonlocatable_fields")
            if not isinstance(source.get("basis"), str) or source["basis"] not in EVIDENCE_BASES:
                issues.append("invalid_source_basis")
    anchors = document_anchors(body)
    modules = metadata.get("modules", [])
    if not isinstance(modules, list):
        issues.append("modules_must_be_list")
    else:
        names: set[str] = set()
        for module in modules:
            if not isinstance(module, dict):
                issues.append("invalid_module")
                continue
            keys(module, {"name", "anchor", "sources", "basis", "limits"}, "module")
            name = module.get("name")
            if not isinstance(name, str) or name not in MODULE_NAMES:
                issues.append("invalid_module_name")
            elif name in names:
                issues.append(f"duplicate_module:{name}")
            else:
                names.add(name)
            anchor = module.get("anchor")
            if not isinstance(anchor, str) or anchor not in anchors:
                issues.append(f"module_anchor_missing:{anchor}")
            elif not anchors[anchor]:
                issues.append(f"module_empty:{anchor}")
            refs = module.get("sources")
            if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) and ref in source_map for ref in refs):
                issues.append(f"module_sources_invalid:{name}")
                refs = []
            basis = module.get("basis")
            if not isinstance(basis, str) or basis not in EVIDENCE_BASES:
                issues.append(f"invalid_module_basis:{name}")
            elif basis == "source-report" and not any(source_map[ref].get("basis") != "unknown" for ref in refs):
                issues.append(f"module_basis_unsupported:{name}")
            elif basis not in {"unknown", "source-report"} and not any(source_map[ref].get("basis") == basis for ref in refs):
                issues.append(f"module_basis_unsupported:{name}")
            if not nonempty(module.get("limits")):
                issues.append(f"module_limits_required:{name}")
        if doc_type == "reference" and not modules:
            issues.append("reference_modules_required")
    if doc_type == "archive" and metadata.get("source_completeness") not in ("complete", "partial", "unknown"):
        issues.append("archive_source_completeness_required")
    if "source_completeness" in metadata and metadata["source_completeness"] not in ("complete", "partial", "unknown"):
        issues.append("invalid_source_completeness")
    if doc_type == "procedure":
        for anchor in sorted(PROCEDURE_ANCHORS):
            if not anchors.get(anchor):
                issues.append(f"procedure_section_required:{anchor}")
    relations = metadata.get("relations", [])
    if not isinstance(relations, list):
        issues.append("relations_must_be_list")
    else:
        for relation in relations:
            if not isinstance(relation, dict):
                issues.append("invalid_relation")
                continue
            keys(relation, {"type", "target"}, "relation")
            if not isinstance(relation.get("type"), str) or relation["type"] not in RELATION_TYPES:
                issues.append("invalid_relation_type")
            if not nonempty(relation.get("target")):
                issues.append("relation_target_required")
            elif relation.get("type") == "derived_from" and not unquote(relation["target"].partition("#")[2]).strip():
                issues.append("derived_from_anchor_required")
    tags = metadata.get("tags", [])
    if not isinstance(tags, list) or not all(nonempty(tag) for tag in tags):
        issues.append("tags_must_be_strings")
    # A migrated document has one metadata authority, not two manually maintained copies.
    if parse_metadata(body):
        issues.append("mixed_frontmatter_blockquote_metadata")
    h1_count = sum(level == 1 for _, _, level, _ in markdown_heading_entries(body))
    if (doc_type == "archive" and h1_count < 1) or (doc_type != "archive" and h1_count != 1):
        issues.append("single_h1_required")
    try:
        json.dumps(metadata)
    except (TypeError, ValueError, RecursionError):
        issues.append("metadata_must_be_json_compatible")
    return issues

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


def extract_title(text: str, *, include_fenced_legacy: bool = False) -> str:
    # Preserve old legacy catalog identity; v2 uses CommonMark structure.
    if include_fenced_legacy:
        for line in text.splitlines():
            match = re.match(r"^#\s+(.+?)\s*$", line)
            if match:
                return strip_inline_markdown(match.group(1))
        return ""
    return next((strip_inline_markdown(title) for _, _, level, title in markdown_heading_entries(text) if level == 1), "")


def extract_headings(text: str) -> list[str]:
    return [strip_inline_markdown(title) for _, _, level, title in markdown_heading_entries(text) if level in {2, 3}]


def metadata_key(raw_key: str) -> str | None:
    key = normalize_space(raw_key).lower()
    for canonical, aliases in METADATA_ALIASES.items():
        if key in aliases:
            return canonical
    return None


HISTORY_OPEN = '<details data-kb-history="legacy-metadata">'
HISTORY_SUMMARY = '<summary>历史来源记录（迁移前元数据，非当前真源）</summary>'
HISTORY_CLOSE = '</details>'


def legacy_metadata_line_indices(text: str) -> list[int]:
    """Recognize only the existing metadata grammar outside code and history."""
    indices: list[int] = []
    historical = False
    for index, line in markdown_content_lines(text):
        if line == HISTORY_OPEN:
            historical = True
            continue
        if historical:
            if line == HISTORY_CLOSE:
                historical = False
            continue
        if index >= 40:
            break
        if not line.startswith(">"):
            continue
        match = re.match(r"^([^:：]{1,24})[:：]\s*(.+?)\s*$", line[1:].strip())
        if match and metadata_key(match.group(1)):
            indices.append(index)
    return indices


def unwrap_metadata_history(text: str) -> str:
    """Recover the pre-migration metadata view without treating it as authority.

    Only exact reserved wrapper lines are stripped, never arbitrary HTML.
    The migration receipt separately hashes every preserved historical span.
    """
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    historical = False
    for line in lines:
        value = line.rstrip("\r\n")
        if not historical and value == HISTORY_OPEN:
            historical = True
            continue
        if historical and value == HISTORY_SUMMARY:
            continue
        if historical and value == HISTORY_CLOSE:
            historical = False
            continue
        output.append(line)
    return "".join(output)


def parse_metadata(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    accepted = set(legacy_metadata_line_indices(text))
    for index, line in markdown_content_lines(text):
        if index not in accepted:
            continue
        if index >= 40:
            break
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
        frontmatter, body, parse_errors = split_frontmatter(loaded.text)
        metadata_errors = parse_errors + (validate_frontmatter(frontmatter, body) if frontmatter is not None and not parse_errors else [])
        rel = path.relative_to(root)
        rel_posix = rel.as_posix()
        catalog_body = unwrap_metadata_history(body)
        metadata = parse_metadata(catalog_body)
        original_date = metadata.get("original_date", "") or date_from_filename(path)
        index_entry = index_details.get(rel_posix, {})
        source = metadata.get("source", "") or str(index_entry.get("source_project", ""))
        kind = "canonical" if len(rel.parts) == 2 else "nested"
        record = {
            "path": rel_posix,
            "kind": kind,
            "category": rel.parts[0],
            "parent": parent_path(root, rel),
            "title": extract_title(body, include_fenced_legacy=frontmatter is None),
            "source": source,
            "original_date": original_date,
            "archive_date": metadata.get("archive_date", ""),
            "summary": extract_summary(catalog_body) or str(index_entry.get("index_summary", "")),
            "keywords": list(index_entry.get("keywords", [])),
            "headings": extract_headings(body),
            "bytes": len(path.read_bytes()),
            "lines": len(loaded.text.splitlines()),
            "content_sha256": hashlib.sha256(loaded.text.encode("utf-8")).hexdigest(),
        }
        valid = frontmatter if frontmatter is not None and not metadata_errors else {}
        record.update({
            "metadata_status": "legacy" if frontmatter is None else ("invalid" if metadata_errors else "v2"),
            "schema_version": valid.get("schema_version"),
            "id": valid.get("id"),
            "document_type": valid.get("document_type", "legacy" if frontmatter is None else "invalid"),
            "scope": valid.get("scope", {}),
            "sources": valid.get("sources", []),
            "modules": valid.get("modules", []),
            "relations": valid.get("relations", []),
            "tags": valid.get("tags", []),
            "source_completeness": valid.get("source_completeness", "unknown"),
            "metadata_errors": metadata_errors,
        })
        if valid:
            record["source"] = metadata.get("source") or "; ".join(item.get("ref") or item.get("citation") or "unknown" for item in valid["sources"])
            record["original_date"] = valid.get("original_date", original_date)
            record["archive_date"] = valid.get("archived_date", metadata.get("archive_date", ""))
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
        "schema_version": 2,
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
    for index, line in markdown_content_lines(text):
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
    """Parse CommonMark links, excluding fenced/indented/inline code correctly."""
    if MarkdownIt is None:
        raise RuntimeError("markdown-it-py >= 3, < 5 required; install with python -m pip install 'markdown-it-py>=3,<5'")
    parser = MarkdownIt("commonmark")
    def walk(tokens):
        for token in tokens:
            if token.type == "link_open":
                target = token.attrGet("href")
                if target:
                    yield target
            elif token.type == "image":
                target = token.attrGet("src")
                if target:
                    yield target
            if token.children:
                yield from walk(token.children)
    yield from walk(parser.parse(text))


def ambiguous_archive_links(root: Path, record: dict[str, object], body: str) -> set[str]:
    """Legacy exports contain un-fenced array/function syntax resembling links.

    Only non-path, non-anchor, extensionless unresolved candidates are ambiguous.
    Explicit paths and real file/anchor links always remain strict.
    """
    if record["document_type"] != "archive":
        return set()
    ambiguous: set[str] = set()
    for ref in markdown_links(body):
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", ref):
            continue
        pointer = unquote(ref.partition("#")[0])
        explicit = ("#" in ref or pointer.startswith(("./", "../", "/", "\\"))
                    or bool(re.search(r"\.[\w-]+$", pointer)))
        plausible_subpath = ("/" in pointer or "\\" in pointer) and not re.search(r'["<>|*()\[\]{}+,;=]|\s/\s', pointer)
        if explicit or plausible_subpath or not pointer:
            continue
        try:
            exists = ((root / record["path"]).parent / pointer).exists()
        except OSError:
            exists = False
        # Plain `[label](missing)` is a real broken link, not a blanket legacy waiver.
        # Only recognizable array access / call notation is ambiguous here.
        occurrences = list(re.finditer(r"(?P<prefix>[A-Za-z0-9_\]\)])\[(?P<label>[^\]]+)\]\((?P<target>[^)]+)\)", body))
        code_candidates = [match for match in occurrences if unquote(match["target"]) == unquote(ref)
                           and re.fullmatch(r"(?:[0-9.]+|[\"'][^\"']+[\"'])", match["label"])]
        if not exists and code_candidates:
            ambiguous.add(ref)
    return ambiguous


def audit_knowledge(root: Path, records: Sequence[dict[str, object]], warnings: list[dict[str, object]] | None = None) -> list[dict[str, object]]:
    errors: list[dict[str, object]] = []
    by_id: dict[str, dict] = {}
    by_path = {record["path"]: record for record in records}
    for record in records:
        for issue in record["metadata_errors"]:
            errors.append({"code": "metadata_v2_invalid", "path": record["path"], "detail": issue})
        if record["id"]:
            if record["id"] in by_id:
                errors.append({"code": "duplicate_stable_id", "id": record["id"], "paths": [by_id[record["id"]]["path"], record["path"]]})
            else:
                by_id[record["id"]] = record

    def resolve(record: dict, ref: str, *, allow_directory: bool = False) -> tuple[str | None, str]:
        if re.match(r"^https?://", ref, re.IGNORECASE):
            if re.search(r"\s", ref):
                raise ValueError("invalid_public_source_url")
            try:
                parsed = urlsplit(ref)
                if not parsed.hostname or parsed.username or parsed.password:
                    raise ValueError("invalid_public_source_url")
                _ = parsed.port
            except ValueError:
                raise ValueError("invalid_public_source_url") from None
            return None, ""
        pointer, _, anchor = ref.partition("#")
        pointer = unquote(pointer)
        anchor = unquote(anchor)
        if pointer.startswith("kb:"):
            target = by_id.get(pointer[3:])
            if target is None:
                raise ValueError("reference_id_missing")
            target_path = root / target["path"]
        else:
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", pointer) or "\\" in pointer or pointer.startswith("/"):
                raise ValueError("reference_scheme_or_absolute_path_forbidden")
            target_path = ((root / record["path"]).parent / pointer).resolve() if pointer else root / record["path"]
        try:
            rel = target_path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            raise ValueError("reference_outside_repository") from None
        if not target_path.is_file() and not (allow_directory and target_path.is_dir()):
            raise ValueError("reference_file_missing")
        if anchor:
            if target_path.suffix.lower() != ".md":
                raise ValueError("reference_anchor_requires_markdown")
            _, target_body, _ = split_frontmatter(load_text(target_path).text)
            if anchor not in document_anchors(target_body):
                raise ValueError("reference_anchor_missing")
        return rel, anchor

    graph: dict[str, set[str]] = defaultdict(set)
    for record in records:
        if record["metadata_status"] != "v2":
            continue
        _, body, _ = split_frontmatter(load_text(root / record["path"]).text)
        references = [(item["ref"], "source", item) for item in record["sources"] if item["ref"] is not None]
        references += [(item["target"], "relation", item) for item in record["relations"]]
        ambiguous = ambiguous_archive_links(root, record, body)
        if warnings is not None:
            warnings.extend({"code": "ambiguous_body_link", "path": record["path"], "target": ref,
                             "limit": "Preserved legacy export syntax; not asserted to be a working link."}
                            for ref in sorted(ambiguous))
        references += [(ref, "link", {}) for ref in markdown_links(body) if ref not in ambiguous and not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", ref)]
        for ref, context, item in references:
            try:
                target_path, anchor = resolve(record, ref, allow_directory=context == "link")
                if target_path is None:
                    continue
                if context in {"source", "relation"} and target_path not in by_path:
                    raise ValueError("knowledge_reference_requires_article")
                if context == "source" or (context == "relation" and item.get("type") == "derived_from"):
                    graph[record["path"]].add(target_path)
                if context == "source":
                    target = by_path[target_path]
                    if (target["metadata_status"] == "v2" and target["sources"]
                            and all(source["basis"] == "unknown" for source in target["sources"])
                            and item["basis"] != "unknown"):
                        raise ValueError("unknown_source_cannot_support_evidence_upgrade")
                if context == "source" and item["basis"] not in {"unknown", "source-report"}:
                    target = by_path[target_path]
                    evidence = [module["basis"] for module in target["modules"] if not anchor or module["anchor"] == anchor]
                    if item["basis"] not in evidence:
                        raise ValueError("source_basis_not_supported_by_target_module")
            except ValueError as exc:
                errors.append({"code": str(exc), "path": record["path"], "context": context, "target": ref})

    # Only provenance is acyclic. supplements/conflicts_with may legitimately be mutual.
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(path: str) -> None:
        if path in visiting:
            errors.append({"code": "provenance_cycle", "path": path})
            return
        if path in visited:
            return
        visiting.add(path)
        for target in sorted(graph.get(path, set())):
            visit(target)
        visiting.remove(path)
        visited.add(path)
    for path in sorted(graph):
        visit(path)
    return errors


def query_records(records: Sequence[dict[str, object]], *, target: str | None = None,
                  module: str | None = None, document_type: str | None = None,
                  client: str | None = None, version: str | None = None,
                  observed_at: str | None = None, tag: str | None = None,
                  basis: str | None = None, limit: int = 20) -> dict[str, object]:
    """AND filters, exact case-insensitive values; one hit per matching module."""
    hits: list[dict[str, object]] = []
    def equal(actual: str, expected: str | None) -> bool:
        return expected is None or actual.casefold() == expected.casefold()
    for record in records:
        if record["metadata_status"] == "invalid" or not equal(record["document_type"], document_type):
            continue
        scope = record["scope"]
        if target and not any(equal(value, target) for value in scope.get("targets", [])):
            continue
        if any(not equal(scope.get(key, "unknown"), value) for key, value in (("client", client), ("version", version), ("observed_at", observed_at))):
            continue
        if tag and not any(equal(value, tag) for value in record["tags"] + record["keywords"]):
            continue
        modules = record["modules"] or [{"name": None, "anchor": None, "basis": "unknown", "sources": [], "limits": "No module evidence declared; legacy/source archival is not technical verification."}]
        for item in modules:
            if not equal(item["name"] or "", module) or not equal(item["basis"], basis):
                continue
            hits.append({"id": record["id"], "path": record["path"], "anchor": item["anchor"], "title": record["title"], "document_type": record["document_type"], "module": item["name"], "scope": scope, "basis": item["basis"], "limits": item["limits"], "sources": [source for source in record["sources"] if not item["sources"] or source["id"] in item["sources"]]})
    return {"count": len(hits), "returned": min(limit, len(hits)), "results": hits[:limit]}


def audit(root: Path, check_generated: bool = True) -> dict[str, object]:
    markdown, payload, records = expected_generated(root)
    warnings: list[dict[str, object]] = []
    errors: list[dict[str, object]] = audit_knowledge(root, records, warnings)
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
        parent_targets = {unquote(target.split("#", 1)[0]).replace("\\", "/") for target in markdown_links(parent_text_cache[str(parent)])}
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
        if record["kind"] == "canonical" and record["metadata_status"] == "legacy":
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
        "metadata_counts": dict(sorted(Counter(str(record["metadata_status"]) for record in records).items())),
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

    query_parser = subparsers.add_parser("query", help="query compact scoped module pointers (AND filters)")
    query_parser.add_argument("--target")
    query_parser.add_argument("--module", choices=sorted(MODULE_NAMES))
    query_parser.add_argument("--type", dest="document_type", choices=sorted(DOCUMENT_TYPES | {"legacy"}))
    query_parser.add_argument("--client")
    query_parser.add_argument("--version")
    query_parser.add_argument("--observed-at")
    query_parser.add_argument("--tag")
    query_parser.add_argument("--basis", choices=sorted(EVIDENCE_BASES))
    query_parser.add_argument("--limit", type=int, default=20)
    query_parser.add_argument("--report", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    if MarkdownIt is None:
        write_report({"ok": False, "error": "markdown-it-py >= 3, < 5 required; install with python -m pip install 'markdown-it-py>=3,<5'"}, getattr(args, "report", None))
        return 2
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
    if args.command == "query":
        if args.limit < 1:
            raise SystemExit("--limit must be positive")
        records = build_records(root)
        errors = audit_knowledge(root, records)
        if errors:
            write_report({"ok": False, "errors": errors}, args.report)
            return 1
        report = query_records(records, **{key: getattr(args, key) for key in ("target", "module", "document_type", "client", "version", "observed_at", "tag", "basis", "limit")})
        compact = json.dumps(report, ensure_ascii=False, separators=(",", ":")) + "\n"
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(compact, encoding="utf-8", newline="\n")
        else:
            sys.stdout.write(compact)
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
