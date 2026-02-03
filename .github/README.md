# TagQt

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FOSS](https://img.shields.io/badge/FOSS-100%25-success)](https://github.com/yourusername/tagqt)
[![Platform](https://img.shields.io/badge/Platform-Linux-green)](https://github.com/yourusername/tagqt)

A modern desktop audio metadata editor built with Python and PySide6, supporting MP3, FLAC, OGG, M4A, and WAV formats.

## Features

- **Metadata**: Edit Title, Artist, Album, Year, Genre, Track/Disc, and extended tags (BPM, Key, ISRC).
- **Global Edit Mode**: Batch edit multiple files simultaneously with dedicated UI.
- **Cover Art**: Fetch from online sources or load from local files.
- **Lyrics**: Fetch synchronized lyrics, load from file, or romanize using Koroman.
- **Auto-Tag**: Automatic metadata lookup via MusicBrainz.
- **File Operations**: Batch rename and Re-encode FLAC files.
- **Visuals**: Modern dark theme with extensive use of PySide6 styling.

## Screenshots

### Editor Mode

![Editor](editor.png)

### Global Editor Mode

![Global](globalmode.png)
*Edits done in this mode will apply to all selected files.*

## Requirements

**Minimum Python Version:** Python 3.10+

**System Dependencies:**

- `ffmpeg` (for re-encoding)

**Python Packages:**

- PySide6
- mutagen
- Pillow
- requests
- koroman
- musicbrainzngs

## Building

**Prerequisites**

- Python 3.10 or higher
- pip

```bash
# Clone the repository
git clone https://github.com/selr1/tagqt.git
cd tagqt

# Create virtual environment (Optional but recommended)
python -m venv venv
source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## To-do

- [ ] Implement audio format conversion for non-FLAC formats
- [ ] Add more lyrics sources
- [ ] Improve performance on very large directories
- [ ] Add plugin system for custom actions

## Credits

- [PySide6](https://doc.qt.io/qtforpython/)
- [Mutagen](https://mutagen.readthedocs.io/)
- [MusicBrainz](https://musicbrainz.org/)
- [Koroman](https://github.com/k44yn3/koroman)
- [FFmpeg](https://www.ffmpeg.org/)
