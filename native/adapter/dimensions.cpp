#include "dimensions.h"
#include "RDimAlignedEntity.h"
#include "RDimRotatedEntity.h"
#include "RDimRadialEntity.h"
#include "RMath.h"
#include "RLine.h"
#include "RTriangle.h"
#include <QJsonArray>
#include <cmath>
#include <stdexcept>
namespace {
void require(bool v,const char* m) { if (!v) throw std::runtime_error(m); }
double number(const QJsonValue& v) { require(v.isDouble() && std::isfinite(v.toDouble()),"Finite dimension number required"); return v.toDouble(); }
RVector point(const QJsonValue& v) {
    require(v.isArray() && v.toArray().size()==3,"Dimension XYZ point required"); auto a=v.toArray(); return {number(a[0]),number(a[1]),number(a[2])};
}
bool finite(const RVector& p) { return std::isfinite(p.x) && std::isfinite(p.y) && std::isfinite(p.z); }
QJsonArray xyz(const RVector& p) { return {p.x,p.y,p.z}; }
double degrees(double a) { return RMath::rad2deg(RMath::getNormalizedAngle(a)); }
}
namespace CadDimensions {
bool supported(const QSharedPointer<REntity>& e) { return e->getType()==RS::EntityDimAligned || e->getType()==RS::EntityDimRotated || e->getType()==RS::EntityDimRadial; }
QSet<RPropertyTypeId> transactionProperties(const QSharedPointer<REntity>& e) {
    auto properties=e->getPropertyTypeIds();
    // Automatic label coordinates are a render cache. CE setters for those
    // coordinates switch to manual position during property replay (undo/redo).
    // Keep authoritative geometry/text properties, and let native rendering
    // recompute derived coordinates instead of recording them as user edits.
    if (!e.dynamicCast<RDimensionEntity>()->hasCustomTextPosition()) {
        if (e->getType()==RS::EntityDimAligned) {
            properties.remove(RDimAlignedEntity::PropertyMiddleOfTextX); properties.remove(RDimAlignedEntity::PropertyMiddleOfTextY); properties.remove(RDimAlignedEntity::PropertyMiddleOfTextZ);
        } else if (e->getType()==RS::EntityDimRotated) {
            properties.remove(RDimRotatedEntity::PropertyMiddleOfTextX); properties.remove(RDimRotatedEntity::PropertyMiddleOfTextY); properties.remove(RDimRotatedEntity::PropertyMiddleOfTextZ);
        } else {
            properties.remove(RDimRadialEntity::PropertyMiddleOfTextX); properties.remove(RDimRadialEntity::PropertyMiddleOfTextY); properties.remove(RDimRadialEntity::PropertyMiddleOfTextZ);
        }
    }
    return properties;
}
void validate(const QSharedPointer<REntity>& e) {
    auto d=e.dynamicCast<RDimensionEntity>(); require(!d.isNull() && supported(e),"Unsupported dimension type");
    auto p=d->getDefinitionPoint(); require(finite(p),"Finite definition point required");
    if (auto l=e.dynamicCast<RDimLinearEntity>()) {
        auto a=l->getExtensionPoint1(),b=l->getExtensionPoint2();
        require(finite(a) && finite(b) && std::abs(a.z-b.z)<=1e-9 && std::abs(a.z-p.z)<=1e-9 && a.get2D().getDistanceTo(b.get2D())>1e-9,"Planar nondegenerate dimension required");
        if (auto r=e.dynamicCast<RDimRotatedEntity>()) require(std::isfinite(r->getData().getRotation()),"Finite dimension angle required");
    } else {
        auto r=e.dynamicCast<RDimRadialEntity>(); auto c=r->getChordPoint();
        require(finite(c) && std::abs(c.z-p.z)<=1e-9 && c.get2D().getDistanceTo(p.get2D())>1e-9,"Planar positive radius required");
    }
    double measured=d->getData().getMeasuredValue(); require(std::isfinite(measured) && measured>1e-9,"Positive finite measured value required");
    require(d->getText().size()<=256 && !d->getText().contains('\\') && !d->getText().contains('^'),"Plain dimension text up to 256 characters required");
    for (const auto c : d->getText()) require(c.unicode()>=32 && c.unicode()!=127,"Control characters in dimension text are unsupported");
}
QSharedPointer<REntity> create(RDocument& doc,const QJsonObject& input) {
    auto mode=input["mode"].toString(); RDimensionData common(&doc);
    common.setDefinitionPoint(point(input["position"])); common.setFontName(QStringLiteral("Standard"));
    common.setCustomTextPosition(false);
    QSharedPointer<REntity> e;
    if (mode=="DIMLINEAR") e.reset(new RDimRotatedEntity(&doc,RDimRotatedData(common,point(input["start"]),point(input["end"]),RMath::deg2rad(number(input["angle"])) )));
    else if (mode=="DIMALIGNED") e.reset(new RDimAlignedEntity(&doc,RDimAlignedData(common,point(input["start"]),point(input["end"]))));
    else if (mode=="DIMRADIUS") e.reset(new RDimRadialEntity(&doc,RDimRadialData(common,point(input["chord"]))));
    else throw std::runtime_error("Unsupported dimension mode");
    validate(e); return e;
}
QSharedPointer<REntity> freshCopy(RDocument& doc,const QSharedPointer<REntity>& e) {
    if (auto d=e.dynamicCast<RDimAlignedEntity>()) return QSharedPointer<REntity>(new RDimAlignedEntity(&doc,d->getData()));
    if (auto d=e.dynamicCast<RDimRotatedEntity>()) return QSharedPointer<REntity>(new RDimRotatedEntity(&doc,d->getData()));
    if (auto d=e.dynamicCast<RDimRadialEntity>()) return QSharedPointer<REntity>(new RDimRadialEntity(&doc,d->getData()));
    throw std::runtime_error("Unsupported dimension copy");
}
QList<QSharedPointer<RShape>> shapes(const QSharedPointer<REntity>& e) {
    auto d=e.dynamicCast<RDimensionEntity>(); auto parts=d->getData().getShapes();
    QList<QSharedPointer<RShape>> result;
    for (const auto& part : parts) { auto flat=part->clone(); flat->to2D(); result.append(flat); }
    return result;
}
QJsonObject snapshot(const QSharedPointer<REntity>& e) {
    auto d=e.dynamicCast<RDimensionEntity>(); const auto& data=d->getData();
    QJsonObject result{{"type","DIMENSION"},{"text",d->getText()==QStringLiteral("<>")?QString():d->getText()},{"position",xyz(d->getDefinitionPoint())}};
    if (auto l=e.dynamicCast<RDimLinearEntity>()) {
        result["start"]=xyz(l->getExtensionPoint1()); result["end"]=xyz(l->getExtensionPoint2());
        result["dimension_type"]=e->getType()==RS::EntityDimAligned ? "DIMALIGNED" : "DIMLINEAR";
        if (auto r=e.dynamicCast<RDimRotatedEntity>()) result["angle"]=degrees(r->getData().getRotation());
    } else { auto r=e.dynamicCast<RDimRadialEntity>(); result["dimension_type"]="DIMRADIUS"; result["chord"]=xyz(r->getChordPoint()); }
    QJsonArray graphics;
    for (const auto& s : shapes(e)) {
        if (auto l=s.dynamicCast<RLine>()) graphics.append(QJsonObject{{"type","LINE"},{"start",xyz(l->getStartPoint())},{"end",xyz(l->getEndPoint())}});
        else if (auto t=s.dynamicCast<RTriangle>()) graphics.append(QJsonObject{{"type","SOLID"},{"vertices",QJsonArray{xyz(t->getCorner(0)),xyz(t->getCorner(1)),xyz(t->getCorner(2))}}});
        else throw std::runtime_error("Unsupported dimension render shape");
    }
    require(!graphics.isEmpty(),"Dimension rendering unavailable");
    QString label=d->getMeasurement();
    if (e->getType()==RS::EntityDimRadial && (d->getText().isEmpty() || d->getText()==QStringLiteral("<>"))) label=QStringLiteral("R")+label;
    result["render"]=QJsonObject{{"shapes",graphics},{"label",label},
        {"text_position",xyz(d->getTextPosition())},{"text_angle",degrees(data.getTextData().getAngle())},
        {"text_height",data.getDimtxt()},{"measurement",data.getMeasuredValue()}};
    return result;
}
bool edit(const QSharedPointer<REntity>& e,const QString& key,const QJsonValue& v) {
    auto d=e.dynamicCast<RDimensionEntity>(); if (d.isNull()) return false;
    auto l=e.dynamicCast<RDimLinearEntity>(); auto r=e.dynamicCast<RDimRadialEntity>();
    if (key=="text") { require(v.isString(),"Dimension text string required"); d->setText(v.toString()); }
    else if (key=="position") d->setDefinitionPoint(point(v));
    else if (l && key=="start") l->setExtensionPoint1(point(v));
    else if (l && key=="end") l->setExtensionPoint2(point(v));
    else if (r && key=="chord") r->setChordPoint(point(v));
    else if (key=="angle" && e->getType()==RS::EntityDimRotated) e.dynamicCast<RDimRotatedEntity>()->getData().setRotation(RMath::deg2rad(number(v)));
    else return false;
    // Endpoint setters in CE do not invalidate every rendering cache themselves.
    d->getData().update(); return true;
}
}
