import os
import shutil
import subprocess
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("sound-mcp")

BUILTIN_DIR = Path("/usr/share/sounds/freedesktop/stereo")
BUILTIN_SOUNDS = {
    "complete": BUILTIN_DIR / "complete.oga",
    "bell": BUILTIN_DIR / "bell.oga",
    "warning": BUILTIN_DIR / "dialog-warning.oga",
    "error": BUILTIN_DIR / "dialog-error.oga",
    "alarm": BUILTIN_DIR / "alarm-clock-elapsed.oga",
}

# User-configurable sounds: drop any audio file (.oga/.ogg/.wav/.mp3/.flac) into
# the dir pointed to by $SOUND_MCP_SOUNDS_DIR (default: ~/.config/sound-mcp/sounds)
# and it becomes available by its filename stem.
AUDIO_EXTS = {".oga", ".ogg", ".wav", ".mp3", ".flac"}
USER_DIR = Path(
    os.environ.get("SOUND_MCP_SOUNDS_DIR")
    or Path.home() / ".config" / "sound-mcp" / "sounds"
)
DEFAULT_SOUND = os.environ.get("SOUND_MCP_DEFAULT", "warning")


def _load_sounds() -> dict[str, Path]:
    sounds = {k: v for k, v in BUILTIN_SOUNDS.items() if v.exists()}
    if USER_DIR.is_dir():
        # User entries win on name collision.
        for f in USER_DIR.iterdir():
            if f.is_file() and f.suffix.lower() in AUDIO_EXTS:
                sounds[f.stem] = f
    return sounds


def _resolve(name: str) -> Path | None:
    # Accept absolute / ~-expanded paths directly.
    if "/" in name or name.startswith("~"):
        p = Path(name).expanduser()
        return p if p.is_file() else None
    return _load_sounds().get(name)


@mcp.tool
def list_sounds() -> dict:
    """List every sound name the user can pick from, plus the current default."""
    sounds = _load_sounds()
    return {
        "default": DEFAULT_SOUND,
        "available": sorted(sounds.keys()),
        "user_dir": str(USER_DIR),
        "user_dir_exists": USER_DIR.is_dir(),
    }


@mcp.tool
def play_sound(name: str | None = None) -> str:
    """Play a notification sound.

    `name` can be a registered sound (see list_sounds) or an absolute path to
    an audio file. If omitted, plays the configured default.
    """
    chosen = name or DEFAULT_SOUND
    path = _resolve(chosen)
    if path is None:
        return f"unknown sound '{chosen}'. try list_sounds() to see options."
    paplay = shutil.which("paplay") or "/usr/bin/paplay"
    subprocess.Popen(
        [paplay, str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return f"played {chosen} ({path})"


@mcp.tool
def notify(
    message: str,
    title: str = "Claude",
    sound: str | None = None,
    urgency: str = "normal",
    expire_ms: int = 0,
) -> str:
    """Show a desktop notification AND play a sound.

    urgency: low | normal | critical (critical toasts are sticky on most desktops).
    expire_ms: notification timeout in ms; 0 = desktop default.
    """
    play_sound(sound)
    ns = shutil.which("notify-send")
    if not ns:
        return "sound played, but notify-send is not installed"
    cmd = [ns, "-u", urgency, "-a", "sound-mcp"]
    if expire_ms > 0:
        cmd += ["-t", str(expire_ms)]
    cmd += [title, message]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return f"sound played, but notify-send failed: {result.stderr.strip()}"
    return f"notified ({urgency}): {title} — {message}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
