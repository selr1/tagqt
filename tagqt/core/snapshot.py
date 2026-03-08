from tagqt.core.tags import MetadataHandler

SNAPSHOT_FIELDS = [
    'title', 'artist', 'album', 'album_artist', 'year', 'genre',
    'track_number', 'disc_number', 'comment', 'bpm', 'initial_key',
    'isrc', 'publisher', 'lyrics',
]


class BatchSnapshot:
    """Captures tag values for a set of files before a batch operation."""

    def __init__(self, operation_name, filepaths):
        self.operation_name = operation_name
        self.snapshots = {}  # filepath -> {field: value}
        for fp in filepaths:
            try:
                md = MetadataHandler(fp)
                self.snapshots[fp] = {f: getattr(md, f, '') for f in SNAPSHOT_FIELDS}
            except Exception:
                pass
