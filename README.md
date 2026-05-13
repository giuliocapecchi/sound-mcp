# sound-mcp

<p align="center">
  <img src="assets/banner.png" alt="sound-mcp banner" width="600">
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-%E2%89%A5%203.11-3776AB?logo=python&logoColor=white" alt="Python"></a>
  <a href="#requirements"><img src="https://img.shields.io/badge/platform-linux-555?logo=linux&logoColor=white" alt="Platform"></a>
  <a href="#license"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

A small [FastMCP](https://github.com/PrefectHQ/fastmcp) server that lets the agent
play a notification sound, and optionally pop a desktop toast, when something
finishes. Useful for *"poll X until Y, then ping me"* workflows.

## Tools

- `list_sounds()`: show every available sound name and the current default.
- `play_sound(name=None)`: play a registered sound, an absolute file path, or the default.
- `notify(message, title="Claude", sound=None, urgency="normal", expire_ms=0)`: desktop toast + sound. `urgency=critical`: makes the toast sticky on most desktops.

## Requirements

Linux with `paplay` (PulseAudio/PipeWire) and `notify-send` (`libnotify-bin`).
Builtin sounds come from `sound-theme-freedesktop`, preinstalled on Ubuntu.
You only need `uv` and Python ≥ 3.11.

## Quick start

### Claude Code

```bash
claude mcp add sound-mcp -- uvx --from git+https://github.com/giuliocapecchi/sound-mcp sound-mcp
```

### Other MCP clients (Claude Desktop, Codex, OpenCode, …)

Add this block to your client's MCP config file:

```json
{
  "mcpServers": {
    "sound-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/giuliocapecchi/sound-mcp", "sound-mcp"]
    }
  }
}
```

Common config locations:

| Client          | Config file                  |
| --------------- | ---------------------------- |
| Claude Desktop  | `claude_desktop_config.json` |
| Codex (OpenAI)  | `~/.codex/config.json`       |
| OpenCode        | `opencode.json`              |

## Configuration

All settings are read from environment variables, so you set them in the `env`
block of your `mcp.json` (or equivalent):

```json
{
  "mcpServers": {
    "sound-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/giuliocapecchi/sound-mcp", "sound-mcp"],
      "env": {
        "SOUND_MCP_DEFAULT": "warning",
        "SOUND_MCP_SOUNDS_DIR": "/home/you/.config/sound-mcp/sounds"
      }
    }
  }
}
```

| Variable               | Default                            | Purpose                                                       |
| ---------------------- | ---------------------------------- | ------------------------------------------------------------- |
| `SOUND_MCP_DEFAULT`    | `warning`                          | Sound played when `play_sound`/`notify` is called with no name. |
| `SOUND_MCP_SOUNDS_DIR` | `~/.config/sound-mcp/sounds`       | Directory scanned for user sound files.                       |

### Custom sounds

Builtin names: `complete`, `bell`, `warning`, `error`, `alarm`.

Drop audio files (`.oga`, `.ogg`, `.wav`, `.mp3`, `.flac`) into your sounds
directory and each becomes a sound keyed by its filename stem. For example
`tada.wav` → `play_sound("tada")`. User files override builtins on name collision.

You can also pass an absolute path directly: `play_sound("/tmp/horn.wav")`.

## Example prompt

> Poll `tailscale status` every 10 seconds. When node `myserver` shows as online,
> call the `notify` tool with `title="Tailscale"` and `message="myserver is back"`.

## Local development

```bash
git clone https://github.com/giuliocapecchi/sound-mcp
cd sound-mcp
uv venv && uv pip install -e .
uv run fastmcp dev src/sound_mcp/server.py   # opens MCP Inspector
```

## License

MIT.
