// Original dependency acceptance fixture: this is not the OPEN CAD application.
#include <QApplication>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QFileInfo>
#include <iostream>
#include "RDocument.h"
#include "RDocumentInterface.h"
#include "RMemoryStorage.h"
#include "RSpatialIndexSimple.h"
#include "RSettings.h"
#include "RMath.h"
#include "RDocumentVariables.h"
#include "RDimStyle.h"
#include "RDimStyleData.h"
#include "RLayer.h"
#include "RLayerState.h"
#include "RLayout.h"
#include "RLinetype.h"
#include "RBlock.h"
#include "RUcs.h"
#include "RView.h"
#include "RLineEntity.h"
#include "RCircleEntity.h"
#include "RAddObjectOperation.h"
#include "RModifyObjectsOperation.h"
#include "RDxfImporterFactory.h"
#include "RDxfExporterFactory.h"

static QJsonArray vector(const RVector& v) { return {v.x, v.y, v.z}; }
static QJsonArray inventory(RDocument& doc) {
    QJsonArray items;
    for (auto id : doc.queryAllEntities()) {
        auto e = doc.queryEntity(id);
        QJsonObject item{{"layer",doc.queryLayer(e->getLayerId())->getName()}};
        auto line = e.dynamicCast<RLineEntity>();
        auto circle = e.dynamicCast<RCircleEntity>();
        if (line) {
            item.insert("type", "LINE"); item.insert("start", vector(line->getStartPoint()));
            item.insert("end", vector(line->getEndPoint()));
        } else if (circle) {
            item.insert("type", "CIRCLE"); item.insert("center", vector(circle->getCenter()));
            item.insert("radius", circle->getRadius());
        } else { item.insert("type", "unsupported"); }
        items.append(item);
    }
    return items;
}

int main(int argc, char** argv) {
    QApplication app(argc, argv);
    RSettings::setNoWrite(true);
    if (argc != 3) { std::cerr << "input.dxf output.dxf required\n"; return 2; }
    if (!QFileInfo::exists(QString::fromLocal8Bit(argv[1])) ||
        QFileInfo::exists(QString::fromLocal8Bit(argv[2]))) {
        std::cerr << "Existing input and new output required; never overwrite a fixture\n";
        return 2;
    }
    RMath::init(); RDimStyleData::initDefaults(); RObject::init(); REntity::init();
    RDocumentVariables::init(); RDimStyle::init(); RLayer::init(); RLayerState::init();
    RLayout::init(); RLinetype::init(); RBlock::init(); RUcs::init(); RView::init();
    RLineEntity::init(); RCircleEntity::init();
    RDxfImporterFactory::registerFileImporter(); RDxfExporterFactory::registerFileExporter();
    // RDocumentInterface deletes its document; RDocument deletes storage/index.
    RDocument& doc = *new RDocument(*new RMemoryStorage(), *new RSpatialIndexSimple());
    RDocumentInterface di(doc);
    QJsonObject checks;
    checks.insert("import", di.importFile(QString::fromLocal8Bit(argv[1])) == RDocumentInterface::IoErrorNoError);
    std::cerr << "imported\n";
    const QJsonArray before = inventory(doc);
    checks.insert("input_count", before.size() == 2);
    auto line = QSharedPointer<RLineEntity>(new RLineEntity(&doc,
        RLineData(RVector(20,0,5), RVector(23,4,5))));
    line->setLayerId(doc.getLayerId("Survey"));
    checks.insert("add_transaction", !di.applyOperation(new RAddObjectOperation(line,QStringLiteral("Fixture add"),false,true)).isFailed());
    const auto id = line->getId();
    checks.insert("add_count", doc.queryAllEntities().size() == 3);
    di.undo(); checks.insert("undo_add", doc.queryAllEntities().size() == 2);
    di.redo(); checks.insert("redo_add", doc.queryAllEntities().size() == 3);
    auto moved = doc.queryEntity(id).dynamicCast<RLineEntity>()->cloneToLineEntity();
    moved->setStartPoint(RVector(10,2,5)); moved->setEndPoint(RVector(13,6,5));
    auto modify = new RModifyObjectsOperation(); modify->addObject(moved,false);
    checks.insert("modify_transaction", !di.applyOperation(modify).isFailed());
    di.undo();
    checks.insert("undo_modify", doc.queryEntity(id).dynamicCast<RLineEntity>()->getStartPoint().equalsFuzzy(RVector(20,0,5)));
    di.redo();
    checks.insert("redo_modify", doc.queryEntity(id).dynamicCast<RLineEntity>()->getStartPoint().equalsFuzzy(RVector(10,2,5)));
    std::cerr << "transactions checked\n";
    checks.insert("export", di.exportFile(QString::fromLocal8Bit(argv[2])));
    std::cerr << "exported\n";
    RDocument& reopened = *new RDocument(*new RMemoryStorage(), *new RSpatialIndexSimple());
    std::cerr << "second document created\n";
    RDocumentInterface reopenedDi(reopened);
    checks.insert("reopen", reopenedDi.importFile(QString::fromLocal8Bit(argv[2])) == RDocumentInterface::IoErrorNoError);
    std::cerr << "reopened\n";
    checks.insert("reopened_count", reopened.queryAllEntities().size() == 3);
    bool passed = true;
    for (auto i = checks.begin(); i != checks.end(); ++i) passed = passed && i.value().toBool();
    const QJsonObject report{{"kind","dependency_functional"},{"engine","qcad"},
        {"checks",checks},{"before",before},{"after",inventory(doc)},
        {"reopened",inventory(reopened)},{"passed",passed},{"application_integrated",false}};
    std::cout << QJsonDocument(report).toJson().constData() << std::flush;
    return passed ? 0 : 1;
}
