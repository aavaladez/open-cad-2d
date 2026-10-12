// Original GPL-3.0-or-later operations over public QCAD shapes/entities.
#pragma once
#include "REntity.h"
#include "RShape.h"
#include <QList>

namespace CadGeometry {
QSharedPointer<RShape> projected(const QSharedPointer<REntity>& entity);
QList<QSharedPointer<REntity>> cutLine(const QSharedPointer<REntity>& entity,
    const QList<QSharedPointer<REntity>>& boundaries, const RVector& picked,
    double pickTolerance, bool extend);
QSharedPointer<REntity> offset(const QSharedPointer<REntity>& entity,
    double distance, const RVector& side);
}
