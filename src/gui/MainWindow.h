#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QSplitter>
#include <memory>
#include "../core/AudioHandler.h"

class TrackTable;
class EditorPanel;
class BrowserPanel;

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void onFolderSelected(const QString& path);
    void onTrackSelected(const QString& filepath);
    void onSaveTags(const QString& filepath, const TrackTags& tags);
    void refreshCurrentFolder();

private:
    void setupUI();
    void applyDarkTheme();
    
    QSplitter *mainSplitter;
    EditorPanel *editorPanel;
    TrackTable *trackTable;
    BrowserPanel *browserPanel;
    
    std::unique_ptr<AudioHandler> audioHandler;
    QString currentPath;
    std::map<QString, TrackTags> tracksCache;
};

#endif // MAINWINDOW_H
