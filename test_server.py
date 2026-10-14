"""Behavior and security regression tests using synthetic, temporary documents."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import server


class KnowledgeToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "knowledge"
        self.root.mkdir()
        self.outside = Path(self.temp.name) / "private.txt"
        self.outside.write_text("PRIVATE SENTINEL", encoding="utf-8")
        (self.root / "equipment.md").write_text("Pump maintenance", encoding="utf-8")
        (self.root / "irrigation.txt").write_text("Irrigation café", encoding="utf-8")
        self.directory = patch.object(server, "KNOWLEDGE_DIR", self.root)
        self.directory.start()
        self.addCleanup(self.directory.stop)

    def test_lists_documents_in_stable_order(self):
        self.assertEqual(server.list_documents(), "equipment.md\nirrigation.txt")

    def test_reads_utf8_document(self):
        self.assertEqual(server.get_document("irrigation.txt"), "Irrigation café")

    def test_search_is_case_insensitive(self):
        self.assertEqual(
            server.search_knowledge("IRRIGATION"),
            "--- irrigation.txt ---\nIrrigation café",
        )

    def test_search_returns_all_matches_in_order(self):
        (self.root / "a.md").write_text("Pump guide", encoding="utf-8")
        self.assertEqual(
            server.search_knowledge("pump"),
            "--- a.md ---\nPump guide\n\n--- equipment.md ---\nPump maintenance",
        )

    def test_no_matches(self):
        self.assertEqual(server.search_knowledge("missing"), "No results found for: missing")

    def test_empty_query_does_not_dump_documents(self):
        for query in ("", " ", "\n\t"):
            with self.subTest(query=query):
                self.assertEqual(server.search_knowledge(query), "Please provide a non-empty search query.")

    def test_rejects_paths_and_invalid_names(self):
        for name in (
            "../private.txt", str(self.outside), "sub/../equipment.md",
            "sub/equipment.md", "..\\private.txt", "C:\\private.txt",
            "", ".hidden.md", "equipment.md\x00", "missing.md", "server.py",
        ):
            with self.subTest(name=name):
                self.assertEqual(server.get_document(name), "Document not found or filename not allowed.")

    def test_ignores_hidden_binary_and_directory_entries(self):
        (self.root / ".hidden.md").write_text("PRIVATE SENTINEL", encoding="utf-8")
        (self.root / "archive.pdf").write_bytes(b"PRIVATE SENTINEL")
        (self.root / "folder.md").mkdir()
        self.assertEqual(server.list_documents(), "equipment.md\nirrigation.txt")
        self.assertEqual(server.search_knowledge("PRIVATE SENTINEL"), "No results found for: PRIVATE SENTINEL")

    def test_symlinks_never_expose_outside_or_inside_documents(self):
        for name, target in (("outside.md", self.outside), ("inside.md", self.root / "equipment.md"), ("broken.md", self.root / "missing.md")):
            (self.root / name).symlink_to(target)
            self.assertEqual(server.get_document(name), "Document not found or filename not allowed.")
        self.assertEqual(server.list_documents(), "equipment.md\nirrigation.txt")
        self.assertEqual(server.search_knowledge("PRIVATE SENTINEL"), "No results found for: PRIVATE SENTINEL")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO test requires POSIX")
    def test_ignores_non_regular_files(self):
        os.mkfifo(self.root / "pipe.txt")
        self.assertEqual(server.get_document("pipe.txt"), "Document not found or filename not allowed.")
        self.assertEqual(server.list_documents(), "equipment.md\nirrigation.txt")

    def test_unreadable_utf8_does_not_break_search(self):
        (self.root / "bad.md").write_bytes(b"\xff\xfe")
        self.assertEqual(server.get_document("bad.md"), "Document could not be read as UTF-8 text.")
        self.assertIn("Pump maintenance", server.search_knowledge("pump"))

    def test_permission_errors_return_safe_response(self):
        with patch.object(Path, "read_text", side_effect=PermissionError("sensitive path")):
            self.assertEqual(server.get_document("equipment.md"), "Document could not be read as UTF-8 text.")
            self.assertEqual(server.search_knowledge("pump"), "No results found for: pump")

    def test_missing_directory(self):
        with patch.object(server, "KNOWLEDGE_DIR", self.root / "missing"):
            self.assertEqual(server.list_documents(), "")
            self.assertEqual(server.search_knowledge("pump"), "No results found for: pump")
            self.assertEqual(server.get_document("equipment.md"), "Document not found or filename not allowed.")

    def test_empty_directory(self):
        empty = self.root / "empty"
        empty.mkdir()
        with patch.object(server, "KNOWLEDGE_DIR", empty):
            self.assertEqual(server.list_documents(), "")


if __name__ == "__main__":
    unittest.main()
