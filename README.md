# Spike Planting 💣

> 🌐 [Versión en Español](README.es.md)

A global countdown timer overlay for Valorant. Hold `4` for 2 seconds to start a 45-second countdown — works even while in-game.

## Features

- Hold `4` for 2 seconds to trigger the countdown
- Always-on-top overlay — works over Valorant, Chrome, anything
- Remembers position between sessions (drag to move)
- Does **not** steal focus or minimize your game
- Optional: add your own video above the counter

## Controls

| Key | Action |
|-----|--------|
| Hold `4` (2s) | Start countdown |
| `Ctrl+Q` | Hide overlay |
| `Ctrl+Shift+Q` | Exit app |

## Requirements

- Python 3.x

```
pip install keyboard
```

> Optional (only if you want a video above the counter):
> ```
> pip install opencv-python Pillow
> ```

## Usage

Run as **Administrator** (required for global keyboard hook):

```
iniciar.bat
```

Or manually:

```
python countdown.py
```

> **Note:** Valorant must be in **Borderless Windowed** mode for the overlay to appear on top.

## Configuration

Edit the top of `countdown.py` to customize:

```python
TOTAL_SECONDS  = 45    # countdown duration
HOLD_SECONDS   = 2     # seconds to hold '4' before triggering
TRIGGER_KEY    = '4'   # key to hold

# Optional video above the counter (leave empty to disable)
VIDEO_PATH     = r''   # e.g. r'C:\Videos\spike.webm'
```

## License

MIT — free to use, modify and share.
