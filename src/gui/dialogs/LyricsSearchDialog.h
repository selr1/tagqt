#ifndef LYRICSSEARCHDIALOG_H
#define LYRICSSEARCHDIALOG_H

#include <QDialog>
#include <QListWidget>
#include <QTextEdit>
#include <QPushButton>
#include "../../core/MetadataHandler.h"

class LyricsSearchDialog : public QDialog {
    Q_OBJECT

public:
    explicit LyricsSearchDialog(const QString& artist, const QString& title, const QString& album, QWidget *parent = nullptr);
    ~LyricsSearchDialog();

    QString getSelectedLyrics() const;

private slots:
    void onSearchClicked();
    void onResultSelected(QListWidgetItem* item);
    void onAcceptClicked();

private:
    void setupUI();
    
    QString artist;
    QString title;
    QString album;
    QListWidget *resultsList;
    QTextEdit *lyricsPreview;
    QPushButton *searchButton;
    QPushButton *acceptButton;
    
    std::unique_ptr<MetadataHandler> metadataHandler;
    QString selectedLyrics;
    std::vector<std::map<std::string, std::string>> searchResults;
};

#endif // LYRICSSEARCHDIALOG_H
