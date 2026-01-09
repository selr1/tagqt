#include "EditorPanel.h"
#include "dialogs/CoverSearchDialog.h"
#include "dialogs/LyricsSearchDialog.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFormLayout>
#include <QGroupBox>
#include <QPixmap>
#include <QFileDialog>
#include <QMessageBox>

EditorPanel::EditorPanel(QWidget *parent) 
    : QWidget(parent), metadataHandler(std::make_unique<MetadataHandler>()) {
    setupUI();
}

EditorPanel::~EditorPanel() {}

void EditorPanel::setupUI() {
    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    
    // Cover art section
    QGroupBox *coverGroup = new QGroupBox("Cover Art", this);
    QVBoxLayout *coverLayout = new QVBoxLayout(coverGroup);
    
    coverLabel = new QLabel(this);
    coverLabel->setFixedSize(200, 200);
    coverLabel->setScaledContents(true);
    coverLabel->setStyleSheet("QLabel { border: 1px solid #3E3E42; background-color: #252526; }");
    coverLabel->setText("No Cover");
    coverLabel->setAlignment(Qt::AlignCenter);
    coverLabel->setCursor(Qt::PointingHandCursor);
    connect(coverLabel, &QLabel::mousePressEvent, [this](QMouseEvent*) { onCoverClicked(); });
    
    fetchCoverButton = new QPushButton("Fetch Cover", this);
    connect(fetchCoverButton, &QPushButton::clicked, this, &EditorPanel::onFetchCoverClicked);
    
    coverLayout->addWidget(coverLabel, 0, Qt::AlignCenter);
    coverLayout->addWidget(fetchCoverButton);
    
    mainLayout->addWidget(coverGroup);
    
    // Metadata fields
    QGroupBox *tagsGroup = new QGroupBox("Metadata", this);
    QFormLayout *formLayout = new QFormLayout(tagsGroup);
    
    titleEdit = new QLineEdit(this);
    artistEdit = new QLineEdit(this);
    albumEdit = new QLineEdit(this);
    albumArtistEdit = new QLineEdit(this);
    yearEdit = new QLineEdit(this);
    genreEdit = new QLineEdit(this);
    
    formLayout->addRow("Title:", titleEdit);
    formLayout->addRow("Artist:", artistEdit);
    formLayout->addRow("Album:", albumEdit);
    formLayout->addRow("Album Artist:", albumArtistEdit);
    formLayout->addRow("Year:", yearEdit);
    formLayout->addRow("Genre:", genreEdit);
    
    mainLayout->addWidget(tagsGroup);
    
    // Lyrics section
    QGroupBox *lyricsGroup = new QGroupBox("Lyrics", this);
    QVBoxLayout *lyricsLayout = new QVBoxLayout(lyricsGroup);
    
    lyricsEdit = new QTextEdit(this);
    lyricsEdit->setMaximumHeight(150);
    
    fetchLyricsButton = new QPushButton("Fetch Lyrics", this);
    connect(fetchLyricsButton, &QPushButton::clicked, this, &EditorPanel::onFetchLyricsClicked);
    
    lyricsLayout->addWidget(lyricsEdit);
    lyricsLayout->addWidget(fetchLyricsButton);
    
    mainLayout->addWidget(lyricsGroup);
    
    // Save button
    saveButton = new QPushButton("Save Changes", this);
    saveButton->setStyleSheet("QPushButton { font-weight: bold; padding: 8px; }");
    connect(saveButton, &QPushButton::clicked, this, &EditorPanel::onSaveClicked);
    
    mainLayout->addWidget(saveButton);
    mainLayout->addStretch();
}

