#ifndef TRACKTABLE_H
#define TRACKTABLE_H

#include <QWidget>
#include <QTreeWidget>
#include <QVBoxLayout>
#include "../core/AudioHandler.h"

class TrackTable : public QWidget {
    Q_OBJECT

public:
    explicit TrackTable(QWidget *parent = nullptr);
    ~TrackTable();

    void clear();
    QString addTrack(const TrackTags& tags);
    void refreshRow(const QString& filepath);

signals:
    void trackSelected(const QString& filepath);
    void refreshRequested();

private slots:
    void onSelectionChanged();

private:
    QTreeWidget *tree;
    std::map<QString, QString> fileToItemMap; // filepath -> item id
};

#endif // TRACKTABLE_H
