cmake_minimum_required(VERSION 3.28)
project(OpenCAD2D VERSION 0.1.0 LANGUAGES NONE)
include(CTest)
find_package(Python3 COMPONENTS Interpreter REQUIRED)
add_test(NAME prototype-regression COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/cad_workflow.py"
    regress --report "${CMAKE_CURRENT_BINARY_DIR}/regression.json")
set_tests_properties(prototype-regression PROPERTIES WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    ENVIRONMENT "PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}/src;QT_QPA_PLATFORM=offscreen")

option(OPENCAD_BUILD_QCAD "Build the audited upstream QCAD CE (adapter remains pending)" OFF)
set(OPENCAD_QCAD_SOURCE "" CACHE PATH "Existing audited QCAD checkout")
if(OPENCAD_BUILD_QCAD)
    enable_language(CXX)
    find_package(Qt6 REQUIRED COMPONENTS Core Gui)
    find_package(Git REQUIRED)
    execute_process(COMMAND "${GIT_EXECUTABLE}" -C "${OPENCAD_QCAD_SOURCE}" rev-parse HEAD
        OUTPUT_VARIABLE QCAD_SHA OUTPUT_STRIP_TRAILING_WHITESPACE RESULT_VARIABLE QCAD_GIT_STATUS)
    if(NOT QCAD_GIT_STATUS EQUAL 0 OR NOT QCAD_SHA STREQUAL "4c830eb4d80285ca64b1f2c2dc0987f729344126")
        message(FATAL_ERROR "Provide the audited QCAD commit; re-audit before changing the pin")
    endif()
    include(ExternalProject)
    ExternalProject_Add(qcad-ce SOURCE_DIR "${OPENCAD_QCAD_SOURCE}"
        PATCH_COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/apply_qcad_patch.py" "${OPENCAD_QCAD_SOURCE}"
        CMAKE_ARGS -DBUILD_QT6=ON -DCMAKE_BUILD_TYPE=Release
                   "-DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}"
        INSTALL_COMMAND "")
    if(WIN32)
    add_library(qcad-audited-core SHARED IMPORTED)
    set_target_properties(qcad-audited-core PROPERTIES
        IMPORTED_IMPLIB "${OPENCAD_QCAD_SOURCE}/release/qcadcore.lib"
        IMPORTED_LOCATION "${OPENCAD_QCAD_SOURCE}/release/qcadcore.dll")
    add_executable(qcad-geometry-smoke native/smoke/geometry.cpp)
    target_compile_definitions(qcad-geometry-smoke PRIVATE QCAD_DLL)
    target_compile_features(qcad-geometry-smoke PRIVATE cxx_std_17)
    target_include_directories(qcad-geometry-smoke PRIVATE
        "${OPENCAD_QCAD_SOURCE}/src/core" "${OPENCAD_QCAD_SOURCE}/src/core/math")
    target_link_libraries(qcad-geometry-smoke PRIVATE qcad-audited-core Qt6::Core Qt6::Gui)
    add_dependencies(qcad-geometry-smoke qcad-ce)
    add_test(NAME qcad-geometry COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_CURRENT_SOURCE_DIR}/tools/check_qcad_geometry.py"
        --binary "$<TARGET_FILE:qcad-geometry-smoke>" --source "${OPENCAD_QCAD_SOURCE}"
        --qt "${CMAKE_PREFIX_PATH}" --report "${CMAKE_CURRENT_BINARY_DIR}/geometry-report.json")
    endif()
endif()
