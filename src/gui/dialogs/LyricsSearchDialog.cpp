#include "LyricsSearchDialog.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QMessageBox>

LyricsSearchDialog::LyricsSearchDialog(const QString& artist, const QString& title, const QString& album, QWidget *parent)
    : QDialog(parent), artist(artist), title(title), album(album), metadataHandler(std::make_unique<MetadataHandler>()) {
    setupUI();
    setWindowTitle("Search Lyrics");
    resize(700, 500);
}

LyricsSearchDialog::~LyricsSearchDialog() {}

void LyricsSearchDialog::setupUI() {
    QVBoxLayout *layout = new QVBoxLayout(this);
    
    QLabel *infoLabel = new QLabel(QString("Searching for: %1 - %2").arg(artist, title), this);
    layout->addWidget(infoLabel);
    
    QHBoxLayout *contentLayout = new QHBoxLayout();
    
    // Results list
    resultsList = new QListWidget(this);
    contentLayout->addWidget(resultsList, 1);
    
    // Preview
    lyricsPreview = new QTextEdit(this);
    lyricsPreview->setReadOnly(true);
    contentLayout->addWidget(lyricsPreview, 2);
    
    layout->addLayout(contentLayout);
    
    QHBoxLayout *buttonLayout = new QHBoxLayout();
    searchButton = new QPushButton("Search", this);
    acceptButton = new QPushButton("Use Selected", this);
    QPushButton *cancelButton = new QPushButton("Cancel", this);
    
    buttonLayout->addWidget(searchButton);
    buttonLayout->addWidget(acceptButton);
    buttonLayout->addWidget(cancelButton);
    
    layout->addLayout(buttonLayout);
    
    connect(searchButton, &QPushButton::clicked, this, &LyricsSearchDialog::onSearchClicked);
    connect(acceptButton, &QPushButton::clicked, this, &LyricsSearchDialog::onAcceptClicked);
    connect(cancelButton, &QPushButton::clicked, this, &QDialog::reject);
    connect(resultsList, &QListWidget::itemClicked, this, &LyricsSearchDialog::onResultSelected);
    
    // Auto-search on open
    onSearchClicked();
}

void LyricsSearchDialog::onSearchClicked() {
    resultsList->clear();
    lyricsPreview->clear();
    
    searchResults = metadataHandler->searchLyrics(
        artist.toStdString(),
        title.toStdString(),
        album.toStdString()
    );
    
    if (searchResults.empty()) {
        QMessageBox::information(this, "No Results", "No lyrics found.");
        return;
    }
    
    for (size_t i = 0; i < searchResults.size(); ++i) {
        const auto& result = searchResults[i];
        QString itemText = QString("%1 - %2")
            .arg(QString::fromStdString(result.at("artist")))
            .arg(QString::fromStdString(result.at("title")));
        
        if (!result.at("album").empty()) {
            itemText += QString(" (%1)").arg(QString::fromStdString(result.at("album")));
        }
        
        QListWidgetItem *item = new QListWidgetItem(itemText, resultsList);
        item->setData(Qt::UserRole, static_cast<int>(i));
        resultsList->addItem(item);
    }
}

void LyricsSearchDialog::onResultSelected(QListWidgetItem* item) {
    int index = item->data(Qt::UserRole).toInt();
    
    if (index >= 0 && index < searchResults.size()) {
        const auto& result = searchResults[index];
        
        // Prefer synced lyrics if available
        QString lyrics;
        if (!result.at("syncedLyrics").empty()) {
            lyrics = QString::fromStdString(result.at("syncedLyrics"));
        } else if (!result.at("plainLyrics").empty()) {
            lyrics = QString::fromStdString(result.at("plainLyrics"));
        }
        
        lyricsPreview->setPlainText(lyrics);
        selectedLyrics = lyrics;
    }
}

void LyricsSearchDialog::onAcceptClicked() {
    if (selectedLyrics.isEmpty()) {
        QMessageBox::warning(this, "No Selection", "Please select lyrics first.");
        return;
    }
    
    accept();
}

QString LyricsSearchDialog::getSelectedLyrics() const {
    return selectedLyrics;
}
