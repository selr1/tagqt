#ifndef BATCHEDITDIALOG_H
#define BATCHEDITDIALOG_H

#include <QDialog>
#include <QLineEdit>
#include <QCheckBox>
#include <QPushButton>
#include <QListWidget>
#include "../../core/AudioHandler.h"

class BatchEditDialog : public QDialog {
    Q_OBJECT

public:
    explicit BatchEditDialog(const std::vector<QString>& filepaths, QWidget *parent = nullptr);
    ~BatchEditDialog();

private slots:
    void onApplyClicked();

private:
    void setupUI();
    void applyChanges();
    
    std::vector<QString> filepaths;
    QLineEdit *artistEdit;
    QLineEdit *albumEdit;
    QLineEdit *albumArtistEdit;
    QLineEdit *yearEdit;
    QLineEdit *genreEdit;
    QCheckBox *artistCheckbox;
    QCheckBox *albumCheckbox;
    QCheckBox *albumArtistCheckbox;
    QCheckBox *yearCheckbox;
    QCheckBox *genreCheckbox;
    QPushButton *applyButton;
    QListWidget *fileList;
    
    std::unique_ptr<AudioHandler> audioHandler;
};

#endif // BATCHEDITDIALOG_H
