#include "geometry_ops.h"
#include "RLineEntity.h"
#include "RCircleEntity.h"
#include "RArcEntity.h"
#include "RPolylineEntity.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace {
constexpr double tolerance=1e-9;
void require(bool ok,const char* message) { if (!ok) throw std::runtime_error(message); }
}
namespace CadGeometry {
QSharedPointer<RShape> projected(const QSharedPointer<REntity>& e) {
    if (auto l=e.dynamicCast<RLineEntity>()) return QSharedPointer<RShape>(new RLine(l->getStartPoint().get2D(),l->getEndPoint().get2D()));
    if (auto c=e.dynamicCast<RCircleEntity>()) return QSharedPointer<RShape>(new RCircle(c->getCenter().get2D(),c->getRadius()));
    if (auto a=e.dynamicCast<RArcEntity>()) return QSharedPointer<RShape>(new RArc(a->getCenter().get2D(),a->getRadius(),a->getStartAngle(),a->getEndAngle(),a->isReversed()));
    if (auto p=e.dynamicCast<RPolylineEntity>()) {
        auto flat=p->getPolylineShape(); flat.setZ(0); return QSharedPointer<RShape>(new RPolyline(flat));
    }
    throw std::runtime_error("Unsupported projected geometry");
}

QList<QSharedPointer<REntity>> cutLine(const QSharedPointer<REntity>& entity,
    const QList<QSharedPointer<REntity>>& boundaries,const RVector& picked,double pickTolerance,bool extend) {
    auto line=entity.dynamicCast<RLineEntity>();
    require(!line.isNull(),"TRIM/EXTEND currently require a LINE target");
    RVector a=line->getStartPoint(),b=line->getEndPoint(),delta=b-a;
    const double length=std::hypot(delta.x,delta.y),denom=delta.x*delta.x+delta.y*delta.y;
    require(std::isfinite(denom) && length>tolerance,"Usable XY line required");
    auto shape=projected(entity);
    require(shape->getDistanceTo(picked.get2D())<=pickTolerance,"Pick point must lie on the target line within tolerance");
    const double epsilon=tolerance/length;
    auto parameter=[&](const RVector& p){ return ((p.x-a.x)*delta.x+(p.y-a.y)*delta.y)/denom; };
    double click=std::clamp(parameter(picked),0.0,1.0);
    QList<double> cuts;
    for (const auto& boundary : boundaries) {
        auto edge=projected(boundary);
        for (const auto& p : shape->getIntersectionPoints(*edge,false)) {
            // Boundary edges remain finite; projection is XY, never an invented
            // extension of a cutting edge. Curve support circles are not edges.
            if (!p.isValid() || !edge->isOnShape(p,true,tolerance)) continue;
            double t=parameter(p);
            if (std::isfinite(t) && (extend ? t<-epsilon || t>1+epsilon : t>epsilon && t<1-epsilon)) cuts.append(t);
        }
    }
    std::sort(cuts.begin(),cuts.end());
    cuts.erase(std::unique(cuts.begin(),cuts.end(),[&](double x,double y){ return std::abs(x-y)<=epsilon; }),cuts.end());
    require(!cuts.isEmpty(),"No usable intersection with finite boundary edges");
    QList<QPair<double,double>> intervals;
    if (extend) {
        require(std::abs(click-.5)>epsilon,"Ambiguous midpoint: pick the endpoint half to extend");
        double nearest=click<.5 ? -INFINITY : INFINITY;
        for (double t : cuts) if (click<.5 && t<0) nearest=std::max(nearest,t);
            else if (click>.5 && t>1) nearest=std::min(nearest,t);
        require(std::isfinite(nearest),"No boundary intersection beyond selected endpoint");
        intervals.append(click<.5 ? qMakePair(nearest,1.0) : qMakePair(0.0,nearest));
    } else {
        double low=0,high=1;
        for (double t : cuts) {
            require(std::abs(t-click)>epsilon,"Ambiguous pick on cutting edge");
            if (t<click) low=t; else { high=t; break; }
        }
        if (low>0) intervals.append(qMakePair(0.0,low));
        if (high<1) intervals.append(qMakePair(high,1.0));
    }
    QList<QSharedPointer<REntity>> result;
    for (const auto& span : intervals) {
        // Interpolate/extrapolate Z along the original XYZ line after native XY
        // intersection. Preserve its data/layer; no Python geometry is involved.
        auto copy=line->cloneToLineEntity(); copy->setStartPoint(a+delta*span.first); copy->setEndPoint(a+delta*span.second);
        result.append(copy);
    }
    require(!result.isEmpty(),"TRIM produced no retained interval");
    return result;
}

QSharedPointer<REntity> offset(const QSharedPointer<REntity>& e,double distance,const RVector& side) {
    require(distance>0 && std::isfinite(distance),"Positive finite offset distance required");
    auto shape=projected(e);
    // A point on the supporting curve has no unambiguous side. For LINE use
    // its infinite support, so a point beyond an endpoint still defines a side.
    double separation;
    if (auto l=shape.dynamicCast<RLine>()) {
        require(l->getLength()>tolerance && std::isfinite(l->getLength()),"Usable XY line required");
        separation=l->getDistanceTo(side.get2D(),false);
    }
    else if (auto a=shape.dynamicCast<RArc>()) separation=std::abs(a->getCenter().getDistanceTo(side.get2D())-a->getRadius());
    else if (auto c=shape.dynamicCast<RCircle>()) separation=std::abs(c->getCenter().getDistanceTo(side.get2D())-c->getRadius());
    else throw std::runtime_error("OFFSET currently supports LINE/CIRCLE/ARC only");
    require(std::isfinite(separation) && separation>tolerance,"Ambiguous offset side on support curve");
    auto shapes=shape->getOffsetShapes(distance,1,RS::NoSide,side.get2D());
    require(shapes.size()==1,"QCAD offset impossible (radius collapse or unsupported geometry)");
    // Create a fresh public entity from original data to reset identity, then
    // set native offset geometry and restore retained Z data.
    if (auto l=e.dynamicCast<RLineEntity>()) {
        auto shifted=shapes[0].dynamicCast<RLine>(); require(!shifted.isNull(),"QCAD offset type mismatch");
        auto a=shifted->getStartPoint(),b=shifted->getEndPoint(); a.z=l->getStartPoint().z; b.z=l->getEndPoint().z;
        QSharedPointer<RLineEntity> result(new RLineEntity(l->getDocument(),l->getData())); result->setStartPoint(a); result->setEndPoint(b); return result;
    }
    if (auto a=e.dynamicCast<RArcEntity>()) {
        auto shifted=shapes[0].dynamicCast<RArc>(); require(!shifted.isNull(),"QCAD offset type mismatch");
        QSharedPointer<RArcEntity> result(new RArcEntity(a->getDocument(),a->getData())); result->setRadius(shifted->getRadius()); return result;
    }
    auto c=e.dynamicCast<RCircleEntity>(); auto shifted=shapes[0].dynamicCast<RCircle>(); require(c && shifted,"QCAD offset type mismatch");
    QSharedPointer<RCircleEntity> result(new RCircleEntity(c->getDocument(),c->getData())); result->setRadius(shifted->getRadius()); return result;
}
}
