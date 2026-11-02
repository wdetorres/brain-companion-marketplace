# Package validation

Checked November 2, 2026 with Python 3, Claude Code 2.1.301 and Codex CLI 0.162.1.

## Automated checks

```sh
python3 -m unittest discover -s tests -v
python3 scripts/configure.py --mcp-url https://brain.example.invalid/mcp --output dist/logo-preview-021
claude plugin validate --strict .
claude plugin validate --strict plugins/brain-workflows
claude plugin validate --strict dist/logo-preview-021
claude plugin validate --strict dist/logo-preview-021/plugins/brain-companion
```

Three tests passed covering the unchanged skill snapshot and hosted MCP configuration; exact custom-bundle contents, endpoint override and non-overwrite behavior; malformed/credential-bearing/interpolated endpoint rejection. The checks also verify agreement between client manifests, logo paths, a square PNG and byte-identical assets in the custom bundle. Both catalogs and Claude manifests passed Claude's strict validator. Custom bundles contain only their supplied endpoint, without the hosted default. The synthetic `.invalid` endpoint cannot reach a real Brain.

## Native discovery

Claude's `plugin details` and Codex's app-server `plugin/read` confirmed these inventories in the 0.2.1 source packages. The generated custom catalog was not installed:

| Catalog | Skills | MCP servers | Hooks |
|---|---:|---:|---:|
| Public repository, `brain-workflows` 0.2.1 | 4 | 1 | 0 |
| Generated local catalog, `brain-companion` | 4 | 1 | 0 |

For Claude, inspect with `claude --plugin-dir ./plugins/brain-workflows plugin details brain-workflows` and the equivalent command for `./dist/logo-preview-021/plugins/brain-companion`.

For Codex, use the app-server's `plugin/list` with the catalog's absolute working directory in `cwds`, followed by `plugin/read` with the returned marketplace path and plugin name. Do not install the plugin just to inspect it. The ordinary CLI plugin list does not discover these unregistered repo catalogs without explicit working-directory discovery.

The initial packaging experiment found that adding the newer portable root `plugin.json`/`mcp.json` layout made this installed Codex inspector report zero MCP servers. The compatibility manifests retain an explicit `mcpServers` path. The 0.2.1 Codex manifest adds presentation metadata; native discovery resolves both `logo` and `composerIcon` to the bundled PNG while preserving all four skills and the MCP server. Revisit the newer portable format after target-client checks pass.

The hosted `/mcp` returned `401` without credentials and an OAuth resource-metadata challenge. Resource discovery returned `200`, identified `https://brain.wilsondetorres.com/mcp` and its `/api/auth` authorization server, and advertised the `brain` scope. Source inspection at application commit `f3a8f1c` still shows one pinned Google owner and one vault; packaging does not change that model.

Owner sign-in, consent, authenticated tool calls, Grok Build, ChatGPT/Claude Chat import and hosted writes are not established by package discovery. No hook registration is part of these checks.

## Logo

`plugins/brain-workflows/assets/logo.png` was generated with the built-in image-generation tool and copied unchanged into the package. It is a 1254×1254 PNG with alpha. The README, Claude listing metadata and Codex presentation metadata share this asset. No application-server branding or OAuth behavior changes are included.

Claude's current [manifest reference](https://code.claude.com/docs/en/plugins-reference#directory-listing-fields) says `icon` is directory-listing metadata, ignored by Claude Code at load time. This repository supplies the supported field without claiming that every Claude surface displays it.

<details>
<summary>Generation prompt</summary>

Use case: logo-brand. Create ONE finished, premium app icon for Brain Companion, a personal second brain that links memories and knowledge. This is an actual small marketplace/plugin icon, not a mockup or presentation. Square 1024x1024 canvas. A charcoal (#191919) rounded-square tile with a generous corner radius, nearly filling the canvas, transparent outside its rounded corners. Center one original off-white (#F6F4EE) abstract brain / connected-memory symbol: two elegantly balanced rounded brain lobes formed from a few bold continuous paths, with two or three integrated circular connection nodes. The silhouette must feel warm, clear and memorable, not medical or mechanical. Subtle negative-space connection between the halves communicates a companion and linked memories. Simple confident geometry, thick even strokes, optical balance, ample interior breathing room, instantly legible at 32px. Existing product identity is monochrome with a charcoal tile and connected circular nodes; build on that visual language. Perfectly flat 2D vector-like artwork, crisp edges. No words, no letters, no text, no tiny details, no sparkles, no gradients, no shadows, no glow, no 3D, no ornamental border. Show only the one icon.

</details>