void EditorPanel::loadTrack(const TrackTags& tags) {
    currentTrack = tags;
    
    titleEdit->setText(QString::fromStdString(tags.title));
    artistEdit->setText(QString::fromStdString(tags.artist));
    albumEdit->setText(QString::fromStdString(tags.album));
    albumArtistEdit->setText(QString::fromStdString(tags.albumArtist));
    yearEdit->setText(QString::fromStdString(tags.year));
    genreEdit->setText(QString::fromStdString(tags.genre));
    lyricsEdit->setPlainText(QString::fromStdString(tags.lyrics));
    
    updateCoverDisplay();
}

TrackTags EditorPanel::getCurrentTags() const {
    TrackTags tags = currentTrack;
    
    tags.title = titleEdit->text().toStdString();
    tags.artist = artistEdit->text().toStdString();
    tags.album = albumEdit->text().toStdString();
    tags.albumArtist = albumArtistEdit->text().toStdString();
    tags.year = yearEdit->text().toStdString();
    tags.genre = genreEdit->text().toStdString();
    tags.lyrics = lyricsEdit->toPlainText().toStdString();
    
    return tags;
}

void EditorPanel::onSaveClicked() {
    TrackTags tags = getCurrentTags();
    emit saveTags(QString::fromStdString(currentTrack.path), tags);
}

void EditorPanel::onFetchCoverClicked() {
    if (currentTrack.path.empty()) {
        QMessageBox::warning(this, "No Track", "Please select a track first.");
        return;
    }
    
    CoverSearchDialog dialog(
        QString::fromStdString(currentTrack.artist),
        QString::fromStdString(currentTrack.album),
        this
    );
    
    if (dialog.exec() == QDialog::Accepted) {
        currentCoverData = dialog.getSelectedCover();
        if (!currentCoverData.empty()) {
            // Save cover to file
            AudioHandler audioHandler;
            if (audioHandler.setCover(currentTrack.path, currentCoverData)) {
                updateCoverDisplay();
                QMessageBox::information(this, "Success", "Cover art updated successfully!");
            } else {
                QMessageBox::warning(this, "Error", "Failed to save cover art.");
            }
        }
    }
}

void EditorPanel::onFetchLyricsClicked() {
    if (currentTrack.path.empty()) {
        QMessageBox::warning(this, "No Track", "Please select a track first.");
        return;
    }
    
    LyricsSearchDialog dialog(
        QString::fromStdString(currentTrack.artist),
        QString::fromStdString(currentTrack.title),
        QString::fromStdString(currentTrack.album),
        this
    );
    
    if (dialog.exec() == QDialog::Accepted) {
        QString lyrics = dialog.getSelectedLyrics();
        if (!lyrics.isEmpty()) {
            lyricsEdit->setPlainText(lyrics);
        }
    }
}

void EditorPanel::onCoverClicked() {
    QString filepath = QFileDialog::getOpenFileName(
        this,
        "Select Cover Image",
        QString(),
        "Images (*.jpg *.jpeg *.png)"
    );
    
    if (!filepath.isEmpty()) {
        QFile file(filepath);
        if (file.open(QIODevice::ReadOnly)) {
            QByteArray data = file.readAll();
            currentCoverData.assign(data.begin(), data.end());
            
            QString mimeType = filepath.endsWith(".png") ? "image/png" : "image/jpeg";
            
            AudioHandler audioHandler;
            if (audioHandler.setCover(currentTrack.path, currentCoverData, mimeType.toStdString())) {
                updateCoverDisplay();
                QMessageBox::information(this, "Success", "Cover art updated successfully!");
            } else {
                QMessageBox::warning(this, "Error", "Failed to save cover art.");
            }
        }
    }
}

void EditorPanel::updateCoverDisplay() {
    if (currentTrack.path.empty()) {
        coverLabel->setText("No Track");
        return;
    }
    
    AudioHandler audioHandler;
    std::vector<unsigned char> coverData = audioHandler.getCover(currentTrack.path);
    
    if (!coverData.empty()) {
        QPixmap pixmap;
        pixmap.loadFromData(coverData.data(), coverData.size());
        coverLabel->setPixmap(pixmap);
    } else {
        coverLabel->setText("No Cover");
    }
}
