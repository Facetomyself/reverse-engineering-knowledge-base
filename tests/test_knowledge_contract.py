from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_kb_catalog import kb_catalog as kb


class KnowledgeContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "demo").mkdir()
        self.index_entries = []
        self.write_index()

    def write_index(self):
        (self.root / "INDEX.md").write_text(
            "# Index\n\n" + "\n".join(f"- [{name}](./demo/{name}.md)" for name in self.index_entries) + "\n",
            encoding="utf-8", newline="\n")

    def metadata(self, name="fixture-reference", document_type="reference"):
        metadata = {
            "schema_version": 2, "id": name, "document_type": document_type,
            "scope": {"targets": ["fixture"], "client": "web", "version": "unknown", "observed_at": "2026-09"},
            "sources": [{"id": "s1", "ref": "https://example.org/research#parameters", "basis": "source-report"}],
            "tags": ["session"],
        }
        if document_type == "reference":
            metadata["modules"] = [{"name": "parameters", "anchor": "parameters", "sources": ["s1"], "basis": "source-report", "limits": "Source report only; no runtime reproduction."}]
        if document_type == "archive":
            metadata["source_completeness"] = "partial"
        return metadata

    def write(self, name="fixture-reference", metadata=None, body=None):
        if metadata is None:
            metadata = self.metadata(name)
        if body is None:
            body = f'# {name}\n\nFixture technical summary without claims of verification.\n\n<a id="parameters"></a>\n## Parameter material\n\nA source-bounded observation with limitations.\n'
        text = "---\n" + kb.yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True) + "---\n\n" + body
        path = self.root / "demo" / (name + ".md")
        path.write_text(text, encoding="utf-8", newline="\n")
        if name not in self.index_entries:
            self.index_entries.append(name)
            self.write_index()
        return path

    def audit(self):
        kb.generate(self.root)
        return kb.audit(self.root)

    def details(self):
        return "\n".join(str(item) for item in self.audit()["errors"])

    def test_v2_generate_deterministic_old_fields_and_module_query(self):
        path = self.write()
        before = path.read_bytes()
        first = kb.generate(self.root)
        payload = (self.root / "catalog.json").read_bytes()
        self.assertEqual(first, kb.generate(self.root))
        self.assertEqual(payload, (self.root / "catalog.json").read_bytes())
        self.assertEqual(before, path.read_bytes())
        record = kb.build_records(self.root)[0]
        self.assertEqual(record["kind"], "canonical")
        self.assertEqual(record["category"], "demo")
        self.assertEqual(record["title"], "fixture-reference")
        self.assertNotIn("schema_version", record["summary"])
        result = kb.query_records([record], target="FIXTURE", module="parameters", document_type="reference", client="web", version="unknown", observed_at="2026-09", tag="session", basis="source-report")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["results"][0]["anchor"], "parameters")
        self.assertEqual(result["results"][0]["sources"][0]["id"], "s1")
        self.assertTrue(self.audit()["ok"], self.audit())

    def test_query_filters_are_and_and_compact_cli(self):
        self.write()
        records = kb.build_records(self.root)
        for kwargs in ({"target": "other"}, {"module": "interfaces"}, {"document_type": "case"}, {"client": "app"}, {"basis": "local-parity"}, {"tag": "missing"}, {"version": "2"}, {"observed_at": "2026-10"}):
            self.assertEqual(kb.query_records(records, **kwargs)["count"], 0, kwargs)
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            result = kb.main(["--root", str(self.root), "query", "--target", "fixture", "--module", "parameters"])
        self.assertEqual(result, 0)
        self.assertEqual(stream.getvalue().count("\n"), 1)
        self.assertEqual(json.loads(stream.getvalue())["count"], 1)

    def test_archive_requires_completeness_not_modules(self):
        self.write("archive", self.metadata("archive", "archive"))
        self.assertTrue(self.audit()["ok"])
        hit = kb.query_records(kb.build_records(self.root), document_type="archive")["results"][0]
        self.assertIsNone(hit["module"])
        self.assertEqual(hit["basis"], "unknown")
        metadata = self.metadata("archive", "archive")
        del metadata["source_completeness"]
        self.write("archive", metadata)
        self.assertIn("archive_source_completeness_required", self.details())

    def test_mixed_legacy_and_v2_no_inferred_verification_or_mutation(self):
        self.write()
        legacy = self.root / "demo" / "legacy.md"
        legacy.write_bytes(b'\xef\xbb\xbf# Legacy\r\n\r\n> source: fixture\r\n> archive date: 2026-09-01\r\n> original date: 2020-01-01\r\n> category: demo\r\n\r\n## Detail\r\n\r\nHistorical source says verified.\r\n')
        self.index_entries.append("legacy")
        self.write_index()
        before = legacy.read_bytes()
        report = self.audit()
        self.assertTrue(report["ok"], report)
        self.assertEqual(legacy.read_bytes(), before)
        record = next(item for item in kb.build_records(self.root) if item["path"].endswith("legacy.md"))
        self.assertEqual(record["document_type"], "legacy")
        self.assertIsNone(record["id"])
        self.assertEqual(record["source"], "fixture")
        self.assertEqual(record["original_date"], "2020-01-01")
        self.assertEqual(record["scope"], {})
        self.assertEqual(kb.query_records([record])["results"][0]["basis"], "unknown")

    def test_invalid_fields_fail_without_crashing(self):
        changes = [{"schema_version": 1}, {"schema_version": True}, {"id": "Bad ID"}, {"scope": {}}, {"sources": []}, {"document_type": []}, {"verified": True}, {"modules": "bad"}, {"tags": [1]}, {"relations": [{"type": "wrong", "target": 2}]}]
        for change in changes:
            with self.subTest(change=change):
                metadata = self.metadata()
                metadata.update(change)
                self.write(metadata=metadata)
                self.assertIn("metadata_v2_invalid", self.details())

    def test_duplicate_yaml_keys_aliases_and_unsafe_tags_rejected(self):
        for yaml_text in ("id: first\nid: second\n", "a: &a [1]\nb: *a\n", "x: !!python/object:builtins.object {}\n", "[]\n", "!!set {x: null}\n"):
            metadata, body, errors = kb.split_frontmatter("---\n" + yaml_text + "---\n# Title\n")
            self.assertTrue(errors)
            self.assertEqual(body, "# Title\n")

    def test_dates_remain_strings_and_missing_yaml_is_actionable(self):
        metadata, _, errors = kb.split_frontmatter("---\nschema_version: 2\nobserved_at: 2026-09-30\n---\n# Title\n")
        self.assertFalse(errors)
        self.assertEqual(metadata["observed_at"], "2026-09-30")
        with mock.patch.object(kb, "yaml", None):
            self.assertIsNone(kb.split_frontmatter("# Legacy\n")[0])
            self.assertIn("PyYAML", kb.split_frontmatter("---\nid: sample\n---\n# Title\n")[2][0])

    def test_module_anchor_and_content_are_required(self):
        self.write(body="# Title\n\n## Other\n\nText.\n")
        self.assertIn("module_anchor_missing", self.details())
        self.write(body='# Title\n\n<a id="parameters"></a>\n## Parameters\n\n## Other\n\nOther text.\n')
        self.assertIn("module_empty", self.details())

    def test_code_fence_heading_does_not_create_anchor(self):
        anchors = kb.document_anchors('# Title\n\n```md\n## fake\n```\n\n## Real\n\nText\n')
        self.assertNotIn("fake", anchors)
        self.assertIn("real", anchors)
        self.write(body='# Title\n\n```markdown\n# An example, not another document title\n```\n\n<a id="parameters"></a>\n## Parameter material\n\nTechnical content.\n')
        self.assertTrue(self.audit()["ok"], self.audit())

    def test_module_section_includes_child_headings_but_not_peer_section(self):
        self.write(body='# Title\n\n<a id="parameters"></a>\n## Parameters\n\n### Signature\n\nSubsection evidence.\n\n## Other\n\nUnrelated.\n')
        self.assertTrue(self.audit()["ok"], self.audit())
        body = (self.root / "demo/fixture-reference.md").read_text(encoding="utf-8")
        section = kb.document_anchors(body)["parameters"]
        self.assertIn("Subsection evidence", section)
        self.assertNotIn("Unrelated", section)

    def test_nested_explicit_anchor_inherits_child_heading_level(self):
        self.write(body='# Title\n\n<a id="parameters"></a>\n## Parameters\n\n<a id="signature-detail"></a>\n### Signature\n\nSubsection evidence.\n\n## Other\n\nUnrelated.\n')
        self.assertTrue(self.audit()["ok"], self.audit())

    def test_only_child_headings_are_not_module_content(self):
        self.write(body='# Title\n\n<a id="parameters"></a>\n## Parameters\n\n### Signature\n\n<!-- Pending content is not evidence. -->\n')
        self.assertIn("module_empty", self.details())

    def test_fenced_examples_are_not_h1_or_metadata_for_all_fence_styles(self):
        for fence in ("```", "~~~", "````", "~~~~"):
            with self.subTest(fence=fence):
                shorter = fence[:3] if len(fence) > 3 else ("~~~" if fence[0] == "`" else "```")
                body = f'{fence}markdown\n# Example title\n{shorter}\n> source: example only\n## Fake heading\n{fence}\n\n# True title\n\n<a id="parameters"></a>\n## Parameter material\n\nSource-bounded text.\n'
                self.write(body=body)
                self.assertTrue(self.audit()["ok"], self.audit())
                record = kb.build_records(self.root)[0]
                self.assertEqual(record["title"], "True title")
                self.assertNotIn("Fake heading", record["headings"])
                self.assertNotIn("fake-heading", kb.document_anchors(body))

    def test_derived_from_requires_nonempty_decoded_fragment(self):
        self.write("source", self.metadata("source"))
        for ref in ("./source.md", "./source.md#", "./source.md#%20"):
            with self.subTest(ref=ref):
                metadata = self.metadata()
                metadata["relations"] = [{"type": "derived_from", "target": ref}]
                self.write(metadata=metadata)
                self.assertIn("derived_from_anchor_required", self.details())

    def test_public_source_url_rejects_whitespace_authority_errors_and_credentials(self):
        for ref in ("https://example.org/not a url", "https://example.org/a\tb", "https://", "https://user:password@example.org/path", "https://example.org:bad-port/path"):
            with self.subTest(ref=ref):
                metadata = self.metadata()
                metadata["sources"][0]["ref"] = ref
                self.write(metadata=metadata)
                self.assertIn("invalid_public_source_url", self.details())

    def test_procedure_all_sections_required(self):
        metadata = self.metadata("procedure", "procedure")
        self.write("procedure", metadata)
        self.assertIn("procedure_section_required", self.details())
        body = "# Procedure\n\n" + "\n".join(f'<a id="{anchor}"></a>\n## {anchor}\n\nConcrete action or criterion.\n' for anchor in sorted(kb.PROCEDURE_ANCHORS))
        self.write("procedure", metadata, body)
        self.assertTrue(self.audit()["ok"], self.audit())

    def test_duplicate_document_and_source_ids_are_errors(self):
        self.write("one", self.metadata("same-id"))
        self.write("two", self.metadata("same-id"))
        self.assertIn("duplicate_stable_id", self.details())
        metadata = self.metadata()
        metadata["sources"].append(copy.deepcopy(metadata["sources"][0]))
        self.write(metadata=metadata)
        self.assertIn("duplicate_source_id", self.details())

    def test_local_path_id_and_anchor_resolution(self):
        self.write("source", self.metadata("source"))
        metadata = self.metadata("derived")
        metadata["sources"][0]["ref"] = "kb:source#parameters"
        metadata["relations"] = [{"type": "derived_from", "target": "./source.md#parameters"}]
        self.write("derived", metadata)
        self.assertTrue(self.audit()["ok"], self.audit())
        metadata["sources"][0]["ref"] = "kb:source#missing"
        self.write("derived", metadata)
        self.assertIn("reference_anchor_missing", self.details())
        metadata["sources"][0]["ref"] = "kb:absent#parameters"
        self.write("derived", metadata)
        self.assertIn("reference_id_missing", self.details())

    def test_unsafe_local_sources_and_missing_links_fail(self):
        for pointer, code in (("../../outside.md", "reference_outside_repository"), ("C:/private/source.md", "reference_scheme_or_absolute_path_forbidden"), ("./missing.md", "reference_file_missing"), ("../INDEX.md", "knowledge_reference_requires_article")):
            metadata = self.metadata()
            metadata["sources"][0]["ref"] = pointer
            self.write(metadata=metadata)
            self.assertIn(code, self.details())

    def test_rooted_drive_unc_and_encoded_paths_are_not_portable_references(self):
        source = self.write("source", self.metadata("source"))
        rooted = source.as_posix()[2:] if source.drive else source.as_posix()
        for pointer in (rooted, rooted.replace("/", "%2f"), "C:source.md", "%43%3asource.md", "//server/share/source.md", r"\source.md", "%5csource.md"):
            for field in ("source", "relation"):
                with self.subTest(pointer=pointer, field=field):
                    metadata = self.metadata()
                    if field == "source":
                        metadata["sources"][0]["ref"] = pointer
                    else:
                        metadata["relations"] = [{"type": "supplements", "target": pointer}]
                    self.write(metadata=metadata)
                    self.assertIn("reference_scheme_or_absolute_path_forbidden", self.details())

    def test_local_body_anchor_is_checked_in_v2(self):
        self.write(body='# Title\n\n<a id="parameters"></a>\n## Parameter material\n\nText [bad](#absent).\n')
        self.assertIn("reference_anchor_missing", self.details())

    def test_source_report_and_unknown_cannot_upgrade_module(self):
        for basis in ("source-report", "unknown"):
            metadata = self.metadata()
            metadata["sources"][0]["basis"] = basis
            metadata["modules"][0]["basis"] = "local-parity"
            self.write(metadata=metadata)
            self.assertIn("module_basis_unsupported", self.details())
        self.write("source", self.metadata("source"))
        metadata = self.metadata()
        metadata["sources"][0].update(ref="kb:source#parameters", basis="local-parity")
        metadata["modules"][0]["basis"] = "local-parity"
        self.write(metadata=metadata)
        self.assertIn("source_basis_not_supported_by_target_module", self.details())

    def test_provenance_cycles_fail_but_supplement_cycles_allowed(self):
        one = self.metadata("one")
        two = self.metadata("two")
        one["sources"][0]["ref"] = "kb:two#parameters"
        two["sources"][0]["ref"] = "kb:one#parameters"
        self.write("one", one)
        self.write("two", two)
        self.assertIn("provenance_cycle", self.details())
        for metadata, target in ((one, "two"), (two, "one")):
            metadata["sources"][0]["ref"] = "https://example.org/article"
            metadata["relations"] = [{"type": "supplements", "target": f"kb:{target}#parameters"}]
            self.write(metadata["id"], metadata)
        self.assertTrue(self.audit()["ok"], self.audit())

    def test_frontmatter_is_single_authority_and_unclosed_is_invalid(self):
        self.write(body='# Title\n\n> source: conflicting old block\n\n<a id="parameters"></a>\n## Parameter material\n\nText.\n')
        self.assertIn("mixed_frontmatter_blockquote_metadata", self.details())
        self.assertIn("frontmatter_unclosed", kb.split_frontmatter("---\nid: one\n# Title")[2])

    def test_templates_and_docs_are_not_articles(self):
        self.write()
        for directory in ("templates", "docs"):
            (self.root / directory).mkdir()
            (self.root / directory / "sample.md").write_text("# Not an article\n", encoding="utf-8")
        self.assertEqual(len(kb.iter_article_paths(self.root)), 1)
        self.assertTrue(self.audit()["ok"])

    def test_query_refuses_invalid_metadata(self):
        self.write(metadata={"schema_version": 5})
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = kb.main(["--root", str(self.root), "query"])
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(stream.getvalue())["ok"])


if __name__ == "__main__":
    unittest.main()
