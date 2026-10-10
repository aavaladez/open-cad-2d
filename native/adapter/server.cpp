// Local pipes only, explicit action dispatch; never shell/script/plugin evaluation.
#include <QApplication>
#include <QJsonDocument>
#include <QJsonParseError>
#include <iostream>
#include <string>
#include "session.h"

int main(int argc,char** argv) {
    QApplication app(argc,argv);
    app.setOrganizationName("OPEN CAD Contributors");
    app.setApplicationName("OpenCADNative");
    try {
        CadSession session;
        std::string line;
        while (std::getline(std::cin,line)) {
            QJsonObject response;
            try {
                if (line.size()>1000000) throw std::runtime_error("Request too large");
                QJsonParseError error;
                auto parsed=QJsonDocument::fromJson(QByteArray::fromStdString(line),&error);
                if (error.error!=QJsonParseError::NoError || !parsed.isObject()) throw std::runtime_error("Invalid JSON request");
                response=session.request(parsed.object());
            } catch (const std::exception& e) {
                response={{"ok",false},{"error",QString::fromUtf8(e.what())}};
            }
            std::cout << QJsonDocument(response).toJson(QJsonDocument::Compact).constData() << std::endl;
        }
        return 0;
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
