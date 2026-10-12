#include "session.h"
#include "geometry_ops.h"
#include "dimensions.h"
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
#include "RArcEntity.h"
#include "RPolylineEntity.h"
#include "RDimAlignedEntity.h"
#include "RDimRotatedEntity.h"
#include "RDimRadialEntity.h"
#include "RDimStyleProxyBasic.h"
#include "ROperation.h"
#include "RAddObjectOperation.h"
#include "RBox.h"
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
bool finitePoint(const RVector& p) { return std::isfinite(p.x) && std::isfinite(p.y) && std::isfinite(p.z); }
bool supported(const QSharedPointer<REntity>& e) {
    return e->getType()==RS::EntityLine || e->getType()==RS::EntityCircle ||
        e->getType()==RS::EntityArc || e->getType()==RS::EntityPolyline || CadDimensions::supported(e);
}
QList<RVector> vertices(const QJsonValue& value) {
    require(value.isArray(),"Vertex array required");
    QList<RVector> result;
    for (const auto& v : value.toArray()) result.append(point(v));
    return result;
}
double angle(const QJsonValue& value) { return RMath::getNormalizedAngle(RMath::deg2rad(number(value))); }
void validGeometry(const QSharedPointer<REntity>& e) {
    if (auto line=e.dynamicCast<RLineEntity>())
        require(finitePoint(line->getStartPoint()) && finitePoint(line->getEndPoint()) &&
            !line->getStartPoint().equalsFuzzy(line->getEndPoint()),"Invalid transformed line");
    else if (auto c=e.dynamicCast<RCircleEntity>()) require(finitePoint(c->getCenter()) &&
        std::isfinite(c->getRadius()) && c->getRadius()>0,"Invalid transformed circle");
    else if (auto a=e.dynamicCast<RArcEntity>()) require(finitePoint(a->getCenter()) &&
        std::isfinite(a->getRadius()) && a->getRadius()>0 && std::isfinite(a->getStartAngle()) &&
        std::isfinite(a->getEndAngle()) && !a->getData().isFullCircle() &&
        std::abs(a->getData().getSweep())>RS::AngleTolerance,"Invalid or full-circle arc");
    else if (auto p=e.dynamicCast<RPolylineEntity>()) {
        const auto& data=p->getData(); auto vs=data.getVertices();
        require(vs.size()>=(data.isClosed()?3:2) && !data.hasArcSegments() && !data.hasWidths() &&
            !p->getPolylineGen(),"Only straight, zero-width polylines supported");
        for (int i=0;i<vs.size();++i) {
            require(finitePoint(vs[i]) && std::abs(vs[i].z-vs[0].z)<=1e-9,"Planar finite vertices required");
            if (i+1<vs.size() || data.isClosed()) require(
                vs[i].get2D().getDistanceTo(vs[(i+1)%vs.size()].get2D())>1e-9,"Degenerate polyline segment");
        }
    } else if (CadDimensions::supported(e)) CadDimensions::validate(e);
    else throw std::runtime_error("Unsupported geometry");
}
std::unique_ptr<RDocumentInterface> emptyDocument() {
    auto result=std::make_unique<RDocumentInterface>(*new RDocument(*new RMemoryStorage(),*new RSpatialIndexSimple()));
    auto& doc=result->getDocument();
    // CE always exports Defpoints. Make that standard layer explicit from the
    // start, so a fresh document and its saved inventory describe the same data.
    QSharedPointer<RLayer> layer(new RLayer(&doc,QStringLiteral("Defpoints"),false,false,RColor(Qt::white),
        doc.getLinetypeId(QStringLiteral("CONTINUOUS")),RLineweight::WeightByLwDefault));
    auto transaction=result->applyOperation(new RAddObjectOperation(layer,QStringLiteral("Default layer"),false,false));
    require(!transaction.isFailed(),"Default layer initialization failed");
    result->flushTransactions();
    return result;
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
                if (CadDimensions::supported(entity)) transaction.addObject(entity,false,false,CadDimensions::transactionProperties(entity));
                else transaction.addObject(entity,false);
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
    RLineEntity::init(); RCircleEntity::init(); RArcEntity::init(); RPolylineEntity::init();
    RDimensionEntity::init(); RDimLinearEntity::init();
    RDimAlignedEntity::init(); RDimRotatedEntity::init(); RDimRadialEntity::init();
    RDimStyle::setDimStyleProxy(new RDimStyleProxyBasic());
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
        require(supported(entity),"Unsupported entity in adapter");
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
    for (int id : dirtyEntities) if (entities.contains(id)) validGeometry(entities[id]);
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
        item["color_index"]=e->getColor().getColorIndex();
        item["linetype"]=document().getLinetypeName(e->getLinetypeId());
        item["lineweight"]=int(e->getLineweight());
        item["ltscale"]=e->getLinetypeScale();
        auto line=e.dynamicCast<RLineEntity>(); auto circle=e.dynamicCast<RCircleEntity>();
        if (line) {
            item["type"]="LINE"; item["start"]=xyz(line->getStartPoint()); item["end"]=xyz(line->getEndPoint());
        } else if (circle) {
            item["type"]="CIRCLE"; item["center"]=xyz(circle->getCenter()); item["radius"]=circle->getRadius();
        } else if (auto arc=e.dynamicCast<RArcEntity>()) {
            item["type"]="ARC"; item["center"]=xyz(arc->getCenter()); item["radius"]=arc->getRadius();
            item["start_angle"]=RMath::rad2deg(RMath::getNormalizedAngle(arc->isReversed()?arc->getEndAngle():arc->getStartAngle()));
            item["end_angle"]=RMath::rad2deg(RMath::getNormalizedAngle(arc->isReversed()?arc->getStartAngle():arc->getEndAngle()));
        } else if (auto poly=e.dynamicCast<RPolylineEntity>()) {
            QJsonArray vs; for (const auto& p : poly->getData().getVertices()) vs.append(xyz(p));
            item["type"]="LWPOLYLINE"; item["vertices"]=vs; item["closed"]=poly->getData().isClosed();
        } else if (CadDimensions::supported(e)) {
            const auto dim=CadDimensions::snapshot(e); for (auto key : dim.keys()) item[key]=dim[key];
        } else throw std::runtime_error("Unsupported snapshot geometry");
        list.append(item);
    }
    for (const auto& name : layers.keys()) {
        auto layer=layers[name];
        const auto color=layer->getColor();
        layerList.append(QJsonObject{{"name",name},{"color",color.name()},
            {"color_index",color.getColorIndex()},{"frozen",layer->isFrozen()},
            {"linetype",document().getLinetypeName(layer->getLinetypeId())},
            {"lineweight",int(layer->getLineweight())},
            {"display_color",color.getColorIndex()==7 ? QStringLiteral("#d6e2ec") : color.name()},
            {"visible",!layer->isOff() && !layer->isFrozen()},{"locked",layer->isLocked()}});
    }
    return {{"entities",list},{"layers",layerList},{"current_layer",currentLayer},{"units",int(document().getUnit())},{"transaction_active",editing}};
}
QJsonObject CadSession::request(const QJsonObject& input) {
    const QString action=input["action"].toString();
    QJsonValue value;
    if (action=="hello") value=QJsonObject{{"protocol",1},{"engine","qcad"},
        {"revision","4c830eb4d80285ca64b1f2c2dc0987f729344126"}};
    else if (action=="snapshot") {}
    else if (action=="select") {
        require(!editing,"Selection during staging is not supported");
        QString mode=input["mode"].toString();
        require(mode=="point" || mode=="window" || mode=="crossing","Unknown selection mode");
        auto a=point(input["a"]).get2D();
        RBox box;
        double best=0; int nearest=-1;
        if (mode=="point") { best=number(input["tolerance"]); require(best>0,"Positive tolerance required"); }
        else { box=RBox(a,point(input["b"]).get2D()); require(box.getWidth()>0 && box.getHeight()>0,"Selection area required"); }
        QJsonArray selected;
        for (int id : entities.keys()) {
            auto e=entities[id]; auto layer=layers[entityLayers[id]];
            if (layer->isOff() || layer->isFrozen()) continue;
            // Picking is evaluated in displayed XY; source XYZ remains untouched.
            auto parts=CadDimensions::supported(e) ? CadDimensions::shapes(e) : QList<QSharedPointer<RShape>>{CadGeometry::projected(e)};
            RBox bounds; for (const auto& part : parts) bounds.growToInclude(part->getBoundingBox());
            if (mode=="point") {
                double distance=INFINITY; for (const auto& part : parts) distance=(std::min)(distance,part->getDistanceTo(a));
                if (distance<best) { best=distance; nearest=id; }
            } else {
                bool hit=box.contains(bounds);
                if (mode=="crossing") for (const auto& part : parts) hit=hit || box.intersectsWith(*part);
                if (hit) selected.append(id);
            }
        }
        if (mode=="point" && nearest>=0) selected.append(nearest);
        value=selected;
    }
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
            require(supported(e),"Unsupported DXF entity"); validGeometry(e);
        }
        if (input.contains("current_layer")) {
            QString name=input["current_layer"].toString();
            auto& imported=temporary->getDocument();
            require(imported.getLayerId(name)!=RObject::INVALID_ID,"Unknown imported current layer");
            imported.setCurrentLayer(name);
        }
        if (input.contains("original_path")) {
            QString original=input["original_path"].toString();
            require(QFileInfo(original).isFile() && !original.contains("://"),"Existing original local DXF path required");
            temporary->getDocument().setFileName(original);
        }
        interface.swap(temporary); refresh();
    } else if (action=="save") {
        require(!editing,"Cannot export during a transaction");
        QString path=input["path"].toString();
        require(!path.isEmpty() && !path.contains("://") && !QFileInfo::exists(path),"New local output required");
        auto fileName=document().getFileName();
        bool success=interface->exportFile(path,QString(),false);
        document().setFileName(fileName);
        require(success,"DXF export failed");
    } else {
        require(editing,"Edit requires transaction");
        if (action=="line" || action=="circle" || action=="arc" || action=="pline" || action=="dimension") {
            writable(currentLayer);
            QSharedPointer<REntity> e;
            if (action=="line") {
                auto a=point(input["start"]), b=point(input["end"]);
                require(!a.equalsFuzzy(b),"Zero length line"); e.reset(new RLineEntity(&document(),RLineData(a,b)));
            } else if (action=="circle") {
                double radius=number(input["radius"]); require(radius>0,"Positive radius required");
                e.reset(new RCircleEntity(&document(),RCircleData(point(input["center"]),radius)));
            } else if (action=="arc") {
                RArc arc;
                if (input.contains("points")) {
                    auto vs=vertices(input["points"]); require(vs.size()==3,"Three arc points required");
                    require(std::abs(vs[0].z-vs[1].z)<=1e-9 && std::abs(vs[0].z-vs[2].z)<=1e-9,"Planar arc required");
                    arc=RArc::createFrom3Points(vs[0].get2D(),vs[1].get2D(),vs[2].get2D());
                    require(arc.isValid(),"Collinear or coincident arc points"); arc.setZ(vs[0].z);
                    // DXF stores the same geometric arc counterclockwise. Endpoint
                    // traversal is deliberately not a persisted entity attribute.
                    if (arc.isReversed()) { double start=arc.getStartAngle(); arc.setStartAngle(arc.getEndAngle()); arc.setEndAngle(start); arc.setReversed(false); }
                } else arc=RArc(point(input["center"]),number(input["radius"]),angle(input["start_angle"]),angle(input["end_angle"]),false);
                e.reset(new RArcEntity(&document(),RArcData(arc)));
            } else if (action=="pline") {
                require(input["closed"].isBool(),"Boolean closure required");
                RPolyline poly; poly.setVertices(vertices(input["vertices"])); poly.setClosed(input["closed"].toBool());
                RPolylineData data(poly); data.setPolylineGen(false);
                e.reset(new RPolylineEntity(&document(),data));
            } else {
                auto parameters=input;
                if (input.contains("source")) {
                    double n=number(input["source"]); int source=input["source"].toInt();
                    require(n==source && entities.contains(source),"Unknown dimension source");
                    auto c=entities[source].dynamicCast<RCircleEntity>(); auto a=entities[source].dynamicCast<RArcEntity>();
                    require(c || a,"DIMRADIUS source must be CIRCLE/ARC");
                    auto center=c ? c->getCenter() : a->getCenter();
                    auto chord=CadGeometry::projected(entities[source])->getClosestPointOnShape(point(input["picked"]).get2D()); chord.z=center.z;
                    require(chord.isValid(),"Invalid radius pick"); parameters["position"]=xyz(center); parameters["chord"]=xyz(chord);
                }
                e=CadDimensions::create(document(),parameters);
            }
            validGeometry(e);
            e->setColor(RColor(RColor::ByLayer)); e->setLinetypeId(document().getLinetypeId("BYLAYER"));
            e->setBlockId(document().getCurrentBlockId());
            int id=virtualId--; entities[id]=e; entityLayers[id]=currentLayer; dirtyEntities.insert(id); value=id;
        } else if (action=="trim" || action=="extend" || action=="offset") {
            double n=number(input["id"]); int id=input["id"].toInt();
            require(n==id && entities.contains(id),"Unknown target entity"); writable(entityLayers[id]);
            if (action=="offset") {
                auto created=CadGeometry::offset(entities[id],number(input["distance"]),point(input["side"]));
                validGeometry(created); int target=virtualId--; entities[target]=created;
                entityLayers[target]=entityLayers[id]; dirtyEntities.insert(target); value=target;
            } else {
                require(input["boundaries"].isArray() && !input["boundaries"].toArray().isEmpty(),"Boundary selection required");
                QList<QSharedPointer<REntity>> boundaries;
                for (const auto& v : input["boundaries"].toArray()) {
                    double n=number(v); int boundary=v.toInt();
                    require(n==boundary && boundary!=id && entities.contains(boundary),"Unknown or self boundary"); boundaries.append(entities[boundary]);
                }
                double tolerance=number(input["tolerance"]); require(tolerance>0,"Positive pick tolerance required");
                auto retained=CadGeometry::cutLine(entities[id],boundaries,point(input["picked"]),tolerance,action=="extend");
                for (const auto& e : retained) validGeometry(e);
                QJsonArray ids{id};
                entities[id]=retained.first(); dirtyEntities.insert(id);
                if (retained.size()==2) {
                    auto line=retained.last().dynamicCast<RLineEntity>();
                    QSharedPointer<REntity> copy(new RLineEntity(&document(),line->getData()));
                    int target=virtualId--; entities[target]=copy; entityLayers[target]=entityLayers[id]; dirtyEntities.insert(target); ids.append(target);
                }
                value=ids;
            }
        } else if (action=="copy" || action=="rotate" || action=="scale") {
            require(input["ids"].isArray() && !input["ids"].toArray().isEmpty(),"Selection required");
            QSet<int> ids;
            for (auto v : input["ids"].toArray()) {
                double n=number(v); int id=v.toInt(); require(n==id && entities.contains(id),"Unknown entity ID");
                ids.insert(id); writable(entityLayers[id]);
            }
            RVector base,delta; double amount=0;
            if (action=="copy") delta=point(input["delta"]);
            else { base=point(input["base"]); amount=number(input["amount"]); }
            if (action=="scale") require(amount>0,"Positive scale required");
            QMap<int,QSharedPointer<REntity>> transformed;
            for (int id : ids) {
                auto clone=entities[id]->cloneToEntity(); bool ok=false;
                if (action=="copy") ok=clone->move(delta);
                else if (action=="rotate") ok=clone->rotate(RMath::deg2rad(amount),base);
                else ok=clone->scale(RVector(amount,amount,1),base);
                require(ok,"QCAD transform failed"); validGeometry(clone); transformed[id]=clone;
            }
            QJsonArray newIds;
            for (int id : transformed.keys()) {
                if (action=="copy") {
                    QSharedPointer<REntity> clone;
                    if (auto line=transformed[id].dynamicCast<RLineEntity>())
                        clone.reset(new RLineEntity(&document(),line->getData()));
                    else if (auto c=transformed[id].dynamicCast<RCircleEntity>()) clone.reset(new RCircleEntity(&document(),c->getData()));
                    else if (auto a=transformed[id].dynamicCast<RArcEntity>()) clone.reset(new RArcEntity(&document(),a->getData()));
                    else if (auto p=transformed[id].dynamicCast<RPolylineEntity>()) clone.reset(new RPolylineEntity(&document(),p->getData()));
                    else if (CadDimensions::supported(transformed[id])) clone=CadDimensions::freshCopy(document(),transformed[id]);
                    else throw std::runtime_error("Unsupported copy geometry");
                    int target=virtualId--; entities[target]=clone; entityLayers[target]=entityLayers[id]; dirtyEntities.insert(target); newIds.append(target);
                } else { entities[id]=transformed[id]; dirtyEntities.insert(id); }
            }
            if (action=="copy") value=newIds;
        } else if (action=="properties") {
            require(input["ids"].isArray() && !input["ids"].toArray().isEmpty(),"Selection required");
            require(input["changes"].isObject() && !input["changes"].toObject().isEmpty(),"Property changes required");
            auto changes=input["changes"].toObject();
            auto keys=changes.keys();
            // Apply the explicit elevation to replacement vertices, independent
            // of JSON key order; it is the panel's common planar Z value.
            if (keys.removeOne("vertices")) keys.prepend("vertices");
            QMap<int,QSharedPointer<REntity>> replacements;
            for (auto v : input["ids"].toArray()) {
                double n=number(v); int id=v.toInt(); require(n==id && entities.contains(id),"Unknown entity ID");
                writable(entityLayers[id]);
                auto e=entities[id]->cloneToEntity();
                auto line=e.dynamicCast<RLineEntity>(); auto circle=e.dynamicCast<RCircleEntity>();
                auto arc=e.dynamicCast<RArcEntity>(); auto poly=e.dynamicCast<RPolylineEntity>();
                for (auto key : keys) {
                    if (key=="layer") writable(changes[key].toString());
                    else if (line && key=="start") line->setStartPoint(point(changes[key]));
                    else if (line && key=="end") line->setEndPoint(point(changes[key]));
                    else if (circle && key=="center") circle->getData().setCenter(point(changes[key]));
                    else if (circle && key=="radius") { double r=number(changes[key]); require(r>0,"Positive radius required"); circle->setRadius(r); }
                    else if (arc && key=="center") arc->getData().setCenter(point(changes[key]));
                    else if (arc && key=="radius") arc->setRadius(number(changes[key]));
                    else if (arc && key=="start_angle") arc->setStartAngle(angle(changes[key]));
                    else if (arc && key=="end_angle") arc->setEndAngle(angle(changes[key]));
                    else if (poly && key=="vertices") poly->getData().setVertices(vertices(changes[key]));
                    else if (poly && key=="elevation") poly->getData().setElevation(number(changes[key]));
                    else if (poly && key=="closed") { require(changes[key].isBool(),"Boolean closure required"); poly->setClosed(changes[key].toBool()); }
                    else if (CadDimensions::edit(e,key,changes[key])) {}
                    else throw std::runtime_error("Property not supported for this entity");
                }
                validGeometry(e);
                replacements[id]=e;
            }
            // Validate the complete selection before replacing any staged object.
            for (int id : replacements.keys()) {
                entities[id]=replacements[id]; dirtyEntities.insert(id);
                if (changes.contains("layer")) entityLayers[id]=changes["layer"].toString();
            }
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
                layers[name].reset(new RLayer(&document(),name,false,false,RColor(QStringLiteral("#d6e2ec")),
                    document().getLinetypeId(QStringLiteral("CONTINUOUS")),RLineweight::WeightByLwDefault));
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
