#include <QApplication>
#include "gui/MainWindow.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    
    app.setApplicationName("TagFix");
    app.setApplicationVersion("2.0.0");
    app.setOrganizationName("TagFix");
    
    MainWindow window;
    window.show();
    
    return app.exec();
}
