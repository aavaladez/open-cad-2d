// Original GPL-3.0-or-later adapter for public QCAD dimension entities.
#pragma once
#include <QJsonObject>
#include "REntity.h"
#include "RShape.h"
namespace CadDimensions {
bool supported(const QSharedPointer<REntity>& e);
void validate(const QSharedPointer<REntity>& e);
QSharedPointer<REntity> create(RDocument& doc,const QJsonObject& input);
QSharedPointer<REntity> freshCopy(RDocument& doc,const QSharedPointer<REntity>& e);
QJsonObject snapshot(const QSharedPointer<REntity>& e);
bool edit(const QSharedPointer<REntity>& e,const QString& key,const QJsonValue& value);
QList<QSharedPointer<RShape>> shapes(const QSharedPointer<REntity>& e);
QSet<RPropertyTypeId> transactionProperties(const QSharedPointer<REntity>& e);
}
