import 'dart:io';
import 'package:flutter/services.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';

class FfmpegManager {
  static FfmpegManager? _instance;
  String? _ffmpegPath;
  
  FfmpegManager._();
  
  static FfmpegManager get instance {
    _instance ??= FfmpegManager._();
    return _instance!;
  }
  
  /// Get the path to the ffmpeg executable
  /// Extracts the bundled binary on first run
  Future<String> getFfmpegPath() async {
    if (_ffmpegPath != null) {
      return _ffmpegPath!;
    }
    
    // Determine platform-specific binary name and asset path
    String binaryName;
    String assetPath;
    
    if (Platform.isLinux) {
      binaryName = 'ffmpeg';
      assetPath = 'assets/ffmpeg/linux/ffmpeg';
    } else if (Platform.isWindows) {
      binaryName = 'ffmpeg.exe';
      assetPath = 'assets/ffmpeg/windows/ffmpeg.exe';
    } else if (Platform.isMacOS) {
      binaryName = 'ffmpeg';
      assetPath = 'assets/ffmpeg/macos/ffmpeg';
    } else {
      throw UnsupportedError('Platform not supported');
    }
    
    // Get application support directory
    final appDir = await getApplicationSupportDirectory();
    final ffmpegDir = Directory(path.join(appDir.path, 'ffmpeg'));
    
    if (!await ffmpegDir.exists()) {
      await ffmpegDir.create(recursive: true);
    }
    
    final ffmpegFile = File(path.join(ffmpegDir.path, binaryName));
    
    // Extract binary if it doesn't exist
    if (!await ffmpegFile.exists()) {
      print('Extracting ffmpeg binary to ${ffmpegFile.path}');
      final byteData = await rootBundle.load(assetPath);
      await ffmpegFile.writeAsBytes(
        byteData.buffer.asUint8List(byteData.offsetInBytes, byteData.lengthInBytes),
      );
      
      // Make executable on Unix-like systems
      if (Platform.isLinux || Platform.isMacOS) {
        await Process.run('chmod', ['+x', ffmpegFile.path]);
      }
    }
    
    _ffmpegPath = ffmpegFile.path;
    return _ffmpegPath!;
  }
  
  /// Check if ffmpeg is available
  Future<bool> isAvailable() async {
    try {
      final ffmpegPath = await getFfmpegPath();
      final result = await Process.run(ffmpegPath, ['-version']);
      return result.exitCode == 0;
    } catch (e) {
      print('FFmpeg not available: $e');
      return false;
    }
  }
}
