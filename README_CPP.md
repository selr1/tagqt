# TagFix - Audio Metadata Editor (C++ Version)

A professional audio metadata editor with a modern dark UI, rebuilt entirely in C++.

## Features

- **Multi-format Support**: MP3, FLAC, M4A, OGG, WAV
- **Complete Metadata Editing**: Title, artist, album, album artist, year, genre
- **Cover Art Management**: View, fetch, and embed album artwork
- **Lyrics Support**: Edit and fetch synchronized/unsynchronized lyrics
- **Batch Editing**: Edit multiple files at once
- **Online Metadata**: Fetch covers from iTunes and MusicBrainz
- **Modern Dark UI**: Professional VS Code-inspired interface

## Prerequisites

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    qt5-default \
    libqt5widgets5 \
    libqt5network5 \
    libtag1-dev \
    libjsoncpp-dev \
    pkg-config
```

### Fedora/RHEL
```bash
sudo dnf install -y \
    gcc-c++ \
    cmake \
    qt5-qtbase-devel \
    taglib-devel \
    jsoncpp-devel \
    pkg-config
```

### macOS
```bash
brew install cmake qt@5 taglib jsoncpp pkg-config
export PATH="/usr/local/opt/qt@5/bin:$PATH"
```

### Windows (MSYS2/MinGW)
```bash
pacman -S --needed \
    mingw-w64-x86_64-gcc \
    mingw-w64-x86_64-cmake \
    mingw-w64-x86_64-qt5 \
    mingw-w64-x86_64-taglib \
    mingw-w64-x86_64-jsoncpp
```

## Building

```bash
# Create build directory
mkdir -p build
cd build

# Configure with CMake
cmake ..

# Build
cmake --build .

# Or use make directly
make -j$(nproc)
```

## Running

```bash
# From build directory
./TagFix

# Or install system-wide
sudo make install
tagfix
```

## Usage

1. **Browse Files**: Use the right panel to navigate your music library
2. **Select Folder**: Click on a folder to load all audio files
3. **Edit Metadata**: Select a track, edit fields in the left panel
4. **Fetch Artwork**: Click "Fetch Cover" to search online databases
5. **Fetch Lyrics**: Click "Fetch Lyrics" to search for song lyrics
6. **Save Changes**: Click "Save Changes" to write tags to file
7. **Batch Edit**: Select multiple files and use File → Batch Edit

## Configuration

Settings are stored in `settings.json` in the application directory:

```json
{
  "covers": {
    "source": "iTunes",
    "force_500px": true
  },
  "lyrics": {
    "auto_fetch": false
  }
}
```

## Technology Stack

- **C++17**: Modern C++ standards
- **Qt5**: Cross-platform GUI framework
- **TagLib**: Audio metadata library
- **JsonCpp**: JSON configuration handling
- **CMake**: Build system

## Architecture

```
src/
├── core/
│   ├── AudioHandler.cpp      # Audio file I/O with TagLib
│   ├── MetadataHandler.cpp   # Online metadata fetching
│   └── ConfigManager.cpp     # Settings management
├── gui/
│   ├── MainWindow.cpp        # Main application window
│   ├── TrackTable.cpp        # Track listing table
│   ├── EditorPanel.cpp       # Metadata editor
│   ├── BrowserPanel.cpp      # File system browser
│   └── dialogs/              # Various dialogs
└── main.cpp                  # Application entry point
```

## Differences from Python Version

This C++ version provides:
- **Better Performance**: Native code execution
- **Lower Memory Usage**: Efficient memory management
- **Faster Startup**: No interpreter overhead
- **Cross-platform Binary**: Single executable deployment
- **Professional UI**: Qt5-based native interface

## License

See LICENSE file for details.

## Contributing

Contributions welcome! Please open issues or pull requests on GitHub.
