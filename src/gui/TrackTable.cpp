#include "TrackTable.h"
#include <QHeaderView>
#include <QTreeWidgetItem>

TrackTable::TrackTable(QWidget *parent) : QWidget(parent) {
    QVBoxLayout *layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);
    
    tree = new QTreeWidget(this);
    tree->setAlternatingRowColors(true);
    tree->setSelectionMode(QAbstractItemView::ExtendedSelection);
    
    // Set up columns
    QStringList headers;
    headers << "Filename" << "Title" << "Artist" << "Album" << "Year" << "Genre" << "Duration" << "Cover" << "Lyrics";
    tree->setHeaderLabels(headers);
    
    // Set column widths
    tree->setColumnWidth(0, 150);
    tree->setColumnWidth(1, 150);
    tree->setColumnWidth(2, 120);
    tree->setColumnWidth(3, 150);
    tree->setColumnWidth(4, 60);
    tree->setColumnWidth(5, 100);
    tree->setColumnWidth(6, 80);
    tree->setColumnWidth(7, 60);
    tree->setColumnWidth(8, 60);
    
    layout->addWidget(tree);
    
    connect(tree, &QTreeWidget::itemSelectionChanged, this, &TrackTable::onSelectionChanged);
}

TrackTable::~TrackTable() {}

void TrackTable::clear() {
    tree->clear();
    fileToItemMap.clear();
}

QString TrackTable::addTrack(const TrackTags& tags) {
    QTreeWidgetItem *item = new QTreeWidgetItem(tree);
    
    item->setText(0, QString::fromStdString(tags.filename));
    item->setText(1, QString::fromStdString(tags.title));
    item->setText(2, QString::fromStdString(tags.artist));
    item->setText(3, QString::fromStdString(tags.album));
    item->setText(4, QString::fromStdString(tags.year));
    item->setText(5, QString::fromStdString(tags.genre));
    
    // Format duration
    int minutes = (int)tags.duration / 60;
    int seconds = (int)tags.duration % 60;
    item->setText(6, QString("%1:%2").arg(minutes).arg(seconds, 2, 10, QChar('0')));
    
    // Cover status
    QString coverStatus;
    if (tags.coverStatus == 0) coverStatus = "-";
    else if (tags.coverStatus == 1) coverStatus = "✓";
    else if (tags.coverStatus == 2) coverStatus = "✓✓";
    item->setText(7, coverStatus);
    
    // Lyrics status
    QString lyricsStatus;
    if (tags.lyricsStatus == 0) lyricsStatus = "-";
    else if (tags.lyricsStatus == 1) lyricsStatus = "T";
    else if (tags.lyricsStatus == 2) lyricsStatus = "S";
    item->setText(8, lyricsStatus);
    
    QString filepath = QString::fromStdString(tags.path);
    item->setData(0, Qt::UserRole, filepath);
    
    fileToItemMap[filepath] = QString::number((quintptr)item);
    
    tree->addTopLevelItem(item);
    
    return QString::number((quintptr)item);
}

void TrackTable::refreshRow(const QString& filepath) {
    // Find the item and emit refresh signal
    emit refreshRequested();
}

void TrackTable::onSelectionChanged() {
    QList<QTreeWidgetItem*> selected = tree->selectedItems();
    if (!selected.isEmpty()) {
        QString filepath = selected[0]->data(0, Qt::UserRole).toString();
        emit trackSelected(filepath);
    }
}
