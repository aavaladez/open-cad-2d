#include "session.h"
#include <QJsonArray>
#include <QFileInfo>
#include <QRegularExpression>
#include <cmath>
#include <stdexcept>
#include "RDocument.h"
#include "RMemoryStorage.h"
#include "RSpatialIndexSimple.h"
#include "RSettings.h"
#include "RMath.h"
#include "RDocumentVariables.h"
#include "RDimStyle.h"
#include "RDimStyleData.h"
#include "RLayerState.h"
#include "RLayout.h"
#include "RLinetype.h"
#include "RBlock.h"
#include "RUcs.h"
#include "RView.h"
#include "RLineEntity.h"
#include "RCircleEntity.h"
#include "ROperation.h"
#include "RDxfImporterFactory.h"
#include "RDxfExporterFactory.h"

namespace {
void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}
double number(const QJsonValue& v) {
    require(v.isDouble() && std::isfinite(v.toDouble()),"Finite number required");
    return v.toDouble();
}
RVector point(const QJsonValue& v) {
    require(v.isArray() && v.toArray().size()==3,"XYZ point required");
    auto a = v.toArray(); return {number(a[0]),number(a[1]),number(a[2])};
}
QJsonArray xyz(const RVector& p) { return {p.x,p.y,p.z}; }
std::unique_ptr<RDocumentInterface> emptyDocument() {
    return std::make_unique<RDocumentInterface>(*new RDocument(*new RMemoryStorage(),*new RSpatialIndexSimple()));
}

// Staged objects use QCAD shapes. One low-level transaction confirms the entire
// command/LSP batch; discarded staging never changes the live undo/redo history.
class BatchOperation final : public ROperation {
public:
    QMap<int,QSharedPointer<REntity>> entities;
    QMap<QString,QSharedPointer<RLayer>> layers;
    QMap<int,QString> entityLayers;
    QSet<int> dirtyEntities;
    QSet<QString> dirtyLayers;
    QString currentLayer;
    RTransaction apply(RDocument& doc, bool preview) override {
        RTransaction transaction(doc.getStorage(),QStringLiteral("OPEN CAD command/LSP"),true);
        // Layer permissions were checked for every staged edit. Final lock flags
        // can differ from the flags at the time of a permitted edit in the batch.
        transaction.setAllowAll(true);
        for (const auto& name : dirtyLayers) transaction.addObject(layers[name],false);
        for (auto id : dirtyEntities) {
            if (entities.contains(id)) {
                auto entity = entities[id];
                entity->setLayerId(doc.getLayerId(entityLayers[id]));
                transaction.addObject(entity,false);
            } else if (id>=0) transaction.deleteObject(doc.queryEntity(id));
        }
        doc.setCurrentLayer(currentLayer,&transaction);
        if (preview) transaction.fail();
        transaction.end(); return transaction;
    }
};
}

