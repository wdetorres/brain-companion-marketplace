import argparse
import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.configure import FILES, ROOT, build


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.output = Path(self.temporary.name) / "marketplace"

    def build(self, url="https://brain.example.invalid/mcp"):
        with contextlib.redirect_stdout(io.StringIO()):
            build(self.output, url)

    def test_bundle_preserves_skills_and_configures_only_explicit_endpoint(self):
        self.build()
        plugin = "plugins/brain-companion"
        expected = {f"{plugin}/{name}" for name in FILES} | {
            f"{plugin}/.claude-plugin/plugin.json", f"{plugin}/.mcp.json",
            ".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json",
        }
        actual = {path.relative_to(self.output).as_posix() for path in self.output.rglob("*") if path.is_file()}
        self.assertEqual(actual, expected)
        for name in FILES:
            self.assertEqual((self.output / plugin / name).read_bytes(), (ROOT / "plugins/brain-workflows" / name).read_bytes())
        manifest = json.loads((self.output / plugin / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(set(manifest), {"name", "version", "author", "description", "mcpServers"})
        self.assertEqual(manifest["mcpServers"], "./.mcp.json")
        self.assertEqual(json.loads((self.output / plugin / ".mcp.json").read_text()), {
            "mcpServers": {"brain-companion": {"type": "http", "url": "https://brain.example.invalid/mcp"}},
        })
        for root, name, target in [(ROOT, "brain-workflows", "plugins/brain-workflows"), (self.output, "brain-companion", plugin)]:
            claude = json.loads((root / ".claude-plugin/marketplace.json").read_text())
            codex = json.loads((root / ".agents/plugins/marketplace.json").read_text())
            self.assertEqual(claude["name"], codex["name"])
            self.assertEqual(claude["plugins"], [{"name": name, "source": f"./{target}"}])
            self.assertEqual(codex["plugins"][0]["source"], {"source": "local", "path": f"./{target}"})
            self.assertEqual(codex["plugins"][0]["policy"], {"installation": "AVAILABLE", "authentication": "ON_INSTALL"})
        before = {name: (self.output / name).read_bytes() for name in expected}
        with self.assertRaises(FileExistsError):
            self.build("https://another.example.invalid/mcp")
        self.assertEqual(before, {name: (self.output / name).read_bytes() for name in expected})

    def test_invalid_endpoints_do_not_create_output(self):
        for url in ("", "http://brain.invalid/mcp", "https:///mcp", "https://user:secret@brain.invalid/mcp",
                    "https://brain.invalid/mcp?token=secret", "https://brain.invalid/mcp#secret",
                    "https://brain.invalid:bad/mcp", "https://brain.invalid:0/mcp", "https://brain.invalid:99999/mcp",
                    "https://brain.invalid/\nmcp", "https://brain.invalid/\\mcp", "https://${BRAIN_HOST}/mcp",
                    "https://bad%20host/mcp", "https://brain.invalid/\x7fmcp"):
            with self.subTest(url=url), self.assertRaises(argparse.ArgumentTypeError):
                self.build(url)
            self.assertFalse(self.output.exists())
        result = subprocess.run([sys.executable, str(ROOT / "scripts/configure.py"), "--output", str(self.output)], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())

    def test_source_snapshot_is_complete_and_has_no_personal_configuration(self):
        source = json.loads((ROOT / "source.json").read_text())
        self.assertEqual(set(source["files"]), set(FILES))
        directory = ROOT / "plugins/brain-workflows"
        self.assertEqual({p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}, set(FILES) | {".claude-plugin/plugin.json"})
        for name, digest in source["files"].items():
            content = (directory / name).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), digest)
            self.assertNotRegex(content.decode(), r"/Users/|/home/box|wilsondetorres|brain-harness|Bearer |AUTO_ACCEPT")
        self.assertEqual(set(json.loads((directory / ".claude-plugin/plugin.json").read_text())), {"name", "version", "author", "description"})


if __name__ == "__main__":
    unittest.main()
