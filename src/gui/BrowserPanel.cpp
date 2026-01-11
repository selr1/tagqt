#include "BrowserPanel.h"
#include <QVBoxLayout>
#include <QHeaderView>
#include <QDir>

BrowserPanel::BrowserPanel(QWidget *parent) : QWidget(parent) {
    setupUI();
}

BrowserPanel::~BrowserPanel() {}

void BrowserPanel::setupUI() {
    QVBoxLayout *layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);
    
    // File system tree
    treeView = new QTreeView(this);
    fileSystemModel = new QFileSystemModel(this);
    fileSystemModel->setRootPath(QDir::rootPath());
    fileSystemModel->setFilter(QDir::Dirs | QDir::NoDotAndDotDot);
    
    treeView->setModel(fileSystemModel);
    treeView->setRootIndex(fileSystemModel->index(QDir::homePath()));
    
    // Hide extra columns (size, type, date)
    treeView->setColumnHidden(1, true);
    treeView->setColumnHidden(2, true);
    treeView->setColumnHidden(3, true);
    
    treeView->header()->setStretchLastSection(false);
    treeView->header()->setSectionResizeMode(0, QHeaderView::Stretch);
    
    layout->addWidget(treeView, 3);
    
    // Log view
    logView = new QTextEdit(this);
    logView->setReadOnly(true);
    logView->setMaximumHeight(150);
    
    layout->addWidget(logView, 1);
    
    connect(treeView, &QTreeView::clicked, this, &BrowserPanel::onDirectoryClicked);
}

void BrowserPanel::setRoot(const QString& path) {
    treeView->setRootIndex(fileSystemModel->index(path));
}

void BrowserPanel::log(const QString& message) {
    logView->append(message);
}

void BrowserPanel::onDirectoryClicked(const QModelIndex& index) {
    QString path = fileSystemModel->filePath(index);
    emit folderSelected(path);
}
