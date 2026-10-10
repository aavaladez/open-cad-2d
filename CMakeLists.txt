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
    find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets)
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
        BUILD_BYPRODUCTS "${OPENCAD_QCAD_SOURCE}/release/qcadcore.lib"
                         "${OPENCAD_QCAD_SOURCE}/release/qcadcore.dll"
                         "${OPENCAD_QCAD_SOURCE}/release/qcadentity.lib"
                         "${OPENCAD_QCAD_SOURCE}/release/qcadoperations.lib"
                         "${OPENCAD_QCAD_SOURCE}/plugins/qcaddxf.lib"
        BUILD_COMMAND "${CMAKE_COMMAND}" --build <BINARY_DIR> --parallel 4
        BUILD_ALWAYS TRUE
        INSTALL_COMMAND "")
    ExternalProject_Add_StepDependencies(qcad-ce patch
        "${CMAKE_CURRENT_SOURCE_DIR}/tools/apply_qcad_patch.py"
        "${CMAKE_CURRENT_SOURCE_DIR}/native/patches/qcad-msvc-link-paths.patch"
        "${CMAKE_CURRENT_SOURCE_DIR}/native/patches/qcad-dxf-z.patch")
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
    foreach(component entity operations)
        add_library(qcad-audited-${component} SHARED IMPORTED)
        set_target_properties(qcad-audited-${component} PROPERTIES
            IMPORTED_IMPLIB "${OPENCAD_QCAD_SOURCE}/release/qcad${component}.lib"
            IMPORTED_LOCATION "${OPENCAD_QCAD_SOURCE}/release/qcad${component}.dll")
    endforeach()
    add_library(qcad-audited-dxf SHARED IMPORTED)
    set_target_properties(qcad-audited-dxf PROPERTIES
        IMPORTED_IMPLIB "${OPENCAD_QCAD_SOURCE}/plugins/qcaddxf.lib"
        IMPORTED_LOCATION "${OPENCAD_QCAD_SOURCE}/plugins/qcaddxf.dll")
    add_executable(qcad-document-smoke native/smoke/document.cpp)
    target_compile_definitions(qcad-document-smoke PRIVATE QCAD_DLL)
    target_compile_features(qcad-document-smoke PRIVATE cxx_std_17)
    target_include_directories(qcad-document-smoke PRIVATE
        "${OPENCAD_QCAD_SOURCE}/src/core" "${OPENCAD_QCAD_SOURCE}/src/core/math"
        "${OPENCAD_QCAD_SOURCE}/src/entity" "${OPENCAD_QCAD_SOURCE}/src/operations"
        "${OPENCAD_QCAD_SOURCE}/src/io/dxf" "${OPENCAD_QCAD_SOURCE}/src/3rdparty")
    target_link_libraries(qcad-document-smoke PRIVATE qcad-audited-core
        qcad-audited-entity qcad-audited-operations qcad-audited-dxf Qt6::Widgets)
    add_dependencies(qcad-document-smoke qcad-ce)
    add_test(NAME qcad-document COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_CURRENT_SOURCE_DIR}/tools/check_qcad_document.py"
        --binary "$<TARGET_FILE:qcad-document-smoke>" --source "${OPENCAD_QCAD_SOURCE}"
        --qt "${CMAKE_PREFIX_PATH}" --output "${CMAKE_CURRENT_BINARY_DIR}/document-acceptance")
    add_test(NAME qcad-geometry COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_CURRENT_SOURCE_DIR}/tools/check_qcad_geometry.py"
        --binary "$<TARGET_FILE:qcad-geometry-smoke>" --source "${OPENCAD_QCAD_SOURCE}"
        --qt "${CMAKE_PREFIX_PATH}" --report "${CMAKE_CURRENT_BINARY_DIR}/geometry-report.json")
    endif()
endif()
