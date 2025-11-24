import 'dart:io';
import 'package:flutter/services.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';

class RomanizationManager {
  static RomanizationManager? _instance;
  String? _scriptPath;
  
  RomanizationManager._();
  
  static RomanizationManager get instance {
    _instance ??= RomanizationManager._();
    return _instance!;
  }
  
  /// Get the path to the romanize.py script
  /// Extracts the bundled script on first run
  Future<String> getScriptPath() async {
    if (_scriptPath != null) {
      return _scriptPath!;
    }
    
    // Asset path for the Python script
    const assetPath = 'scripts/romanize.py';
    
    // Get application support directory
    final appDir = await getApplicationSupportDirectory();
    final scriptsDir = Directory(path.join(appDir.path, 'scripts'));
    
    if (!await scriptsDir.exists()) {
      await scriptsDir.create(recursive: true);
    }
    
    final scriptFile = File(path.join(scriptsDir.path, 'romanize.py'));
    
    // Extract script if it doesn't exist or needs updating
    if (!await scriptFile.exists()) {
      print('Extracting romanization script to ${scriptFile.path}');
      final scriptContent = await rootBundle.loadString(assetPath);
      await scriptFile.writeAsString(scriptContent);
      
      // Make executable on Unix-like systems (though not strictly needed for Python scripts)
      if (Platform.isLinux || Platform.isMacOS) {
        await Process.run('chmod', ['+x', scriptFile.path]);
      }
    }
    
    _scriptPath = scriptFile.path;
    return _scriptPath!;
  }
  
  /// Check if Python3 and koroman are available
  Future<bool> isAvailable() async {
    try {
      final scriptPath = await getScriptPath();
      // Test with empty string to check if script can run
      final result = await Process.run('python3', [scriptPath, 'test']);
      // If koroman is missing, the script will return exit code 1 with error in JSON
      return result.exitCode == 0 || result.stdout.toString().contains('"result"');
    } catch (e) {
      print('Romanization not available: $e');
      return false;
    }
  }
}
