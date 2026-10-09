// Original analytic acceptance fixture; no CAD command compatibility claim.
#include <QCoreApplication>
#include <QJsonDocument>
#include <QJsonObject>
#include <cmath>
#include <iostream>
#include "RLine.h"
#include "RCircle.h"

int main(int argc, char** argv) {
    QCoreApplication app(argc, argv);
    const RLine line(RVector(0, 0, 7), RVector(3, 4, 7));
    const RCircle circle(RVector(10, 20, 9), 3);
    const auto near = [](double a, double b) {
        return std::isfinite(a) && std::abs(a - b) <= 1e-9;
    };
    const bool passed = near(line.getLength(), 5)
        && near(line.getStartPoint().getZ(), 7) && near(line.getEndPoint().getZ(), 7)
        && near(circle.getCenter().getZ(), 9) && near(circle.getRadius(), 3)
        && near(circle.getLength(), 6 * std::acos(-1.0));
    const QJsonObject result{{"line_length", line.getLength()},
        {"line_start_z", line.getStartPoint().getZ()}, {"line_end_z", line.getEndPoint().getZ()},
        {"circle_z", circle.getCenter().getZ()}, {"circle_radius", circle.getRadius()},
        {"circle_length", circle.getLength()}};
    const QJsonObject report{{"origin", "qcad"},
        {"version", "4c830eb4d80285ca64b1f2c2dc0987f729344126"},
        {"result", result}, {"passed", passed}, {"document_adapter", false}};
    std::cout << QJsonDocument(report).toJson().constData();
    return passed ? 0 : 1;
}
