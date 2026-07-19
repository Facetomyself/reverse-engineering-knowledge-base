from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "kb_catalog.py"
SPEC = importlib.util.spec_from_file_location("kb_catalog", SCRIPT)
assert SPEC and SPEC.loader
kb_catalog = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = kb_catalog
SPEC.loader.exec_module(kb_catalog)


class KnowledgeBaseCatalogTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temp = Path(tempfile.mkdtemp())
        (temp / "demo" / "bundle").mkdir(parents=True)
        (temp / "INDEX.md").write_text(
            "# Index\n\n"
            "| 文章 | 来源项目 | 关键词 | 摘要 |\n"
            "|------|----------|--------|------|\n"
            "| [bundle.md](./demo/bundle.md) | demo | `trace`, `fixture` | demo summary |\n",
            encoding="utf-8",
            newline="\n",
        )
        (temp / "demo" / "bundle.md").write_text(
            "# Bundle\n\n"
            "> 来源: fixture\n"
            "> 原始发布时间: 2026-01-01\n"
            "> 归档日期: 2026-01-02\n"
            "> 分类: demo\n\n"
            "## Articles\n\n"
            "- [Child](bundle/child-20260101-01.md)\n",
            encoding="utf-8",
            newline="\n",
        )
        (temp / "demo" / "bundle" / "child-20260101-01.md").write_text(
            "# Child\n\n"
            "> 来源: fixture\n"
            "> 归档日期: 2026-01-02\n"
            "> 分类: demo\n\n"
            "## Detail\n\nUseful technical paragraph with enough content for summary extraction.\n",
            encoding="utf-8",
            newline="\n",
        )
        return temp

    def test_generate_is_deterministic_and_check_passes(self) -> None:
        root = self.make_repo()
        first = kb_catalog.generate(root)
        first_markdown = (root / "CATALOG.md").read_bytes()
        first_json = (root / "catalog.json").read_bytes()
        second = kb_catalog.generate(root)
        self.assertEqual(first, second)
        self.assertEqual(first_markdown, (root / "CATALOG.md").read_bytes())
        self.assertEqual(first_json, (root / "catalog.json").read_bytes())
        payload = json.loads(first_json.decode("utf-8"))
        self.assertEqual(payload["article_count"], 2)
        self.assertTrue(kb_catalog.audit(root)["ok"])

    def test_sanitize_truncates_high_confidence_tail(self) -> None:
        root = self.make_repo()
        child = root / "demo" / "bundle" / "child-20260101-01.md"
        child.write_text(
            child.read_text(encoding="utf-8")
            + "\n下边是广告环节\n\n小肩膀教育安全逆向教学\n关注该公众号\n",
            encoding="utf-8",
            newline="\n",
        )
        dry_run = kb_catalog.sanitize(root, apply=False)
        self.assertEqual(dry_run["changed_count"], 1)
        self.assertIn("广告环节", child.read_text(encoding="utf-8"))
        applied = kb_catalog.sanitize(root, apply=True)
        self.assertEqual(applied["changed_count"], 1)
        cleaned = child.read_text(encoding="utf-8")
        self.assertNotIn("广告环节", cleaned)
        self.assertIn("Useful technical paragraph", cleaned)

    def test_missing_canonical_metadata_is_an_error(self) -> None:
        root = self.make_repo()
        canonical = root / "demo" / "bundle.md"
        canonical.write_text("# Bundle\n\n- [Child](bundle/child-20260101-01.md)\n", encoding="utf-8", newline="\n")
        kb_catalog.generate(root)
        report = kb_catalog.audit(root)
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("canonical_metadata_missing", codes)

    def test_descriptive_category_metadata_matches_directory(self) -> None:
        self.assertTrue(
            kb_catalog.category_metadata_matches(
                "反检测/风控对抗 — 浏览器源码级指纹伪装",
                "anti-detection",
            )
        )
        self.assertTrue(
            kb_catalog.category_metadata_matches(
                "移动 App 逆向 — 环境搭建",
                "mobile-app-reverse",
            )
        )
        self.assertFalse(kb_catalog.category_metadata_matches("协议分析", "anti-detection"))

    def test_root_catalog_link_is_not_treated_as_canonical(self) -> None:
        root = self.make_repo()
        index = root / "INDEX.md"
        index.write_text(
            index.read_text(encoding="utf-8") + "\n[Detailed catalog](./CATALOG.md)\n",
            encoding="utf-8",
            newline="\n",
        )
        kb_catalog.generate(root)
        report = kb_catalog.audit(root)
        self.assertTrue(report["ok"], report["errors"])

    def test_repeated_training_pitch_is_high_confidence_tail(self) -> None:
        marker = "国内最早和系统完整的浏览器内核培训教程"
        self.assertEqual(kb_catalog.marker_name(f"{marker}，欢迎咨询。"), marker)


if __name__ == "__main__":
    unittest.main()
