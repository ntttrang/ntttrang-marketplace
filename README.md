# ntttrang-marketplace

My personal Claude Code plugin marketplace — a collection of skills, agents, hooks, and MCP servers.

## Plugins

| Plugin | Description |
|--------|-------------|
| [drawio-tools](./plugins/drawio-tools) | Understand and explain existing diagrams — `.drawio`/XML, exported SVG, or images (screenshots, whiteboard photos, hand-drawn sketches) of flowcharts, architecture, ERD, sequence, and org charts. Delivers a plain-language summary, a full node/edge inventory, a step-by-step walkthrough, and a Mermaid recreation |

## Install

This marketplace lives in a **private GitHub repo**. You need GitHub access to it (Claude Code uses your existing GitHub authentication).

```text
/plugin marketplace add ntttrang/ntttrang-marketplace
```

Then install a plugin:

```text
/plugin install drawio-tools@ntttrang-marketplace
```

Or interactively: `/plugin` → Browse marketplaces → `ntttrang-marketplace`.

After pulling new plugins or versions to this repo, refresh with:

```text
/plugin marketplace update ntttrang-marketplace
```

## Adding a new plugin

1. Create the plugin directory: `plugins/<plugin-name>/` with its own `.claude-plugin/plugin.json` and components (`skills/`, `agents/`, `hooks/`, …). See the [plugin docs](https://code.claude.com/docs/en/plugins).
2. Add an entry to [`plugins`](./.claude-plugin/marketplace.json) in `.claude-plugin/marketplace.json`:

   ```json
   {
     "name": "<plugin-name>",
     "source": "./plugins/<plugin-name>",
     "description": "What it does",
     "version": "0.1.0"
   }
   ```

3. Add a row to the plugin table above, commit, and push. Installed users get it on `/plugin marketplace update`.
