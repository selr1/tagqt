"""
Music playback controller using PySide6.QtMultimedia.

Manages a queue of file paths and plays them in order.
Includes LRC lyrics parsing and synchronized line tracking.
"""

import re
import logging
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, QObject, Signal

logger = logging.getLogger(__name__)

_LRC_PATTERN = re.compile(r'\[(\d+):(\d+)[\.:](\d+)\](.*)')


def parse_lrc(text: str) -> list[tuple[int, str]]:
    """
    Parse LRC formatted lyrics into a list of (milliseconds, line) tuples
    sorted by time ascending. Lines without timestamps are ignored.

    Handles formats:
    [mm:ss.xx]  — standard LRC
    [mm:ss.xxx] — extended precision
    """
    result = []
    for line in text.splitlines():
        match = _LRC_PATTERN.match(line.strip())
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            frac = match.group(3)
            # Normalize: if 2 digits treat as centiseconds, if 3 as milliseconds
            if len(frac) <= 2:
                ms_frac = int(frac) * 10
            else:
                ms_frac = int(frac)
            ms = (minutes * 60 + seconds) * 1000 + ms_frac
            text_part = match.group(4).strip()
            result.append((ms, text_part))
    return sorted(result, key=lambda x: x[0])


class PlayerController(QObject):
    """Manages playback of a queue of audio files."""

    state_changed = Signal(str)          # 'playing', 'paused', 'stopped'
    track_changed = Signal(int)          # index of now-playing track
    position_changed = Signal(int, int)  # current_ms, total_ms
    lyric_line_changed = Signal(int)     # index of current lyric line

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._player.setAudioOutput(self._audio)
        self._audio.setVolume(1.0)
        self._queue: list[str] = []
        self._current: int = -1

        # Lyrics sync state
        self._lrc_lines: list[tuple[int, str]] = []
        self._last_lyric_idx: int = -1

        self._player.playbackStateChanged.connect(self._on_state_changed)
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.mediaStatusChanged.connect(self._on_media_status)

    # ── Public API ──────────────────────────────────────────────────────

    def set_queue(self, filepaths: list[str], start_index: int = 0):
        """Set the playback queue from the current display order."""
        self._queue = list(filepaths)
        self._current = start_index
        self._load_current()

    def play_pause(self):
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            self.state_changed.emit('paused')
        else:
            self._player.play()
            self.state_changed.emit('playing')

    def stop(self):
        self._player.stop()
        self._lrc_lines = []
        self._last_lyric_idx = -1
        self.state_changed.emit('stopped')

    def next_track(self):
        if self._current < len(self._queue) - 1:
            self._current += 1
            self._load_current()
            self._player.play()
            self.track_changed.emit(self._current)
            self.state_changed.emit('playing')

    def prev_track(self):
        if self._current > 0:
            self._current -= 1
            self._load_current()
            self._player.play()
            self.track_changed.emit(self._current)
            self.state_changed.emit('playing')

    def seek(self, ms: int):
        self._player.setPosition(ms)
        self._last_lyric_idx = -1  # force re-evaluation at new position

    def set_volume(self, value: float):
        """Set volume as 0.0–1.0."""
        self._audio.setVolume(value)

    def set_lyrics(self, lrc_text: str):
        """Parse and load LRC lyrics for sync. Call when a track starts."""
        self._lrc_lines = parse_lrc(lrc_text) if lrc_text else []
        self._last_lyric_idx = -1

    @property
    def current_index(self):
        return self._current

    @property
    def current_path(self):
        if 0 <= self._current < len(self._queue):
            return self._queue[self._current]
        return None

    # ── Internal ────────────────────────────────────────────────────────

    def _load_current(self):
        if 0 <= self._current < len(self._queue):
            self._player.setSource(
                QUrl.fromLocalFile(self._queue[self._current])
            )

    def _on_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.state_changed.emit('stopped')

    def _on_position_changed(self, pos):
        self.position_changed.emit(pos, self._player.duration())

        # Sync lyrics
        if not self._lrc_lines:
            return
        current_idx = 0
        for i, (ms, _) in enumerate(self._lrc_lines):
            if pos >= ms:
                current_idx = i
            else:
                break
        if current_idx != self._last_lyric_idx:
            self._last_lyric_idx = current_idx
            self.lyric_line_changed.emit(current_idx)

    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.next_track()
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            path = self.current_path or "<unknown>"
            logger.warning("Unplayable file, skipping: %s", path)
            self.next_track()
