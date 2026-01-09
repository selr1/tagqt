#include "MainWindow.h"
#include "TrackTable.h"
#include "EditorPanel.h"
#include "BrowserPanel.h"
#include "dialogs/SettingsDialog.h"
#include <QMenuBar>
#include <QMenu>
#include <QAction>
#include <QApplication>
#include <QStyle>
#include <QDir>
#include <QDirIterator>
#include <QFileInfo>
#include <filesystem>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent), audioHandler(std::make_unique<AudioHandler>()) {
    
    setWindowTitle("TagFix");
    resize(1200, 800);
    
    setupUI();
    applyDarkTheme();
    
    currentPath = QDir::homePath();
    browserPanel->setRoot(currentPath);
}

MainWindow::~MainWindow() {}

void MainWindow::setupUI() {
    // Create menu bar
    QMenuBar *menuBar = new QMenuBar(this);
    setMenuBar(menuBar);
    
    QMenu *fileMenu = menuBar->addMenu("&File");
    QAction *settingsAction = fileMenu->addAction("&Settings");
    connect(settingsAction, &QAction::triggered, [this]() {
        SettingsDialog dialog(this);
        dialog.exec();
    });
    
    QAction *exitAction = fileMenu->addAction("E&xit");
    connect(exitAction, &QAction::triggered, qApp, &QApplication::quit);
    
    // Create main splitter
    mainSplitter = new QSplitter(Qt::Horizontal, this);
    setCentralWidget(mainSplitter);
    
    // Create panels
    editorPanel = new EditorPanel(this);
    trackTable = new TrackTable(this);
    browserPanel = new BrowserPanel(this);
    
    // Add panels to splitter
    mainSplitter->addWidget(editorPanel);
    mainSplitter->addWidget(trackTable);
    mainSplitter->addWidget(browserPanel);
    
    // Set stretch factors (proportions)
    mainSplitter->setStretchFactor(0, 1);  // Editor
    mainSplitter->setStretchFactor(1, 3);  // Table
    mainSplitter->setStretchFactor(2, 1);  // Browser
    
    // Connect signals
    connect(browserPanel, &BrowserPanel::folderSelected, this, &MainWindow::onFolderSelected);
    connect(trackTable, &TrackTable::trackSelected, this, &MainWindow::onTrackSelected);
    connect(editorPanel, &EditorPanel::saveTags, this, &MainWindow::onSaveTags);
    connect(trackTable, &TrackTable::refreshRequested, this, &MainWindow::refreshCurrentFolder);
}

void MainWindow::applyDarkTheme() {
    // Modern dark theme
    QString darkStyleSheet = R"(
        QMainWindow, QWidget {
            background-color: #1E1E1E;
            color: #D4D4D4;
        }
        
        QMenuBar {
            background-color: #252526;
            color: #D4D4D4;
            border-bottom: 1px solid #3E3E42;
        }
        
        QMenuBar::item:selected {
            background-color: #3C3C3C;
        }
        
        QMenu {
            background-color: #252526;
            color: #D4D4D4;
            border: 1px solid #3E3E42;
        }
        
        QMenu::item:selected {
            background-color: #094771;
        }
        
        QLineEdit, QTextEdit {
            background-color: #3C3C3C;
            color: #D4D4D4;
            border: 1px solid #3E3E42;
            padding: 4px;
        }
        
        QPushButton {
            background-color: #252526;
            color: #D4D4D4;
            border: 1px solid #3E3E42;
            padding: 6px 12px;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #3C3C3C;
        }
        
        QPushButton:pressed {
            background-color: #3E3E42;
        }
        
        QTreeWidget, QTreeView, QListWidget {
            background-color: #1E1E1E;
            color: #D4D4D4;
            border: 1px solid #3E3E42;
            alternate-background-color: #252526;
        }
        
        QTreeWidget::item:selected, QTreeView::item:selected, QListWidget::item:selected {
            background-color: #094771;
            color: #FFFFFF;
        }
        
        QHeaderView::section {
            background-color: #252526;
            color: #D4D4D4;
            border: 1px solid #3E3E42;
            padding: 4px;
        }
        
        QLabel {
            color: #D4D4D4;
        }
        
        QComboBox {
            background-color: #3C3C3C;
            color: #D4D4D4;
            border: 1px solid #3E3E42;
            padding: 4px;
        }
        
        QCheckBox {
            color: #D4D4D4;
        }
        
        QSplitter::handle {
            background-color: #3E3E42;
        }
    )";
    
    setStyleSheet(darkStyleSheet);
}

void MainWindow::onFolderSelected(const QString& path) {
    currentPath = path;
    trackTable->clear();
    tracksCache.clear();
    
    QStringList supportedExts = {"*.mp3", "*.flac", "*.m4a", "*.ogg", "*.wav"};
    
    // Use QDirIterator for safe recursive directory traversal
    QDirIterator it(path, supportedExts, QDir::Files | QDir::NoSymLinks, QDirIterator::Subdirectories);
    
    while (it.hasNext()) {
        QString filepath = it.next();
        TrackTags tags = audioHandler->getTags(filepath.toStdString());
        QString itemId = trackTable->addTrack(tags);
        tracksCache[filepath] = tags;
    }
    
    browserPanel->log(QString("Loaded %1 tracks from %2").arg(tracksCache.size()).arg(path));
}

void MainWindow::onTrackSelected(const QString& filepath) {
    if (tracksCache.find(filepath) != tracksCache.end()) {
        editorPanel->loadTrack(tracksCache[filepath]);
    }
}

void MainWindow::onSaveTags(const QString& filepath, const TrackTags& tags) {
    if (audioHandler->saveTags(filepath.toStdString(), tags)) {
        // Update cache
        tracksCache[filepath] = tags;
        trackTable->refreshRow(filepath);
        browserPanel->log(QString("Saved tags for: %1").arg(QFileInfo(filepath).fileName()));
        
        // Reload in editor if still selected
        editorPanel->loadTrack(tags);
    } else {
        browserPanel->log(QString("Failed to save tags for: %1").arg(QFileInfo(filepath).fileName()));
    }
}

void MainWindow::refreshCurrentFolder() {
    if (!currentPath.isEmpty()) {
        onFolderSelected(currentPath);
    }
}
