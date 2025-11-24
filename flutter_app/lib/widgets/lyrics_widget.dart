import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/audio_file.dart';
import '../services/tag_service.dart';
import '../services/romanization_service.dart';
import '../providers/app_state.dart';
import 'lyrics_edit_dialog.dart';

class LyricsWidget extends StatefulWidget {
  final AudioFile file;

  const LyricsWidget({super.key, required this.file});

  @override
  State<LyricsWidget> createState() => _LyricsWidgetState();
}

class _LyricsWidgetState extends State<LyricsWidget> {
  String? _lyrics;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadLyrics();
  }


  @override
  void didUpdateWidget(covariant LyricsWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Reload if file path changed OR if tags changed (after reloadFile)
    // Also reload if pending lyrics changed
    if (oldWidget.file.path != widget.file.path || 
        oldWidget.file.tags != widget.file.tags ||
        oldWidget.file.pendingLyrics != widget.file.pendingLyrics) {
      _loadLyrics();
    }
  }
  
  // Listen to app state changes to reload when batch template updates
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // This will trigger when appState changes (batch mode toggle, batch fetch complete)
    // We reload to pick up changes
    _loadLyrics();
  }


  Future<void> _loadLyrics() async {
    final appState = context.read<AppState>();
    final isBatch = appState.isBatchMode;
    
    // In batch mode, handle lyrics differently
    if (isBatch) {
      // Prioritize the specific file's pending lyrics if available
      if (widget.file.pendingLyrics != null) {
        if (mounted) {
          setState(() {
            _lyrics = widget.file.pendingLyrics;
            _isLoading = false;
          });
        }
        return;
      }

      // Fallback: Check if batch template has pending lyrics (only if we are viewing the template or if we want to show a "default")
      // But for unique preview, we usually want to see the file's own state.
      // If the file has NO lyrics and NO pending lyrics, we might show "No lyrics" instead of the template's lyrics.
      // Showing template lyrics on a different song is confusing.
      
      // However, if the user manually pasted lyrics into the template to apply to all, maybe they want to see it?
      // But "Fetch All" generates unique lyrics.
      
      // Let's stick to: Show file's lyrics (pending or tag). 
      // Only show template lyrics if widget.file IS the template (which happens in some views, but EditorPanel usually passes selectedFile).
      
      if (widget.file == appState.batchTemplate && appState.batchTemplate?.pendingLyrics != null) {
         if (mounted) {
          setState(() {
            _lyrics = appState.batchTemplate!.pendingLyrics;
            _isLoading = false;
          });
        }
        return;
      }
      
      // Load from file's tags if no pending lyrics
      setState(() => _isLoading = true);
      final tagService = TagService();
      final lyrics = await tagService.getLyrics(widget.file);
      if (mounted) {
        setState(() {
          _lyrics = lyrics;
          _isLoading = false;
        });
      }
      return;
    }
    
    // Normal mode: use file's data
    // If we have pending lyrics, use them directly
    if (widget.file.pendingLyrics != null) {
      if (mounted) {
        setState(() {
          _lyrics = widget.file.pendingLyrics;
          _isLoading = false;
        });
      }
      return;
    }

    setState(() => _isLoading = true);
    final tagService = TagService();
    final lyrics = await tagService.getLyrics(widget.file);
    if (mounted) {
      setState(() {
        _lyrics = lyrics;
        _isLoading = false;
      });
    }
  }

  Future<void> _editLyrics() async {
    // Pass pending lyrics if available, otherwise current lyrics
    final initialLyrics = widget.file.pendingLyrics ?? _lyrics ?? '';
    
    await showLyricsEditDialog(
      context,
      widget.file,
      initialLyrics,
    );
    
    // No need to reload file here, AppState handles pending changes
    // didUpdateWidget will catch the change in pendingLyrics
  }

  @override
  Widget build(BuildContext context) {
    final appState = context.watch<AppState>();
    final isBatch = appState.isBatchMode;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                const Text(
                  'Lyrics',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                if (!isBatch) ...[
                  const SizedBox(width: 16),
                  Checkbox(
                    value: widget.file.extractLyrics,
                    onChanged: (value) {
                      context.read<AppState>().setExtractLyrics(widget.file, value ?? false);
                    },
                  ),
                  const Text('Copy and Rename'),
                ],
              ],
            ),
            Row(
              children: [
                if (isBatch) ...[
                  // Batch mode options
                  Checkbox(
                    value: appState.batchTemplate?.extractLyrics ?? false,
                    onChanged: (value) {
                      context.read<AppState>().setBatchExtract(value ?? false);
                    },
                  ),
                  const Text('Copy and Rename'),
                  const SizedBox(width: 16),
                ],
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    border: Border.all(color: Theme.of(context).colorScheme.outline),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<bool>(
                      value: isBatch 
                          ? (appState.batchTemplate?.romanizeLyrics ?? false)
                          : widget.file.romanizeLyrics,
                      icon: const Icon(Icons.translate),
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.onSurface,
                        fontWeight: FontWeight.w500,
                      ),
                      items: const [
                        DropdownMenuItem(
                          value: false, 
                          child: Text('Original Lyrics'),
                        ),
                        DropdownMenuItem(
                          value: true, 
                          child: Text('Romanize (Korean)'),
                        ),
                      ],
                      onChanged: (value) {
                        if (isBatch) {
                          context.read<AppState>().setBatchRomanize(value ?? false);
                        } else {
                          context.read<AppState>().setRomanizeLyrics(widget.file, value ?? false);
                        }
                      },
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                if (isBatch)
                  FilledButton.tonalIcon(
                    onPressed: appState.isLoading ? null : () => appState.batchFetchLyrics(),
                    icon: appState.isFetchingLyrics 
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.cloud_download),
                    label: const Text('Fetch All'),
                  )
                else
                  FilledButton.tonalIcon(
                    onPressed: _editLyrics,
                    icon: const Icon(Icons.edit),
                    label: const Text('Edit Lyrics'),
                  ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 12),
        Container(
          height: 200,
          width: double.infinity,
          decoration: BoxDecoration(
            border: Border.all(
              color: widget.file.pendingLyrics != null
                  ? Theme.of(context).colorScheme.primary
                  : Theme.of(context).colorScheme.outline.withOpacity(0.5),
              width: widget.file.pendingLyrics != null ? 3 : 1,
            ),
            borderRadius: BorderRadius.circular(8),
            color: Theme.of(context).colorScheme.surfaceContainerHighest,
          ),
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _lyrics == null || _lyrics!.isEmpty
                  ? Center(
                      child: Text(
                        'No lyrics',
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    )
                  : SingleChildScrollView(
                      padding: const EdgeInsets.all(12),
                      child: SelectableText(
                        _lyrics!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.onSurface,
                          height: 1.5,
                        ),
                      ),
                    ),
        ),
      ],
    );
  }
}
