# Package validation

Checked November 2, 2026 with Python 3, Claude Code 2.1.301 and Codex CLI 0.162.1.

## Automated checks

```sh
python3 -m unittest discover -s tests -v
python3 scripts/configure.py --mcp-url https://brain.example.invalid/mcp --output dist/hosted-preview
claude plugin validate --strict .
claude plugin validate --strict plugins/brain-workflows
claude plugin validate --strict dist/hosted-preview
claude plugin validate --strict dist/hosted-preview/plugins/brain-companion
```

Three tests passed covering the source snapshot and hosted MCP configuration; exact custom-bundle contents, endpoint override and non-overwrite behavior; malformed/credential-bearing/interpolated endpoint rejection. Both catalogs and manifests passed Claude's strict validator. Custom bundles contain only their supplied endpoint, without the hosted default. The synthetic `.invalid` endpoint cannot reach a real Brain.

## Native discovery

Claude's `plugin details` and Codex's app-server `plugin/list`/`plugin/read` confirmed these inventories in this repository. Both Codex entries remained uninstalled and disabled:

| Catalog | Skills | MCP servers | Hooks |
|---|---:|---:|---:|
| Public repository, `brain-workflows` 0.2.0 | 4 | 1 | 0 |
| Generated local catalog, `brain-companion` | 4 | 1 | 0 |

For Claude, inspect with `claude --plugin-dir ./plugins/brain-workflows plugin details brain-workflows` and the equivalent command for `./dist/hosted-preview/plugins/brain-companion`.

For Codex, use the app-server's `plugin/list` with the catalog's absolute working directory in `cwds`, followed by `plugin/read` with the returned marketplace path and plugin name. Do not install the plugin just to inspect it. The ordinary CLI plugin list does not discover these unregistered repo catalogs without explicit working-directory discovery.

The initial packaging experiment found that adding the newer portable root `plugin.json`/`mcp.json` layout made this installed Codex inspector report zero MCP servers. The compatibility manifest with an explicit `mcpServers` path reported the configured server. This package retains the verified compatibility format; revisit the newer format after target-client checks pass.

The hosted `/mcp` returned `401` without credentials and an OAuth resource-metadata challenge. Resource discovery returned `200`, identified `https://brain.wilsondetorres.com/mcp` and its `/api/auth` authorization server, and advertised the `brain` scope. Source inspection at application commit `f3a8f1c` still shows one pinned Google owner and one vault; packaging does not change that model.

Owner sign-in, consent, authenticated tool calls, Grok Build, ChatGPT/Claude Chat import and hosted writes are not established by package discovery. No client installation or hook registration is part of these checks.
