from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_kb_catalog import kb_catalog as kb

SPEC = importlib.util.spec_from_file_location("kb_migrate", Path(__file__).resolve().parents[1] / "scripts" / "kb_migrate.py")
migration = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = migration
SPEC.loader.exec_module(migration)


class MigrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "article"
        (self.root / "demo").mkdir(parents=True)
        self.paths = []

    def metadata(self, identifier="fixture-archive", citation=False):
        source = {"id": "s1", "ref": None, "basis": "unknown", "reason": "No original attribution remains."}
        if citation:
            source.update(basis="source-report", citation="Original Author, Research Notes", reason="No locator was provided.")
        return {"schema_version": 2, "id": identifier, "document_type": "archive",
                "scope": {"targets": ["unknown"], "client": "unknown", "version": "unknown", "observed_at": "unknown"},
                "sources": [source], "source_completeness": "unknown", "original_date": "2020-01-02", "archived_date": "2026-07-18"}

    def article(self, name="one", raw=None):
        if raw is None:
            raw = (f"# {name}\n\n> source: Original Author\n> original date: 2020-01-02\n> archive date: 2026-07-18\n> category: demo\n\n"
                   "This technical source paragraph remains exactly unchanged after migration.\n\n## Evidence\n\nObserved source limitations; no reproduction.\n").encode("utf-8")
        path = self.root / "demo" / (name + ".md")
        path.write_bytes(raw)
        self.paths.append(path)
        (self.root / "INDEX.md").write_text("# Index\n\n" + "\n".join(f"- [{p.stem}](./demo/{p.name})" for p in self.paths), encoding="utf-8")
        kb.generate(self.root)
        return {"path": path.relative_to(self.root).as_posix(), "pre_sha256": migration.sha(raw), "metadata": self.metadata("fixture-" + name)}

    def make_plan(self, entries):
        manifest = self.base / "manifest.json"
        manifest.write_text(json.dumps({"schema_version": 1, "records": entries}), encoding="utf-8")
        out = self.base / "plan"
        migration.plan(self.root, manifest, out)
        return out

    def test_dates_are_explicit_strings_and_not_observation(self):
        entry = self.article()
        result, _ = migration.transform((self.root / entry["path"]).read_bytes(), entry)
        fm, body, issues = kb.split_frontmatter(result.decode("utf-8"))
        self.assertFalse(issues)
        self.assertEqual(fm["scope"]["observed_at"], "unknown")
        self.assertEqual(fm["original_date"], "2020-01-02")
        self.assertEqual(fm["archived_date"], "2026-07-18")
        fm["original_date"] = 2020
        self.assertIn("original_date_must_be_nonempty_string", kb.validate_frontmatter(fm, body))
        literal = "---\noriginal_date: 2020-01-02\narchived_date: 2026-07-18\n---\n# Date\n"
        dates, _, _ = kb.split_frontmatter(literal)
        self.assertTrue(all(isinstance(value, str) for value in dates.values()))

    def test_unknown_source_requires_reason_and_archive(self):
        metadata = self.metadata()
        self.assertEqual(kb.validate_frontmatter(metadata, "# Source\n\nMaterial\n"), [])
        del metadata["sources"][0]["reason"]
        self.assertIn("nonlocatable_source_reason_required", kb.validate_frontmatter(metadata, "# Source\nText\n"))
        metadata = self.metadata()
        metadata["document_type"] = "case"
        self.assertIn("nonlocatable_source_document_type_forbidden", kb.validate_frontmatter(metadata, "# Source\nText\n"))

    def test_citation_only_source_is_bounded_and_allows_case_reference(self):
        metadata = self.metadata(citation=True)
        for document_type in ("archive", "case", "reference"):
            metadata["document_type"] = document_type
            if document_type == "reference":
                metadata["modules"] = [{"name": "parameters", "anchor": "evidence", "sources": ["s1"], "basis": "source-report", "limits": "Citation only, locator absent, not reproduced."}]
            self.assertEqual(kb.validate_frontmatter(metadata, "# Source\n\n## Evidence\n\nSource text.\n"), [])
        metadata["sources"][0]["basis"] = "runtime-observation"
        self.assertIn("nonlocatable_source_basis_unsupported", kb.validate_frontmatter(metadata, "# Source\n## Evidence\nText\n"))
        metadata["sources"][0]["basis"] = "source-report"
        metadata["document_type"] = "procedure"
        self.assertIn("nonlocatable_source_document_type_forbidden", kb.validate_frontmatter(metadata, "# Source\nText\n"))

    def test_unknown_source_cannot_upgrade_module(self):
        metadata = self.metadata()
        metadata["modules"] = [{"name": "parameters", "anchor": "evidence", "sources": ["s1"], "basis": "source-report", "limits": "unknown"}]
        self.assertIn("module_basis_unsupported:parameters", kb.validate_frontmatter(metadata, "# Source\n## Evidence\nText\n"))

    def test_unknown_target_cannot_be_cited_as_source_report(self):
        one, two = self.article("one"), self.article("two")
        two["metadata"]["sources"] = [{"id": "s1", "ref": "./one.md#evidence", "basis": "source-report"}]
        with self.assertRaisesRegex(migration.MigrationError, "projected_full_corpus_validation_failed"):
            self.make_plan([one, two])
        validation = json.loads((self.base / "plan/validation.json").read_text(encoding="utf-8"))
        self.assertIn("unknown_source_cannot_support_evidence_upgrade", str(validation))

    def test_history_and_entire_body_are_byte_preserved_with_mixed_eol_and_bom(self):
        raw = b'\xef\xbb\xbf# One\r\n\r\n> source: Original Author\r\n> archive date: 2026-07-18\n> original date: 2020-01-02\r\n> category: demo\r\n\r\n## Keep\n\n```python\r\n# not a heading\n> source: code literal\r\n```\r\n\nLast line without newline'
        entry = self.article(raw=raw)
        changed, receipt = migration.transform(raw, entry)
        self.assertTrue(changed.startswith(b"\xef\xbb\xbf---\r\n"))
        self.assertIn(b'```python\r\n# not a heading\n> source: code literal\r\n```\r\n\nLast line without newline', changed)
        self.assertTrue(changed.endswith(b"Last line without newline"))
        self.assertTrue(receipt["body_bytes_preserved"])
        fm, body, _ = kb.split_frontmatter(changed.decode("utf-8-sig"))
        self.assertFalse(kb.parse_metadata(body))
        self.assertEqual(kb.parse_metadata(kb.unwrap_metadata_history(body))["source"], "Original Author")
        for region in receipt["history"]:
            preserved = raw[region["original_byte_start"]:region["original_byte_end"]]
            self.assertEqual(migration.sha(preserved), region["preserved_sha256"])
            self.assertIn(preserved, changed)

    def test_terminal_metadata_without_newline_is_preserved(self):
        raw = b"# One\n\n> source: Author"
        entry = {"metadata": self.metadata()}
        changed, details = migration.transform(raw, entry)
        self.assertTrue(details["body_bytes_preserved"])
        self.assertIn(raw.split(b"\n")[-1], changed)
        self.assertFalse(changed.endswith(b"\n"))

    def test_original_html_details_is_not_removed_by_preservation_check(self):
        raw = b'# One\n\n> source: Author\n\n<details>\n<summary>Technical body</summary>\n\nLiteral technical source.\n</details>\n'
        changed, details = migration.transform(raw, {"metadata": self.metadata()})
        self.assertTrue(details["body_bytes_preserved"])
        self.assertIn(raw[raw.index(b"<details>"):], changed)

    @unittest.skipUnless(migration.os.name == "nt", "Windows exclusive handle contract")
    def test_target_lock_rejects_direct_write_and_atomic_editor_save(self):
        entry = self.article()
        target = self.root / entry["path"]
        original = target.read_bytes()
        alternative = self.root / "demo/editor-save.tmp"
        alternative.write_bytes(b"User save")
        with migration.locked_target_file(target) as stream:
            self.assertEqual(stream.read(), original)
            with self.assertRaises(OSError):
                target.write_bytes(b"Concurrent direct user write")
            with self.assertRaises(OSError):
                migration.os.replace(alternative, target)
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(alternative.read_bytes(), b"User save")

    @unittest.skipUnless(migration.os.name == "nt", "Windows exclusive handle contract")
    def test_failed_target_write_restores_under_same_lock(self):
        entry = self.article()
        target = self.root / entry["path"]
        original = target.read_bytes()
        actual = migration.write_locked_stream
        attempts = []
        def fail_once(stream, raw):
            attempts.append(True)
            if len(attempts) == 1:
                stream.seek(0)
                stream.write(b"PARTIAL")
                raise OSError("injected disk error")
            actual(stream, raw)
        with mock.patch.object(migration, "write_locked_stream", side_effect=fail_once):
            with self.assertRaisesRegex(migration.MigrationError, "target_write_failed_restored"):
                migration.atomic_write(target, b"replacement", expected_sha256=migration.sha(original))
        self.assertEqual(target.read_bytes(), original)

    def test_hardlinked_input_or_target_cannot_modify_outside_repository(self):
        entry = self.article()
        target = self.root / entry["path"]
        original = target.read_bytes()
        external = self.base / "outside-original.md"
        migration.os.link(target, external)
        with self.assertRaisesRegex(migration.MigrationError, "hardlinked_input_forbidden"):
            migration.snapshot(self.root)
        if migration.os.name == "nt":
            with self.assertRaisesRegex(migration.MigrationError, "hardlinked_target_forbidden"):
                migration.atomic_write(target, b"replacement", expected_sha256=migration.sha(original))
        self.assertEqual(external.read_bytes(), original)
        self.assertEqual(target.read_bytes(), original)

    @unittest.skipUnless(migration.os.name == "nt", "Windows exclusive handle contract")
    def test_hardlink_created_during_write_restores_original_while_locked(self):
        entry = self.article()
        target = self.root / entry["path"]
        original = target.read_bytes()
        external = self.base / "concurrent-link.md"
        actual = migration.write_locked_stream
        calls = []
        def link_once(stream, raw):
            calls.append(True)
            if len(calls) == 1:
                migration.os.link(target, external)
            actual(stream, raw)
        with mock.patch.object(migration, "write_locked_stream", side_effect=link_once):
            with self.assertRaisesRegex(migration.MigrationError, "target_write_failed_restored"):
                migration.atomic_write(target, b"replacement", expected_sha256=migration.sha(original))
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(external.read_bytes(), original)

    def test_no_h1_needs_reviewed_title_never_uses_fenced_heading(self):
        raw = b"```markdown\n# Example Only\n```\n\nTechnical body.\n"
        entry = {"metadata": self.metadata()}
        with self.assertRaisesRegex(migration.MigrationError, "reviewed_title"):
            migration.transform(raw, entry)
        entry.update(title_if_missing="Mechanical file title", title_basis="filename: fixture.md")
        changed, receipt = migration.transform(raw, entry)
        self.assertIn(raw, changed)
        self.assertEqual(receipt["inserted_title"], "Mechanical file title")

    def test_archives_keep_multiple_h1_other_types_do_not(self):
        body = "# One\n\nParagraph.\n\n# Two\n\nOther original section.\n"
        metadata = self.metadata()
        self.assertFalse(kb.validate_frontmatter(metadata, body))
        metadata = self.metadata(citation=True)
        metadata["document_type"] = "case"
        self.assertIn("single_h1_required", kb.validate_frontmatter(metadata, body))

    def test_duplicate_ids_fail_before_any_article_write(self):
        one, two = self.article("one"), self.article("two")
        two["metadata"]["id"] = one["metadata"]["id"]
        before = migration.snapshot(self.root)
        with self.assertRaisesRegex(migration.MigrationError, "projected_full_corpus_validation_failed"):
            self.make_plan([one, two])
        self.assertEqual(before, migration.snapshot(self.root))

    def test_source_cycles_fail_before_write(self):
        one, two = self.article("one"), self.article("two")
        one["metadata"]["sources"] = [{"id": "s1", "ref": "./two.md#evidence", "basis": "source-report"}]
        two["metadata"]["sources"] = [{"id": "s1", "ref": "./one.md#evidence", "basis": "source-report"}]
        with self.assertRaisesRegex(migration.MigrationError, "projected_full_corpus_validation_failed"):
            self.make_plan([one, two])
        self.assertIn("provenance_cycle", (self.base / "plan/validation.json").read_text(encoding="utf-8"))

    def test_plan_dry_run_apply_verify_restore_and_legacy_fields(self):
        entry = self.article()
        before = migration.snapshot(self.root)
        old_record = kb.build_records(self.root)[0]
        out = self.make_plan([entry])
        self.assertEqual(before, migration.snapshot(self.root))
        self.assertEqual(migration.apply(self.root, out)["status"], "applied")
        self.assertTrue(migration.verify(self.root, out)["ok"])
        record = kb.build_records(self.root)[0]
        for field in ("source", "original_date", "archive_date", "summary", "title", "headings"):
            self.assertEqual(record[field], old_record[field], field)
        self.assertEqual(migration.apply(self.root, out)["changed_this_call"], 0)
        self.assertEqual(migration.apply(self.root, out, restore=True)["status"], "restored")
        self.assertEqual(before, migration.snapshot(self.root))

    def test_changed_since_plan_in_target_or_dependency_blocks_all_writes(self):
        entry = self.article()
        out = self.make_plan([entry])
        index = self.root / "INDEX.md"
        index.write_bytes(index.read_bytes() + b"\nExternal edit.\n")
        before = migration.snapshot(self.root)
        with self.assertRaisesRegex(migration.MigrationError, "changed_since_plan"):
            migration.apply(self.root, out)
        self.assertEqual(before, migration.snapshot(self.root))

    def test_batch_interruption_resume_and_range_safe_restore(self):
        one, two = self.article("one"), self.article("two")
        before = migration.snapshot(self.root)
        out = self.make_plan([one, two])
        self.assertEqual(migration.apply(self.root, out, batch_size=1)["status"], "partial")
        self.assertFalse(migration.verify(self.root, out)["ok"])
        real_write = migration.atomic_write
        def failing_write(path, payload, **kwargs):
            if path == self.root / "catalog.json":
                raise OSError("simulated interruption")
            return real_write(path, payload, **kwargs)
        with mock.patch.object(migration, "atomic_write", side_effect=failing_write):
            with self.assertRaisesRegex(OSError, "simulated interruption"):
                migration.apply(self.root, out)
        self.assertEqual(migration.apply(self.root, out)["status"], "applied")
        self.assertEqual(migration.apply(self.root, out, batch_size=1, restore=True)["status"], "partial")
        migration.apply(self.root, out, restore=True)
        self.assertEqual(before, migration.snapshot(self.root))

    def test_restore_refuses_external_user_changes_and_wrong_root(self):
        entry = self.article()
        out = self.make_plan([entry])
        migration.apply(self.root, out)
        target = self.root / entry["path"]
        target.write_bytes(target.read_bytes() + b"User edit.\n")
        before = migration.snapshot(self.root)
        with self.assertRaisesRegex(migration.MigrationError, "changed_since_plan"):
            migration.apply(self.root, out, restore=True)
        self.assertEqual(before, migration.snapshot(self.root))
        other = self.base / "other"
        other.mkdir()
        with self.assertRaisesRegex(migration.MigrationError, "plan_root_or_schema_mismatch"):
            migration.apply(other, out, restore=True)

    def test_staged_backup_and_plan_tamper_are_rejected(self):
        entry = self.article()
        out = self.make_plan([entry])
        staged = out / "staged" / entry["path"]
        staged.write_bytes(staged.read_bytes() + b"tamper")
        with self.assertRaisesRegex(migration.MigrationError, "staged_hash_mismatch"):
            migration.apply(self.root, out)

    def test_unsafe_paths_and_in_repository_output_rejected(self):
        for relative in ("../escape.md", "/absolute", "C:/drive", "demo/../escape.md", "demo\\escape.md"):
            with self.assertRaises(migration.MigrationError):
                migration.safe_path(self.root, relative)
        entry = self.article()
        with self.assertRaisesRegex(migration.MigrationError, "outside_article_root"):
            migration.plan(self.root, self.base / "missing.json", self.root / "plan")

    def test_missing_link_fails_in_isolated_preflight(self):
        entry = self.article()
        entry["metadata"]["sources"] = [{"id": "s1", "ref": "./missing.md", "basis": "source-report"}]
        before = migration.snapshot(self.root)
        with self.assertRaisesRegex(migration.MigrationError, "projected_full_corpus_validation_failed"):
            self.make_plan([entry])
        self.assertEqual(before, migration.snapshot(self.root))

    def test_commonmark_code_headings_links_setext_and_unicode(self):
        text = ("Article title\n=============\n\n## Evidence\n\nBody.\n\n"
                "    # code heading\n    > source: code\n    [code](missing.md)\n\n"
                "`[inline](missing.md)`\n\n```markdown\n# fenced\n[link](missing.md)\n```\n\n"
                "- Item\n    - [Unicode](../中文/文章.md)\n\n[reference][r]\n\n[r]: ./target.md\n")
        self.assertEqual(kb.extract_title(text), "Article title")
        self.assertEqual(kb.extract_headings(text), ["Evidence"])
        self.assertFalse(kb.parse_metadata(text))
        links = list(kb.markdown_links(text))
        self.assertEqual(len(links), 2)
        self.assertIn("./target.md", links)
        self.assertIn("article-title", kb.document_anchors(text))
        with mock.patch.object(kb, "MarkdownIt", None):
            with self.assertRaisesRegex(RuntimeError, "markdown-it-py"):
                list(kb.markdown_links("# Title\n"))

    def test_ambiguous_array_syntax_is_not_a_broken_link_waiver(self):
        record = {"document_type": "archive", "path": "demo/source.md"}
        body = "# Source\n\nK[0..3](输入白化)\n\n[说明](missing)\n\n[x](./missing)\n\n[x](missing.md)\n\n[x](#missing)\n"
        ambiguous = kb.ambiguous_archive_links(self.root, record, body)
        self.assertEqual({kb.unquote(value) for value in ambiguous}, {"输入白化"})
        record["document_type"] = "reference"
        self.assertFalse(kb.ambiguous_archive_links(self.root, record, body))

    def test_archive_explicit_broken_links_and_directory_sources_remain_strict(self):
        entry = self.article()
        for target in ("missing", "./missing", "missing.md", "#missing"):
            raw = (self.root / entry["path"]).read_bytes() + (f"\n[x]({target})\n").encode("utf-8")
            transformed, _ = migration.transform(raw, entry)
            (self.root / entry["path"]).write_bytes(transformed)
            errors = kb.audit_knowledge(self.root, kb.build_records(self.root))
            self.assertTrue(errors, target)
            # Restore the explicit legacy fixture for the next trial.
            (self.root / entry["path"]).write_bytes(raw[:raw.rfind(b"\n[x](")])
        (self.root / "demo/subdir").mkdir()
        entry["metadata"]["sources"] = [{"id": "s1", "ref": "./subdir", "basis": "source-report"}]
        transformed, _ = migration.transform((self.root / entry["path"]).read_bytes(), entry)
        (self.root / entry["path"]).write_bytes(transformed)
        self.assertTrue(kb.audit_knowledge(self.root, kb.build_records(self.root)))


if __name__ == "__main__":
    unittest.main()
