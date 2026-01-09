#ifndef SETTINGSDIALOG_H
#define SETTINGSDIALOG_H

#include <QDialog>
#include <QComboBox>
#include <QCheckBox>
#include <QPushButton>
#include "../../core/ConfigManager.h"

class SettingsDialog : public QDialog {
    Q_OBJECT

public:
    explicit SettingsDialog(QWidget *parent = nullptr);
    ~SettingsDialog();

private slots:
    void onSaveClicked();

private:
    void setupUI();
    void loadSettings();
    
    QComboBox *coverSourceCombo;
    QCheckBox *force500Checkbox;
    QCheckBox *autoFetchLyricsCheckbox;
    QPushButton *saveButton;
    
    std::unique_ptr<ConfigManager> configManager;
};

#endif // SETTINGSDIALOG_H
