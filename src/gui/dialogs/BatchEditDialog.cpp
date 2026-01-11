#include "BatchEditDialog.h"
#include <QVBoxLayout>
#include <QFormLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QMessageBox>
#include <QProgressDialog>
#include <QFileInfo>

BatchEditDialog::BatchEditDialog(const std::vector<QString>& filepaths, QWidget *parent)
    : QDialog(parent), filepaths(filepaths), audioHandler(std::make_unique<AudioHandler>()) {
    setupUI();
    setWindowTitle("Batch Edit");
    resize(500, 400);
}

BatchEditDialog::~BatchEditDialog() {}

void BatchEditDialog::setupUI() {
    QVBoxLayout *layout = new QVBoxLayout(this);
    
    QLabel *infoLabel = new QLabel(QString("Editing %1 files").arg(filepaths.size()), this);
    layout->addWidget(infoLabel);
    
    // File list
    fileList = new QListWidget(this);
    for (const QString& filepath : filepaths) {
        QFileInfo info(filepath);
        fileList->addItem(info.fileName());
    }
    layout->addWidget(fileList);
    
    // Edit fields with checkboxes
    QFormLayout *formLayout = new QFormLayout();
    
    QHBoxLayout *artistLayout = new QHBoxLayout();
    artistCheckbox = new QCheckBox(this);
    artistEdit = new QLineEdit(this);
    artistLayout->addWidget(artistCheckbox);
    artistLayout->addWidget(artistEdit);
    formLayout->addRow("Artist:", artistLayout);
    
    QHBoxLayout *albumLayout = new QHBoxLayout();
    albumCheckbox = new QCheckBox(this);
    albumEdit = new QLineEdit(this);
    albumLayout->addWidget(albumCheckbox);
    albumLayout->addWidget(albumEdit);
    formLayout->addRow("Album:", albumLayout);
    
    QHBoxLayout *albumArtistLayout = new QHBoxLayout();
    albumArtistCheckbox = new QCheckBox(this);
    albumArtistEdit = new QLineEdit(this);
    albumArtistLayout->addWidget(albumArtistCheckbox);
    albumArtistLayout->addWidget(albumArtistEdit);
    formLayout->addRow("Album Artist:", albumArtistLayout);
    
    QHBoxLayout *yearLayout = new QHBoxLayout();
    yearCheckbox = new QCheckBox(this);
    yearEdit = new QLineEdit(this);
    yearLayout->addWidget(yearCheckbox);
    yearLayout->addWidget(yearEdit);
    formLayout->addRow("Year:", yearLayout);
    
    QHBoxLayout *genreLayout = new QHBoxLayout();
    genreCheckbox = new QCheckBox(this);
    genreEdit = new QLineEdit(this);
    genreLayout->addWidget(genreCheckbox);
    genreLayout->addWidget(genreEdit);
    formLayout->addRow("Genre:", genreLayout);
    
    layout->addLayout(formLayout);
    
    // Buttons
    QHBoxLayout *buttonLayout = new QHBoxLayout();
    applyButton = new QPushButton("Apply", this);
    QPushButton *cancelButton = new QPushButton("Cancel", this);
    
    buttonLayout->addStretch();
    buttonLayout->addWidget(applyButton);
    buttonLayout->addWidget(cancelButton);
    
    layout->addLayout(buttonLayout);
    
    connect(applyButton, &QPushButton::clicked, this, &BatchEditDialog::onApplyClicked);
    connect(cancelButton, &QPushButton::clicked, this, &QDialog::reject);
}

void BatchEditDialog::onApplyClicked() {
    applyChanges();
}

void BatchEditDialog::applyChanges() {
    QProgressDialog progress("Applying changes...", "Cancel", 0, filepaths.size(), this);
    progress.setWindowModality(Qt::WindowModal);
    
    int successCount = 0;
    int failCount = 0;
    
    for (size_t i = 0; i < filepaths.size(); ++i) {
        if (progress.wasCanceled()) {
            break;
        }
        
        const QString& filepath = filepaths[i];
        TrackTags tags = audioHandler->getTags(filepath.toStdString());
        
        // Apply checked fields
        if (artistCheckbox->isChecked()) {
            tags.artist = artistEdit->text().toStdString();
        }
        if (albumCheckbox->isChecked()) {
            tags.album = albumEdit->text().toStdString();
        }
        if (albumArtistCheckbox->isChecked()) {
            tags.albumArtist = albumArtistEdit->text().toStdString();
        }
        if (yearCheckbox->isChecked()) {
            tags.year = yearEdit->text().toStdString();
        }
        if (genreCheckbox->isChecked()) {
            tags.genre = genreEdit->text().toStdString();
        }
        
        if (audioHandler->saveTags(filepath.toStdString(), tags)) {
            successCount++;
        } else {
            failCount++;
        }
        
        progress.setValue(i + 1);
    }
    
    QString message = QString("Successfully updated %1 files.").arg(successCount);
    if (failCount > 0) {
        message += QString("\nFailed to update %1 files.").arg(failCount);
    }
    
    QMessageBox::information(this, "Batch Edit Complete", message);
    accept();
}
