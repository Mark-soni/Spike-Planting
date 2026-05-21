# Spike Planting 💣

> 🌐 [Versión en Español](README.es.md)

A Valorant overlay that shows a 45-second countdown with the Spike animation when you hold the `4` key — works globally even while in-game.

## Features

- Hold `4` for 2 seconds to trigger the countdown
- Spike animation synced to the 45-second timer
- Always-on-top overlay — works over Valorant, Chrome, anything
- Remembers position between sessions (drag to move)
- Does **not** steal focus or minimize your game

## Controls

| Key | Action |
|-----|--------|
| Hold `4` (2s) | Start countdown |
| `Ctrl+Q` | Hide overlay |
| `Ctrl+Shift+Q` | Exit app |

## Requirements

- Python 3.x
- Your own `Spike.webm` video file (place path in `countdown.py`)

```
pip install keyboard opencv-python Pillow
```

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
SPIKE_OFFSET_X = 290   # horizontal position of spike in video
HALF_CROP      = 380   # zoom level (higher = more zoomed out)
```

## License

MIT — free to use, modify and share.
