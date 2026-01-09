#ifndef EDITORPANEL_H
#define EDITORPANEL_H

#include <QWidget>
#include <QLineEdit>
#include <QTextEdit>
#include <QPushButton>
#include <QLabel>
#include "../core/AudioHandler.h"
#include "../core/MetadataHandler.h"

class EditorPanel : public QWidget {
    Q_OBJECT

public:
    explicit EditorPanel(QWidget *parent = nullptr);
    ~EditorPanel();

    void loadTrack(const TrackTags& tags);
    TrackTags getCurrentTags() const;

signals:
    void saveTags(const QString& filepath, const TrackTags& tags);

private slots:
    void onSaveClicked();
    void onFetchCoverClicked();
    void onFetchLyricsClicked();
    void onCoverClicked();

private:
    void setupUI();
    void updateCoverDisplay();
    
    QLineEdit *titleEdit;
    QLineEdit *artistEdit;
    QLineEdit *albumEdit;
    QLineEdit *albumArtistEdit;
    QLineEdit *yearEdit;
    QLineEdit *genreEdit;
    QTextEdit *lyricsEdit;
    QLabel *coverLabel;
    QPushButton *saveButton;
    QPushButton *fetchCoverButton;
    QPushButton *fetchLyricsButton;
    
    TrackTags currentTrack;
    std::unique_ptr<MetadataHandler> metadataHandler;
    std::vector<unsigned char> currentCoverData;
};

#endif // EDITORPANEL_H
