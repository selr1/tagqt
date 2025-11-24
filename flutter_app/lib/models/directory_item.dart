import 'audio_file.dart';

/// Represents either a directory or an audio file in the file list
class DirectoryItem {
  final String path;
  final String name;
  final bool isDirectory;
  final AudioFile? audioFile; // null if this is a directory
  
  const DirectoryItem({
    required this.path,
    required this.name,
    required this.isDirectory,
    this.audioFile,
  });
  
  /// Create a DirectoryItem from a directory path
  factory DirectoryItem.fromDirectory(String path, String name) {
    return DirectoryItem(
      path: path,
      name: name,
      isDirectory: true,
      audioFile: null,
    );
  }
  
  /// Create a DirectoryItem from an AudioFile
  factory DirectoryItem.fromAudioFile(AudioFile file) {
    return DirectoryItem(
      path: file.path,
      name: file.filename,
      isDirectory: false,
      audioFile: file,
    );
  }
}
