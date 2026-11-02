"""Build a local marketplace containing four skills and your HTTPS MCP endpoint."""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("brain-recall", "brain-capture", "brain-review", "brain-maintain")
FILES = tuple(f"skills/{name}/{file}" for name in SKILLS for file in ("SKILL.md", "agents/openai.yaml")) + (
    "skills/brain-capture/references/write-outcomes.md",
    "skills/brain-review/references/review-actions.md",
)
ASSETS = ("assets/logo.png",)


def endpoint(value: str) -> str:
    try:
        url = urlsplit(value)
        valid = (
            url.scheme == "https" and re.fullmatch(r"[A-Za-z0-9.:-]+", url.hostname or "")
            and url.port != 0 and url.username is None and url.password is None
            and not any(c.isspace() or ord(c) < 32 or ord(c) == 127 or c in "\\$?#" for c in value)
        )
    except ValueError:
        valid = False
    if not valid:
        raise argparse.ArgumentTypeError("Use a literal HTTPS MCP URL without credentials, query, fragment or variables")
    return value


def build(output: Path, mcp_url: str) -> None:
    mcp_url = endpoint(mcp_url)
    if output.exists() or output.is_symlink():
        raise FileExistsError("Choose a new output directory; existing packages are never overwritten")
    source = ROOT / "plugins/brain-workflows"
    manifest = json.loads((source / ".claude-plugin/plugin.json").read_text())
    if set(manifest) != {"name", "version", "author", "description", "mcpServers", "icon"} or manifest["name"] != "brain-workflows" or manifest["mcpServers"] != "./.mcp.json" or manifest["icon"] != "./assets/logo.png":
        raise ValueError("Review changed plugin metadata before exporting it")
    codex = json.loads((source / ".codex-plugin/plugin.json").read_text())
    if {k: v for k, v in codex.items() if k != "interface"} != {k: v for k, v in manifest.items() if k != "icon"}:
        raise ValueError("Codex and Claude plugin metadata must agree")
    plugin = "plugins/brain-companion"
    entries = {}
    for name in FILES + ASSETS:
        path = source / name
        if path.is_symlink() or path.resolve() != path or not path.is_file():
            raise ValueError(f"Expected a regular package file: {name}")
        entries[f"{plugin}/{name}"] = path.read_bytes()

    custom_manifest = {
        **manifest, "name": "brain-companion", "mcpServers": "./.mcp.json",
        "description": "Four Brain workflows with your owner-authorized Brain Companion MCP connection.",
    }
    # shortcut: keep compatibility manifests until portable MCP discovery passes in target clients.
    configs = {
        f"{plugin}/.claude-plugin/plugin.json": custom_manifest,
        f"{plugin}/.codex-plugin/plugin.json": {
            **{k: v for k, v in custom_manifest.items() if k != "icon"},
            "interface": codex["interface"],
        },
        f"{plugin}/.mcp.json": {"mcpServers": {"brain-companion": {"type": "http", "url": mcp_url}}},
        ".claude-plugin/marketplace.json": {
            "name": "brain-companion-local", "owner": manifest["author"],
            "description": "Brain workflows with an owner-supplied MCP endpoint.",
            "plugins": [{"name": "brain-companion", "source": f"./{plugin}"}],
        },
        ".agents/plugins/marketplace.json": {
            "name": "brain-companion-local",
            "plugins": [{
                "name": "brain-companion", "source": {"source": "local", "path": f"./{plugin}"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Productivity",
            }],
        },
    }
    entries.update({name: (json.dumps(value, indent=2) + "\n").encode() for name, value in configs.items()})
    output.mkdir(parents=True)
    for name, content in sorted(entries.items()):
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as file:
            file.write(content)
        if path.read_bytes() != content:
            raise OSError(f"Package readback failed: {name}")
    print(output.resolve())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-url", required=True, type=endpoint, help="Your deployed Brain endpoint; no default")
    parser.add_argument("--output", required=True, type=Path, help="A new local marketplace directory")
    args = parser.parse_args()
    build(args.output, args.mcp_url)
