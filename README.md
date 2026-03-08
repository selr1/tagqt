<p align="center">
  <img src="assets/logo.png" alt="TagQt" width="420"/>
</p>

<p align="center">
  <strong>A music metadata editor built with Python and Qt</strong>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square&labelColor=1e1e2e&color=f38ba8" alt="License: MIT"/></a>
  <a href="https://github.com/selr1/tagqt"><img src="https://img.shields.io/badge/FOSS-100%25-success?style=flat-square&labelColor=1e1e2e&color=a6e3a1" alt="FOSS"/></a>
  <a href="https://github.com/selr1/tagqt"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-green?style=flat-square&labelColor=1e1e2e&color=cba6f7" alt="Platform"/></a>
  <a href="https://github.com/selr1/tagqt"><img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&labelColor=1e1e2e&color=89b4fa" alt="Python 3.10+"/></a>
</p>

TagQt lets you edit audio file metadata without the bloat. Load a folder, edit tags one at a time or in bulk, fetch lyrics and album art automatically, auto-tag from MusicBrainz, rename files by pattern, and re-encode FLAC — all from one window.

## Screenshot

<p align="center">
  <img src="assets/screenshot.png" alt="TagQt Screenshot" width="800"/>
</p>

## Features

- Edit tags for MP3, FLAC, OGG, M4A, and WAV files
- Batch edit — select multiple files and change them all at once
- Auto-tag from MusicBrainz (artist, album, year, track number, genre)
- Fetch synced and plain lyrics from LRCLIB
- Search and download album artwork
- Resize covers to a target resolution
- Batch rename files using a tag pattern (`%artist% - %title%`)
- Re-encode FLAC files to 24-bit 48kHz
- Romanize Korean and CJK lyrics
- Import and export metadata as CSV
- Convert filename and tag case (title case, UPPER, lower)
- Command palette (`Ctrl+K`) for quick access to any action
- Catppuccin Mocha dark theme with optional light mode
- Drag and drop files or folders to load them

## Keyboard Shortcuts

| Shortcut | Action                                   |
| -------- | ---------------------------------------- |
| `Ctrl+O` | Open a folder                            |
| `Ctrl+S` | Save changes                             |
| `Ctrl+G` | Toggle global edit for all visible files |
| `Ctrl+A` | Select all files                         |
| `Ctrl+K` | Open the command palette                 |
| `Ctrl+Q` | Quit the app                             |
| `Escape` | Exit global edit mode                    |

## Installation

### From a Release

Download the latest build from [Releases](https://github.com/selr1/tagqt/releases):

- **Windows** — download the `.exe` and run it directly
- **Linux** — download the AppImage, make it executable with `chmod +x`, and run it

### From Source

Requires Python 3.10 or later.

```bash
git clone https://github.com/selr1/tagqt.git
cd tagqt
pip install -r requirements.txt
python main.py
```

## Dependencies

| Package          | What it does                                            |
| ---------------- | ------------------------------------------------------- |
| `PySide6`        | Qt GUI framework                                        |
| `mutagen`        | Reads and writes audio metadata                         |
| `Pillow`         | Handles image processing for cover art                  |
| `requests`       | Makes HTTP requests for lyrics, covers, and MusicBrainz |
| `musicbrainzngs` | Connects to the MusicBrainz API                         |
| `koroman`        | Romanizes Korean and CJK text                           |

Optional:

- `ffmpeg` — needed for FLAC re-encoding and must be on your PATH

## Usage

1. Open a folder with `Ctrl+O` or drag a folder onto the window
2. Click a file to view and edit its tags in the sidebar
3. Press `Ctrl+S` to save your changes, or click the Save button
4. Select multiple files (or press `Ctrl+G`) to enter global edit mode — any changes you make will apply to all selected files at once
5. Right-click files for quick actions like fetching covers, fetching lyrics, renaming, re-encoding, or auto-tagging

### Batch Operations

All batch tools work on either your current selection or all visible files:

- **Fetch lyrics** — searches LRCLIB for synced or plain lyrics and saves `.lrc` files alongside the audio
- **Fetch covers** — searches for album art, embeds it into the file, and saves a `cover.jpg` next to it
- **Auto-tag** — looks up the release on MusicBrainz and fills in missing metadata
- **Rename** — renames files based on a pattern like `%artist% - %title%`
- **Re-encode FLAC** — converts FLAC files to 24-bit 48kHz using ffmpeg

## Building

Check [`.github/workflows/release.yml`](.github/workflows/release.yml) for the full build steps. The CI builds a Windows `.exe` and a Linux AppImage on every version tag push.

## Contributing

Contributions are welcome — open an issue or submit a pull request.
