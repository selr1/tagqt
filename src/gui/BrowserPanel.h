#ifndef BROWSERPANEL_H
#define BROWSERPANEL_H

#include <QWidget>
#include <QTreeView>
#include <QFileSystemModel>
#include <QTextEdit>
#include <QVBoxLayout>

class BrowserPanel : public QWidget {
    Q_OBJECT

public:
    explicit BrowserPanel(QWidget *parent = nullptr);
    ~BrowserPanel();

    void setRoot(const QString& path);
    void log(const QString& message);

signals:
    void folderSelected(const QString& path);

private slots:
    void onDirectoryClicked(const QModelIndex& index);

private:
    void setupUI();
    
    QTreeView *treeView;
    QFileSystemModel *fileSystemModel;
    QTextEdit *logView;
};

#endif // BROWSERPANEL_H
