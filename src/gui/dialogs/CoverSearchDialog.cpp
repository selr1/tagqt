#include "CoverSearchDialog.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QPixmap>
#include <QMessageBox>

CoverSearchDialog::CoverSearchDialog(const QString& artist, const QString& album, QWidget *parent)
    : QDialog(parent), artist(artist), album(album), metadataHandler(std::make_unique<MetadataHandler>()) {
    setupUI();
    setWindowTitle("Search Cover Art");
    resize(600, 400);
}

CoverSearchDialog::~CoverSearchDialog() {}

void CoverSearchDialog::setupUI() {
    QVBoxLayout *layout = new QVBoxLayout(this);
    
    QLabel *infoLabel = new QLabel(QString("Searching for: %1 - %2").arg(artist, album), this);
    layout->addWidget(infoLabel);
    
    resultsList = new QListWidget(this);
    layout->addWidget(resultsList);
    
    QHBoxLayout *buttonLayout = new QHBoxLayout();
    searchButton = new QPushButton("Search", this);
    QPushButton *cancelButton = new QPushButton("Cancel", this);
    
    buttonLayout->addWidget(searchButton);
    buttonLayout->addWidget(cancelButton);
    
    layout->addLayout(buttonLayout);
    
    connect(searchButton, &QPushButton::clicked, this, &CoverSearchDialog::onSearchClicked);
    connect(cancelButton, &QPushButton::clicked, this, &QDialog::reject);
    connect(resultsList, &QListWidget::itemDoubleClicked, this, &CoverSearchDialog::onItemDoubleClicked);
    
    // Auto-search on open
    onSearchClicked();
}

void CoverSearchDialog::onSearchClicked() {
    resultsList->clear();
    
    std::vector<Release> releases = metadataHandler->searchReleases(
        artist.toStdString(),
        album.toStdString()
    );
    
    if (releases.empty()) {
        QMessageBox::information(this, "No Results", "No releases found.");
        return;
    }
    
    for (const Release& release : releases) {
        QString itemText = QString("%1 - %2 (%3)")
            .arg(QString::fromStdString(release.artist))
            .arg(QString::fromStdString(release.title))
            .arg(QString::fromStdString(release.date));
        
        QListWidgetItem *item = new QListWidgetItem(itemText, resultsList);
        item->setData(Qt::UserRole, QString::fromStdString(release.id));
        resultsList->addItem(item);
    }
}

void CoverSearchDialog::onItemDoubleClicked(QListWidgetItem* item) {
    QString mbid = item->data(Qt::UserRole).toString();
    
    selectedCover = metadataHandler->getCoverBytes(mbid.toStdString());
    
    if (selectedCover.empty()) {
        QMessageBox::warning(this, "Error", "Failed to download cover art.");
        return;
    }
    
    accept();
}

std::vector<unsigned char> CoverSearchDialog::getSelectedCover() const {
    return selectedCover;
}
