#include "SettingsDialog.h"
#include <QVBoxLayout>
#include <QFormLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QMessageBox>

SettingsDialog::SettingsDialog(QWidget *parent)
    : QDialog(parent), configManager(std::make_unique<ConfigManager>()) {
    setupUI();
    loadSettings();
    setWindowTitle("Settings");
    resize(400, 300);
}

SettingsDialog::~SettingsDialog() {}

void SettingsDialog::setupUI() {
    QVBoxLayout *layout = new QVBoxLayout(this);
    
    QFormLayout *formLayout = new QFormLayout();
    
    // Cover source
    coverSourceCombo = new QComboBox(this);
    coverSourceCombo->addItem("iTunes");
    coverSourceCombo->addItem("MusicBrainz");
    formLayout->addRow("Cover Source:", coverSourceCombo);
    
    // Force 500px
    force500Checkbox = new QCheckBox("Force 500x500 covers", this);
    formLayout->addRow("", force500Checkbox);
    
    // Auto fetch lyrics
    autoFetchLyricsCheckbox = new QCheckBox("Auto-fetch lyrics", this);
    formLayout->addRow("", autoFetchLyricsCheckbox);
    
    layout->addLayout(formLayout);
    
    // Buttons
    QHBoxLayout *buttonLayout = new QHBoxLayout();
    saveButton = new QPushButton("Save", this);
    QPushButton *cancelButton = new QPushButton("Cancel", this);
    
    buttonLayout->addStretch();
    buttonLayout->addWidget(saveButton);
    buttonLayout->addWidget(cancelButton);
    
    layout->addLayout(buttonLayout);
    
    connect(saveButton, &QPushButton::clicked, this, &SettingsDialog::onSaveClicked);
    connect(cancelButton, &QPushButton::clicked, this, &QDialog::reject);
}

void SettingsDialog::loadSettings() {
    std::string source = configManager->get("covers", "source", "iTunes");
    coverSourceCombo->setCurrentText(QString::fromStdString(source));
    
    bool force500 = configManager->getBool("covers", "force_500px", true);
    force500Checkbox->setChecked(force500);
    
    bool autoFetch = configManager->getBool("lyrics", "auto_fetch", false);
    autoFetchLyricsCheckbox->setChecked(autoFetch);
}

void SettingsDialog::onSaveClicked() {
    configManager->set("covers", "source", coverSourceCombo->currentText().toStdString());
    configManager->setBool("covers", "force_500px", force500Checkbox->isChecked());
    configManager->setBool("lyrics", "auto_fetch", autoFetchLyricsCheckbox->isChecked());
    
    if (configManager->save()) {
        QMessageBox::information(this, "Success", "Settings saved successfully!");
        accept();
    } else {
        QMessageBox::warning(this, "Error", "Failed to save settings.");
    }
}
