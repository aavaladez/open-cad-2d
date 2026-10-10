// Original OPEN CAD adapter: QCAD is the authoritative document and geometry.
#pragma once
#include <QJsonObject>
#include <QMap>
#include <QSet>
#include <memory>
#include "RDocumentInterface.h"
#include "REntity.h"
#include "RLayer.h"

class CadSession {
public:
    CadSession();
    QJsonObject request(const QJsonObject& input);
private:
    std::unique_ptr<RDocumentInterface> interface;
    QMap<int,QSharedPointer<REntity>> entities;
    QMap<QString,QSharedPointer<RLayer>> layers;
    QMap<int,QString> entityLayers;
    QSet<int> dirtyEntities;
    QSet<QString> dirtyLayers;
    QString currentLayer;
    bool editing = false;
    int virtualId = -2;
    RDocument& document();
    void refresh();
    void begin();
    QJsonObject commit();
    QJsonObject snapshot();
    void writable(const QString& layer);
};
