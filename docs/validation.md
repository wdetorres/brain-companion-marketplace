# Package validation

Checked November 2, 2026 with Python 3, Claude Code 2.1.301 and Codex CLI 0.162.1.

## Automated checks

```sh
python3 -m unittest discover -s tests -v
python3 scripts/configure.py --mcp-url https://brain.example.invalid/mcp --output dist/preview
claude plugin validate --strict .
claude plugin validate --strict plugins/brain-workflows
claude plugin validate --strict dist/preview
claude plugin validate --strict dist/preview/plugins/brain-companion
```

Three tests passed: complete source snapshot and hashes; exact exported contents, endpoint settings and non-overwrite behavior; malformed/credential-bearing/interpolated endpoint rejection. Both catalogs and both plugin manifests passed Claude's strict validator. The synthetic `.invalid` endpoint cannot reach a real Brain.

## Native discovery

Claude's `plugin details` and Codex's app-server `plugin/list`/`plugin/read` confirmed these inventories in this repository. Both Codex entries remained uninstalled and disabled:

| Catalog | Skills | MCP servers | Hooks |
|---|---:|---:|---:|
| Public repository, `brain-workflows` | 4 | 0 | 0 |
| Generated local catalog, `brain-companion` | 4 | 1 | 0 |

For Claude, inspect with `claude --plugin-dir ./plugins/brain-workflows plugin details brain-workflows` and the equivalent command for `./dist/preview/plugins/brain-companion`.

For Codex, use the app-server's `plugin/list` with the catalog's absolute working directory in `cwds`, followed by `plugin/read` with the returned marketplace path and plugin name. Do not install the plugin just to inspect it. The ordinary CLI plugin list does not discover these unregistered repo catalogs without explicit working-directory discovery.

The initial packaging experiment found that adding the newer portable root `plugin.json`/`mcp.json` layout made this installed Codex inspector report zero MCP servers. The compatibility manifest with an explicit `mcpServers` path reported the configured server. This package retains the verified compatibility format; revisit the newer format after target-client checks pass.

OAuth, authenticated tool calls, Grok Build, ChatGPT/Claude Chat import and hosted writes are not established by package discovery. No client installation or hook registration is part of these checks.