CadSession::CadSession() {
    RSettings::setNoWrite(true);
    RMath::init(); RDimStyleData::initDefaults(); RObject::init(); REntity::init();
    RDocumentVariables::init(); RDimStyle::init(); RLayer::init(); RLayerState::init();
    RLayout::init(); RLinetype::init(); RBlock::init(); RUcs::init(); RView::init();
    RLineEntity::init(); RCircleEntity::init();
    RDxfImporterFactory::registerFileImporter(); RDxfExporterFactory::registerFileExporter();
    interface = emptyDocument(); refresh();
}
RDocument& CadSession::document() { return interface->getDocument(); }
void CadSession::refresh() {
    entities.clear(); layers.clear(); entityLayers.clear();
    auto& doc = document();
    for (auto id : doc.queryAllLayers()) {
        auto layer = doc.queryLayer(id); layers[layer->getName()] = layer->cloneToLayer();
    }
    currentLayer = doc.queryLayer(doc.getCurrentLayerId())->getName();
    for (auto id : doc.queryAllEntities()) {
        auto entity = doc.queryEntity(id);
        require(entity->getType()==RS::EntityLine || entity->getType()==RS::EntityCircle,"Unsupported entity in adapter");
        entities[id] = entity->cloneToEntity(); entityLayers[id] = doc.queryLayer(entity->getLayerId())->getName();
    }
    dirtyEntities.clear(); dirtyLayers.clear();
}
void CadSession::begin() {
    require(!editing,"Transaction already active"); refresh(); editing = true; virtualId = -2;
}
void CadSession::writable(const QString& name) {
    require(layers.contains(name),"Unknown layer");
    require(!layers[name]->isLocked(),"Layer locked");
}
QJsonObject CadSession::commit() {
    require(editing,"No active transaction");
    QJsonObject ids;
    if (!dirtyEntities.isEmpty() || !dirtyLayers.isEmpty() ||
        currentLayer!=document().queryLayer(document().getCurrentLayerId())->getName()) {
        auto op = new BatchOperation();
        op->entities=entities; op->layers=layers; op->entityLayers=entityLayers;
        op->dirtyEntities=dirtyEntities; op->dirtyLayers=dirtyLayers; op->currentLayer=currentLayer;
        auto result = interface->applyOperation(op);
        require(!result.isFailed(),"QCAD transaction failed");
        for (auto id : entities.keys()) if (id<0) ids[QString::number(id)] = entities[id]->getId();
    }
    editing=false; refresh(); return ids;
}
QJsonObject CadSession::snapshot() {
    QJsonArray list,layerList;
    for (auto id : entities.keys()) {
        auto e=entities[id];
        QJsonObject item{{"id",id},{"layer",entityLayers[id]}};
        auto line=e.dynamicCast<RLineEntity>(); auto circle=e.dynamicCast<RCircleEntity>();
        if (line) {
            item["type"]="LINE"; item["start"]=xyz(line->getStartPoint()); item["end"]=xyz(line->getEndPoint());
        } else {
            item["type"]="CIRCLE"; item["center"]=xyz(circle->getCenter()); item["radius"]=circle->getRadius();
        }
        list.append(item);
    }
    for (const auto& name : layers.keys()) {
        auto layer=layers[name];
        const auto color=layer->getColor();
        layerList.append(QJsonObject{{"name",name},{"color",color.name()},
            {"display_color",color.getColorIndex()==7 ? QStringLiteral("#d6e2ec") : color.name()},
            {"visible",!layer->isOff() && !layer->isFrozen()},{"locked",layer->isLocked()}});
    }
    return {{"entities",list},{"layers",layerList},{"current_layer",currentLayer},{"units",int(document().getUnit())}};
}
QJsonObject CadSession::request(const QJsonObject& input) {
    const QString action=input["action"].toString();
    QJsonValue value;
    if (action=="hello") value=QJsonObject{{"protocol",1},{"engine","qcad"},
        {"revision","4c830eb4d80285ca64b1f2c2dc0987f729344126"}};
    else if (action=="snapshot") {}
    else if (action=="begin") begin();
    else if (action=="rollback") { require(editing,"No transaction"); editing=false; refresh(); }
    else if (action=="commit") value=commit();
    else if (action=="undo" || action=="redo") {
        require(!editing,"History cannot change during a transaction");
        if (action=="undo") interface->undo(); else interface->redo(); refresh();
    } else if (action=="load") {
        require(!editing,"Cannot import during a transaction");
        QString path=input["path"].toString();
        require(QFileInfo(path).isFile() && !path.contains("://"),"Existing local file required");
        auto temporary=emptyDocument();
        require(temporary->importFile(path)==RDocumentInterface::IoErrorNoError,"DXF import failed");
        for (auto id : temporary->getDocument().queryAllEntities()) {
            auto e=temporary->getDocument().queryEntity(id);
            require(e->getType()==RS::EntityLine || e->getType()==RS::EntityCircle,"Unsupported DXF entity");
        }
        interface.swap(temporary); refresh();
    } else if (action=="save") {
        require(!editing,"Cannot export during a transaction");
        QString path=input["path"].toString();
        require(!path.isEmpty() && !path.contains("://") && !QFileInfo::exists(path),"New local output required");
        require(interface->exportFile(path),"DXF export failed");
    } else {
        require(editing,"Edit requires transaction");
        if (action=="line" || action=="circle") {
            writable(currentLayer);
            QSharedPointer<REntity> e;
            if (action=="line") {
                auto a=point(input["start"]), b=point(input["end"]);
                require(!a.equalsFuzzy(b),"Zero length line"); e.reset(new RLineEntity(&document(),RLineData(a,b)));
            } else {
                double radius=number(input["radius"]); require(radius>0,"Positive radius required");
                e.reset(new RCircleEntity(&document(),RCircleData(point(input["center"]),radius)));
            }
            e->setColor(RColor(RColor::ByLayer)); e->setLinetypeId(document().getLinetypeId("BYLAYER"));
            e->setBlockId(document().getCurrentBlockId());
            int id=virtualId--; entities[id]=e; entityLayers[id]=currentLayer; dirtyEntities.insert(id); value=id;
        } else if (action=="move" || action=="erase") {
            require(input["ids"].isArray() && !input["ids"].toArray().isEmpty(),"Selection required");
            QSet<int> ids;
            for (auto v : input["ids"].toArray()) {
                double n=number(v); require(n==v.toInt() && entities.contains(v.toInt()),"Unknown entity ID");
                ids.insert(v.toInt()); writable(entityLayers[v.toInt()]);
            }
            RVector delta;
            if (action=="move") delta=point(input["delta"]);
            for (int id : ids) {
                if (action=="move") require(entities[id]->move(delta),"QCAD move failed");
                else entities.remove(id);
                dirtyEntities.insert(id);
            }
        } else if (action=="layer") {
            QString mode=input["mode"].toString().toUpper(), name=input["name"].toString();
            require(!name.isEmpty() && !name.contains(QRegularExpression("[<>/\\\\\":;?*|=]")),"Invalid layer name");
            if (mode=="NEW") {
                require(!layers.contains(name),"Layer already exists");
                layers[name].reset(new RLayer(&document(),name,false,false,RColor(QStringLiteral("#d6e2ec"))));
                dirtyLayers.insert(name);
            } else {
                require(layers.contains(name),"Unknown layer");
                if (mode=="SET") currentLayer=name;
                else {
                    require(!layers[name]->isProtected(),"Layer protected");
                    if (mode=="LOCK" || mode=="UNLOCK") layers[name]->setLocked(mode=="LOCK");
                    else if (mode=="ON" || mode=="OFF") layers[name]->setOff(mode=="OFF");
                    else throw std::runtime_error("Unknown layer option");
                    dirtyLayers.insert(name);
                }
            }
        } else throw std::runtime_error("Unknown adapter action");
    }
    return {{"ok",true},{"value",value},{"document",snapshot()}};
}
