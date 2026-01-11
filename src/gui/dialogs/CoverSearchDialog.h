#ifndef COVERSEARCHDIALOG_H
#define COVERSEARCHDIALOG_H

#include <QDialog>
#include <QListWidget>
#include <QPushButton>
#include "../../core/MetadataHandler.h"

class CoverSearchDialog : public QDialog {
    Q_OBJECT

public:
    explicit CoverSearchDialog(const QString& artist, const QString& album, QWidget *parent = nullptr);
    ~CoverSearchDialog();

    std::vector<unsigned char> getSelectedCover() const;

private slots:
    void onSearchClicked();
    void onItemDoubleClicked(QListWidgetItem* item);

private:
    void setupUI();
    
    QString artist;
    QString album;
    QListWidget *resultsList;
    QPushButton *searchButton;
    
    std::unique_ptr<MetadataHandler> metadataHandler;
    std::vector<unsigned char> selectedCover;
};

#endif // COVERSEARCHDIALOG_H
