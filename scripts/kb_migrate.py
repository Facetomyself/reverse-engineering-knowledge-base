#!/usr/bin/env python3
"""One-shot, byte-preserving knowledge migration: plan -> apply -> verify.

Plan and backups live outside the article repository. No source deletion, Git
operations, implicit inference, or scheduled automation is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import kb_catalog as kb

SCHEMA_VERSION = 1
EXCLUDED = {".git", "pending", "__pycache__", ".pytest_cache"}
GENERATED = {kb.GENERATED_MARKDOWN, kb.GENERATED_JSON}


class MigrationError(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


@contextmanager
def locked_target_file(path: Path):
    """Windows handle denies WRITE and DELETE, including editor atomic-save.

    Targets are updated through this same checked handle, not via rename. Readers
    may see an in-progress file; backups and the external journal are authoritative
    recovery artifacts after interruption. An unknown partial hash is never
    overwritten automatically. Non-Windows publication fails closed.
    """
    if os.name != "nt":
        raise MigrationError("safe_target_publication_requires_windows")
    import ctypes
    import msvcrt
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                 ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.CreateFileW(str(path), 0x80000000 | 0x40000000, 0x1, None, 3, 0x80, None)
    if handle == ctypes.c_void_p(-1).value:
        raise MigrationError(f"target_lock_failed:{path.name}:{ctypes.get_last_error()}")
    try:
        fd = msvcrt.open_osfhandle(handle, os.O_RDWR | os.O_BINARY)
    except BaseException:
        kernel.CloseHandle(handle)
        raise
    with os.fdopen(fd, "r+b", buffering=0) as stream:
        if os.fstat(stream.fileno()).st_nlink != 1:
            raise MigrationError(f"hardlinked_target_forbidden:{path.name}")
        yield stream


def write_locked_stream(stream, raw: bytes) -> None:
    stream.seek(0)
    remaining = memoryview(raw)
    while remaining:
        written = stream.write(remaining)
        if not written:
            raise OSError("short target write")
        remaining = remaining[written:]
    stream.truncate()
    stream.flush()
    os.fsync(stream.fileno())


def atomic_write(path: Path, raw: bytes, expected_sha256: str | None = None) -> None:
    """Atomic external receipts; exclusive checked-handle writes for targets."""
    if path.is_symlink():
        raise MigrationError(f"symlink_target:{path}")
    if expected_sha256 is not None:
        with locked_target_file(path) as stream:
            original = stream.read()
            if sha(original) != expected_sha256:
                raise MigrationError(f"target_changed_at_publication:{path.name}")
            try:
                write_locked_stream(stream, raw)
                # Creating a hardlink is not blocked by Windows share flags.
                # Recheck while still locked and restore original bytes on drift.
                if os.fstat(stream.fileno()).st_nlink != 1:
                    raise MigrationError(f"hardlink_created_during_publication:{path.name}")
            except BaseException as exc:
                # No other writer or rename can enter this locked window.
                try:
                    write_locked_stream(stream, original)
                except BaseException:
                    raise MigrationError(f"target_write_failed_original_backup_required:{path.name}") from exc
                raise MigrationError(f"target_write_failed_restored:{path.name}") from exc
        return
    fd, temporary = tempfile.mkstemp(prefix=".kb-migrate-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def safe_path(root: Path, relative: str) -> Path:
    if (not isinstance(relative, str) or not relative or "\\" in relative
            or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", relative)
            or relative.startswith("/") or any(part in {"", ".", ".."} for part in relative.split("/"))):
        raise MigrationError(f"unsafe_relative_path:{relative}")
    candidate = root / relative
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        raise MigrationError(f"path_outside_root:{relative}") from None
    current = candidate
    while current != root:
        if current.is_symlink():
            raise MigrationError(f"symlink_path:{relative}")
        current = current.parent
    return candidate


def snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    folded: set[str] = set()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED for part in relative.parts):
            continue
        if path.is_symlink():
            raise MigrationError(f"symlink_in_repository:{relative.as_posix()}")
        if not path.is_file():
            continue
        if path.stat().st_nlink != 1:
            raise MigrationError(f"hardlinked_input_forbidden:{relative.as_posix()}")
        name = relative.as_posix()
        if name.casefold() in folded:
            raise MigrationError(f"case_insensitive_name_collision:{name}")
        folded.add(name.casefold())
        result[name] = sha(path.read_bytes())
    return result


def wrap_legacy_metadata(raw: bytes) -> tuple[bytes, list[dict[str, Any]]]:
    """Only insert reserved wrappers; every original byte remains in order."""
    bom = raw.startswith(b"\xef\xbb\xbf")
    payload = raw[3:] if bom else raw
    text = payload.decode("utf-8")
    if kb.HISTORY_OPEN in text or kb.HISTORY_SUMMARY in text:
        raise MigrationError("reserved_history_marker_already_present")
    newline = "\r\n" if text.count("\r\n") > text.count("\n") - text.count("\r\n") else "\n"
    indices = kb.legacy_metadata_line_indices(text)
    lines = payload.splitlines(keepends=True)
    groups: list[tuple[int, int]] = []
    for index in indices:
        if groups and groups[-1][1] == index:
            groups[-1] = (groups[-1][0], index + 1)
        else:
            groups.append((index, index + 1))
    output: list[bytes] = []
    mappings: list[dict[str, Any]] = []
    position = 0
    for start, end in groups:
        output.extend(lines[position:start])
        prefix_start = sum(map(len, output))
        output.append((kb.HISTORY_OPEN + newline + kb.HISTORY_SUMMARY + newline).encode("utf-8"))
        prefix_end = sum(map(len, output))
        preserved = b"".join(lines[start:end])
        output.append(preserved)
        suffix_start = sum(map(len, output))
        # A terminal metadata line without newline gets an insertion, not an edit.
        if not preserved.endswith((b"\n", b"\r")):
            output.append(newline.encode("ascii"))
        terminal = end == len(lines) and not payload.endswith((b"\n", b"\r"))
        output.append((kb.HISTORY_CLOSE + ("" if terminal else newline)).encode("utf-8"))
        suffix_end = sum(map(len, output))
        mappings.append({"original_start_line": start + 1, "original_end_line": end,
                         "original_byte_start": sum(map(len, lines[:start])) + (3 if bom else 0),
                         "original_byte_end": sum(map(len, lines[:end])) + (3 if bom else 0),
                         "preserved_sha256": sha(preserved), "bytes": len(preserved),
                         "destination": 'details[data-kb-history="legacy-metadata"]',
                         "inserted_ranges": [[prefix_start, prefix_end], [suffix_start, suffix_end]]})
        position = end
    output.extend(lines[position:])
    return b"".join(output), mappings


def transform(raw: bytes, entry: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    text = raw.decode("utf-8-sig")
    existing, _, errors = kb.split_frontmatter(text)
    if existing is not None or errors:
        raise MigrationError("target_not_legacy")
    metadata = entry.get("metadata")
    if not isinstance(metadata, dict):
        raise MigrationError("metadata_mapping_required")
    if metadata.get("document_type") not in {"archive", "reference", "case"}:
        raise MigrationError("bulk_migration_requires_reviewed_archive_reference_or_case")
    body, history = wrap_legacy_metadata(raw)
    newline = "\r\n" if text.count("\r\n") > text.count("\n") - text.count("\r\n") else "\n"
    title_basis = entry.get("title_basis") or entry.get("title_fallback_basis")
    original_title = kb.extract_title(text)
    inserted_title = None
    if not original_title:
        inserted_title = entry.get("title_if_missing")
        if (not isinstance(inserted_title, str) or not inserted_title.strip()
                or any(char in inserted_title for char in "\r\n") or not title_basis):
            raise MigrationError("missing_h1_requires_reviewed_title_and_basis")
        body = ("# " + inserted_title + newline + newline).encode("utf-8") + body
    elif entry.get("title_if_missing"):
        raise MigrationError("title_override_for_existing_h1_forbidden")
    problems = kb.validate_frontmatter(metadata, body.decode("utf-8"))
    if problems:
        raise MigrationError("invalid_migrated_metadata:" + json.dumps(problems, ensure_ascii=False))
    frontmatter = "---\n" + kb.yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=120) + "---\n\n"
    prefix = frontmatter.replace("\n", newline).encode("utf-8")
    result = (b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"") + prefix + body
    # Stronger than a normalized-text comparison: reconstruct original exactly.
    reconstructed = body
    if inserted_title:
        reconstructed = reconstructed[len(("# " + inserted_title + newline + newline).encode("utf-8")):]
    # Remove only ranges inserted by this operation, not arbitrary original HTML.
    original_parts: list[bytes] = []
    cursor = 0
    for start, end in sorted(span for item in history for span in item["inserted_ranges"]):
        original_parts.append(reconstructed[cursor:start])
        cursor = end
    original_parts.append(reconstructed[cursor:])
    reconstructed = b"".join(original_parts)
    original_payload = raw[3:] if raw.startswith(b"\xef\xbb\xbf") else raw
    if reconstructed != original_payload:
        raise MigrationError("body_byte_preservation_failed")
    return result, {"body_bytes_preserved": True, "bom_preserved": raw.startswith(b"\xef\xbb\xbf"),
                    "inserted_newline": repr(newline), "history": history,
                    "inserted_title": inserted_title, "title_basis": title_basis,
                    "legacy_metadata": kb.parse_metadata(text)}


def _copy_repository(root: Path, destination: Path) -> None:
    shutil.copytree(root, destination, ignore=shutil.ignore_patterns(*EXCLUDED))


def plan(root: Path, manifest_path: Path, output: Path) -> dict[str, Any]:
    root, output = root.resolve(), output.resolve()
    if not (root / "INDEX.md").is_file():
        raise MigrationError("article_root_requires_index")
    if output == root or root in output.parents:
        raise MigrationError("plan_directory_must_be_outside_article_root")
    if output.exists():
        raise MigrationError("plan_directory_already_exists")
    output.mkdir(parents=True)
    write_json(output / "receipt.json", {"status": "planning", "root": str(root)})
    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
        if manifest.get("schema_version") != SCHEMA_VERSION or not isinstance(manifest.get("records"), list):
            raise MigrationError("invalid_manifest_schema")
        initial = snapshot(root)
        article_paths = {path.relative_to(root).as_posix() for path in kb.iter_article_paths(root)}
        entries = []
        seen: set[str] = set()
        before_records = {record["path"]: record for record in kb.build_records(root)}
        baseline_report = kb.audit(root, check_generated=False)
        if not baseline_report["ok"]:
            write_json(output / "baseline-validation.json", baseline_report)
            raise MigrationError("baseline_validation_failed")
        for item in manifest["records"]:
            relative = item.get("path")
            target = safe_path(root, relative)
            if relative.casefold() in seen or relative not in article_paths:
                raise MigrationError(f"duplicate_or_nonarticle_target:{relative}")
            seen.add(relative.casefold())
            raw = target.read_bytes()
            if sha(raw) != item.get("pre_sha256"):
                raise MigrationError(f"changed_since_inventory:{relative}")
            if item.get("action") == "preserve_v2":
                if before_records[relative]["metadata_status"] != "v2":
                    raise MigrationError(f"preserve_target_not_v2:{relative}")
                continue
            migrated, preservation = transform(raw, item)
            for folder, content in (("backup", raw), ("staged", migrated)):
                stored = safe_path(output / folder, relative)
                stored.parent.mkdir(parents=True, exist_ok=True)
                stored.write_bytes(content)
            entries.append({"path": relative, "kind": "article", "before_sha256": sha(raw),
                            "after_sha256": sha(migrated), "preservation": preservation})
        if not entries:
            raise MigrationError("no_migration_targets")
        with tempfile.TemporaryDirectory(prefix="kb-migration-check-") as temporary:
            isolated = Path(temporary) / "article"
            _copy_repository(root, isolated)
            for entry in entries:
                safe_path(isolated, entry["path"]).write_bytes(safe_path(output / "staged", entry["path"]).read_bytes())
            kb.generate(isolated)
            validation = kb.audit(isolated, check_generated=True)
            write_json(output / "validation.json", validation)
            if not validation["ok"]:
                raise MigrationError("projected_full_corpus_validation_failed")
            after_records = {record["path"]: record for record in kb.build_records(isolated)}
            fields = ("source", "original_date", "archive_date", "summary", "title", "keywords", "headings", "kind", "category", "parent", "document_type", "scope", "sources", "id")
            for entry in entries:
                before, after = before_records[entry["path"]], after_records[entry["path"]]
                entry["catalog_field_changes"] = {field: {"before": before[field], "after": after[field]} for field in fields if before[field] != after[field]}
            for name in sorted(GENERATED):
                target = root / name
                if not target.is_file():
                    raise MigrationError(f"generated_baseline_required:{name}")
                old, new = target.read_bytes(), (isolated / name).read_bytes()
                (output / "backup" / name).write_bytes(old)
                (output / "staged" / name).write_bytes(new)
                entries.append({"path": name, "kind": "generated", "before_sha256": sha(old), "after_sha256": sha(new)})
        if snapshot(root) != initial:
            raise MigrationError("repository_changed_during_plan")
        result = {"schema_version": SCHEMA_VERSION, "root": str(root), "manifest_sha256": sha(manifest_bytes),
                  "created_at": datetime.now(timezone.utc).isoformat(), "snapshot": initial, "entries": entries,
                  "validation": {"ok": True, "article_count": validation["article_count"], "warnings": validation["warnings"]}}
        write_json(output / "input-manifest.json", manifest)
        write_json(output / "plan.json", result)
        digest = sha((output / "plan.json").read_bytes())
        (output / "plan.sha256").write_text(digest + "\n", encoding="ascii", newline="\n")
        write_json(output / "receipt.json", {"status": "planned", "plan_sha256": digest, "article_targets": len(entries) - 2,
                                            "generated_targets": 2, "applied": [], "root_unchanged": True})
        return {"ok": True, "status": "planned", "plan": str(output / "plan.json"), "targets": len(entries)}
    except Exception as exc:
        write_json(output / "receipt.json", {"status": "plan_failed", "error": str(exc), "root_unchanged": True})
        raise


def load_plan(root: Path, directory: Path) -> dict[str, Any]:
    root, directory = root.resolve(), directory.resolve()
    if directory == root or root in directory.parents:
        raise MigrationError("plan_directory_must_be_outside_article_root")
    raw = (directory / "plan.json").read_bytes()
    if sha(raw) != (directory / "plan.sha256").read_text(encoding="ascii").strip():
        raise MigrationError("plan_hash_mismatch")
    result = json.loads(raw)
    if result.get("schema_version") != SCHEMA_VERSION or Path(result["root"]).resolve() != root:
        raise MigrationError("plan_root_or_schema_mismatch")
    seen: set[str] = set()
    article_paths = {p.relative_to(root).as_posix() for p in kb.iter_article_paths(root)}
    for entry in result["entries"]:
        name = entry["path"]
        safe_path(root, name)
        if name.casefold() in seen or name not in result["snapshot"] or entry["before_sha256"] != result["snapshot"][name]:
            raise MigrationError(f"invalid_plan_entry:{name}")
        seen.add(name.casefold())
        if entry["kind"] == "generated":
            if name not in GENERATED:
                raise MigrationError(f"invalid_generated_target:{name}")
        elif entry["kind"] != "article" or name not in article_paths:
            raise MigrationError(f"invalid_article_target:{name}")
        for folder, field in (("backup", "before_sha256"), ("staged", "after_sha256")):
            if sha(safe_path(directory / folder, name).read_bytes()) != entry[field]:
                raise MigrationError(f"{folder}_hash_mismatch:{name}")
    return result


def preflight_current(root: Path, plan_data: dict[str, Any]) -> dict[str, str]:
    current = snapshot(root)
    expected = plan_data["snapshot"]
    if set(current) != set(expected):
        raise MigrationError("repository_file_set_changed_since_plan")
    entries = {entry["path"]: entry for entry in plan_data["entries"]}
    for name, digest in current.items():
        permitted = {expected[name]}
        if name in entries:
            permitted.add(entries[name]["after_sha256"])
        if digest not in permitted:
            raise MigrationError(f"changed_since_plan:{name}")
    return current


def projected_validation(root: Path, directory: Path, plan_data: dict[str, Any], restore: bool = False) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="kb-migration-preflight-") as temporary:
        isolated = Path(temporary) / "article"
        _copy_repository(root, isolated)
        for entry in plan_data["entries"]:
            (isolated / entry["path"]).write_bytes((directory / ("backup" if restore else "staged") / entry["path"]).read_bytes())
        result = kb.audit(isolated, check_generated=not restore)
    if not result["ok"]:
        write_json(directory / "prewrite-validation.json", result)
        raise MigrationError("prewrite_full_corpus_validation_failed")
    return result


def apply(root: Path, directory: Path, batch_size: int | None = None, restore: bool = False) -> dict[str, Any]:
    root, directory = root.resolve(), directory.resolve()
    if os.name != "nt":
        raise MigrationError("safe_target_publication_requires_windows")
    if batch_size is not None and batch_size < 1:
        raise MigrationError("batch_size_must_be_positive")
    receipt = {"status": "preflight", "operation": "restore" if restore else "apply", "written_this_call": []}
    try:
        plan_data = load_plan(root, directory)
        current = preflight_current(root, plan_data)
        projected_validation(root, directory, plan_data, restore=restore)
        # No target mutation until every input, backup, output and link has passed.
        if current != preflight_current(root, plan_data):
            raise MigrationError("repository_changed_during_preflight")
        desired_field = "before_sha256" if restore else "after_sha256"
        entries = [entry for entry in plan_data["entries"] if current[entry["path"]] != entry[desired_field]]
        selected = entries if batch_size is None else entries[:batch_size]
        receipt.update({"status": "restoring" if restore else "applying", "remaining_before": len(entries)})
        write_json(directory / "receipt.json", receipt)
        for entry in selected:
            target = safe_path(root, entry["path"])
            if sha(target.read_bytes()) != current[entry["path"]]:
                raise MigrationError(f"target_changed_immediately_before_write:{entry['path']}")
            payload = safe_path(directory / ("backup" if restore else "staged"), entry["path"]).read_bytes()
            if sha(payload) != entry[desired_field]:
                raise MigrationError(f"payload_changed_immediately_before_write:{entry['path']}")
            receipt["inflight"] = {"path": entry["path"], "expected_sha256": current[entry["path"]],
                                    "desired_sha256": entry[desired_field], "backup": "backup/" + entry["path"]}
            write_json(directory / "receipt.json", receipt)
            atomic_write(target, payload, expected_sha256=current[entry["path"]])
            receipt["inflight"] = None
            receipt["written_this_call"].append(entry["path"])
            write_json(directory / "receipt.json", receipt)
        current = preflight_current(root, plan_data)
        remaining = [entry["path"] for entry in plan_data["entries"] if current[entry["path"]] != entry[desired_field]]
        receipt.update({"ok": True, "status": ("restored" if restore else "applied") if not remaining else "partial",
                        "remaining": remaining, "changed_this_call": len(selected)})
        if not remaining:
            verified = kb.audit(root, check_generated=not restore)
            if not verified["ok"]:
                write_json(directory / "postwrite-validation.json", verified)
                raise MigrationError("postwrite_validation_failed")
            receipt["validation"] = {"ok": True, "article_count": verified["article_count"], "warnings": verified["warnings"]}
        write_json(directory / "receipt.json", receipt)
        return receipt
    except Exception as exc:
        receipt.update({"ok": False, "status": "failed", "error": str(exc), "recovery": "fix external drift, then repeat apply or use restore; no automatic deletion"})
        write_json(directory / "receipt.json", receipt)
        raise


def verify(root: Path, directory: Path) -> dict[str, Any]:
    root, directory = root.resolve(), directory.resolve()
    plan_data = load_plan(root, directory)
    current = preflight_current(root, plan_data)
    remaining = [entry["path"] for entry in plan_data["entries"] if current[entry["path"]] != entry["after_sha256"]]
    check = kb.audit(root, check_generated=not remaining)
    result = {"ok": check["ok"] and not remaining, "status": "verified" if not remaining and check["ok"] else "incomplete",
              "remaining": remaining, "validation": check}
    write_json(directory / "verification.json", result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("plan", help="dry-run: stage and validate without writing the article root")
    create.add_argument("--manifest", required=True, type=Path)
    create.add_argument("--out", required=True, type=Path)
    for name in ("apply", "restore", "verify"):
        item = sub.add_parser(name)
        item.add_argument("--plan", required=True, type=Path, help="directory containing plan.json")
        if name != "verify":
            item.add_argument("--batch-size", type=int)
    args = parser.parse_args(argv)
    try:
        if args.command == "plan":
            result = plan(args.root, args.manifest, args.out)
        elif args.command == "verify":
            result = verify(args.root, args.plan)
        else:
            result = apply(args.root, args.plan, args.batch_size, restore=args.command == "restore")
        print(json.dumps({key: value for key, value in result.items() if key not in {"remaining", "written_this_call", "validation"}}, ensure_ascii=False))
        return 0 if result.get("ok") else 1
    except (MigrationError, OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
