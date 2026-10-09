# Matriz de comandos

Generada desde el Excel original; cada fila conserva ID, hoja y fila.

SHA-256: `7fa08654ca249eac3f04b6a900af491e19baaa105ed5bb93503943f8230bf8b0`. Total: 472 entradas.

Estados: {'prototype_partial': 12, 'pending': 399, 'excluded': 61}. Ningún comando del Excel terminado; variantes del prototipo comprobadas por pruebas locales.

Fuente encontrada = registro textual exacto del comando, sin ejecución ni equivalencia de opciones. Ausencia de coincidencia no prueba ausencia funcional. QCAD usa nombres/alias diferentes (p. ej. circlecr). Comparación completa pendiente de adaptar contratos por fila.

Detalle íntegro de descripciones, aliases, rutas, alcance, implementación, test y enlaces de fuente: [coverage.csv](../requirements/coverage.csv) y [coverage.json](../requirements/coverage.json). Datos originales: [catalog.json](../requirements/catalog.json).

| ID | Hoja: fila | Categoría | Comando | Alcance | QCAD fuente | LC3 fuente | Estado | Test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ACAD-0002 | AutoCAD: 2 | Dibujo | LINE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Line/Line2P/Line2PInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/createActions/lineoperations.lua) | prototype_partial | test_commands.Commands.test_line_alias_chain_z_undo |
| ACAD-0003 | AutoCAD: 3 | Dibujo | PLINE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0004 | AutoCAD: 4 | Dibujo | 3DPOLY | 2d_with_z | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0005 | AutoCAD: 5 | Dibujo | XLINE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0006 | AutoCAD: 6 | Dibujo | RAY | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0007 | AutoCAD: 7 | Dibujo | CIRCLE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Circle/CircleCP/CircleCPInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/createActions/circleoperations.lua) | prototype_partial | test_commands.Commands.test_circle_invalid_and_valid |
| ACAD-0008 | AutoCAD: 8 | Dibujo | ARC | 2d | sin coincidencia | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/createActions/arcoperations.lua) | pending | pendiente |
| ACAD-0009 | AutoCAD: 9 | Dibujo | ELLIPSE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Ellipse/EllipseCPP/EllipseCPPInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/createActions/ellipseoperations.lua) | pending | pendiente |
| ACAD-0010 | AutoCAD: 10 | Dibujo | RECTANG | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0011 | AutoCAD: 11 | Dibujo | POLYGON | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Shape/ShapePolygonCP/ShapePolygonCPInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0012 | AutoCAD: 12 | Dibujo | SPLINE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Spline/SplineControlPoints/SplineControlPointsInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/createActions/splineoperations.lua) | pending | pendiente |
| ACAD-0013 | AutoCAD: 13 | Dibujo | DONUT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0014 | AutoCAD: 14 | Dibujo | POINT | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Point/Point1P/Point1PInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/createActions/pointoperations.lua) | pending | pendiente |
| ACAD-0015 | AutoCAD: 15 | Dibujo | PTYPE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0016 | AutoCAD: 16 | Dibujo | MLINE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0017 | AutoCAD: 17 | Dibujo | SKETCH | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0018 | AutoCAD: 18 | Dibujo | REVCLOUD | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0019 | AutoCAD: 19 | Dibujo | WIPEOUT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0020 | AutoCAD: 20 | Dibujo | REGION | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0021 | AutoCAD: 21 | Dibujo | BOUNDARY | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0022 | AutoCAD: 22 | Dibujo | HATCH | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Hatch/HatchFromSelection/HatchFromSelectionInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0023 | AutoCAD: 23 | Dibujo | GRADIENT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0024 | AutoCAD: 24 | Dibujo | HATCHEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0025 | AutoCAD: 25 | Dibujo | SOLID | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0026 | AutoCAD: 26 | Dibujo | TRACE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0027 | AutoCAD: 27 | Dibujo | DIVIDE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Divide/DivideInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0028 | AutoCAD: 28 | Dibujo | MEASURE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0029 | AutoCAD: 29 | Dibujo | TEXT | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Text/TextInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/createActions/textoperations.lua) | pending | pendiente |
| ACAD-0030 | AutoCAD: 30 | Dibujo | MTEXT | 2d | sin coincidencia | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/createActions/mtextoperations.lua) | pending | pendiente |
| ACAD-0031 | AutoCAD: 31 | Dibujo | TABLE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0032 | AutoCAD: 32 | Dibujo | FIELD | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0033 | AutoCAD: 33 | Dibujo | LEADER | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Dimension/Leader/LeaderInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0034 | AutoCAD: 34 | Dibujo | QLEADER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0035 | AutoCAD: 35 | Dibujo | MLEADER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0036 | AutoCAD: 36 | Dibujo | HELIX | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0037 | AutoCAD: 37 | Modificación | MOVE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Translate/TranslateInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/actions/moveoperation.lua) | prototype_partial | test_commands.Commands.test_move_erase_layer_lock |
| ACAD-0038 | AutoCAD: 38 | Modificación | COPY | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Edit/Copy/CopyInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/actions/copyoperation.lua) | pending | pendiente |
| ACAD-0039 | AutoCAD: 39 | Modificación | ROTATE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Rotate/RotateInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/actions/rotateoperation.lua) | pending | pendiente |
| ACAD-0040 | AutoCAD: 40 | Modificación | SCALE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Scale/ScaleInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/actions/scaleoperation.lua) | pending | pendiente |
| ACAD-0041 | AutoCAD: 41 | Modificación | MIRROR | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Mirror/MirrorInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0042 | AutoCAD: 42 | Modificación | OFFSET | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Offset/OffsetInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0043 | AutoCAD: 43 | Modificación | TRIM | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Trim/TrimInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/actions/trimoperation.lua) | pending | pendiente |
| ACAD-0044 | AutoCAD: 44 | Modificación | EXTEND | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Trim/TrimInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0045 | AutoCAD: 45 | Modificación | FILLET | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0046 | AutoCAD: 46 | Modificación | CHAMFER | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Bevel/BevelInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0047 | AutoCAD: 47 | Modificación | STRETCH | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Stretch/StretchInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0048 | AutoCAD: 48 | Modificación | LENGTHEN | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Lengthen/LengthenInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0049 | AutoCAD: 49 | Modificación | BREAK | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/BreakOut/BreakOutInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0050 | AutoCAD: 50 | Modificación | BREAKATPOINT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0051 | AutoCAD: 51 | Modificación | JOIN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0052 | AutoCAD: 52 | Modificación | EXPLODE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Explode/ExplodeInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0053 | AutoCAD: 53 | Modificación | ERASE | 2d | sin coincidencia | sin coincidencia | prototype_partial | test_commands.Commands.test_move_erase_layer_lock |
| ACAD-0054 | AutoCAD: 54 | Modificación | ARRAY | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0055 | AutoCAD: 55 | Modificación | ARRAYRECT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0056 | AutoCAD: 56 | Modificación | ARRAYPOLAR | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0057 | AutoCAD: 57 | Modificación | ARRAYPATH | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0058 | AutoCAD: 58 | Modificación | ARRAYEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0059 | AutoCAD: 59 | Modificación | ALIGN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0060 | AutoCAD: 60 | Modificación | PEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0061 | AutoCAD: 61 | Modificación | SPLINEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0062 | AutoCAD: 62 | Modificación | MLEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0063 | AutoCAD: 63 | Modificación | MATCHPROP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0064 | AutoCAD: 64 | Modificación | CHANGE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0065 | AutoCAD: 65 | Modificación | CHPROP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0066 | AutoCAD: 66 | Modificación | OVERKILL | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0067 | AutoCAD: 67 | Modificación | BLEND | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0068 | AutoCAD: 68 | Modificación | REVERSE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Modify/Reverse/ReverseInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0069 | AutoCAD: 69 | Modificación | SCALETEXT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0070 | AutoCAD: 70 | Modificación | JUSTIFYTEXT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0071 | AutoCAD: 71 | Modificación | TEXTEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0072 | AutoCAD: 72 | Modificación | SPELL | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0073 | AutoCAD: 73 | Modificación | FIND | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0074 | AutoCAD: 74 | Modificación | TXTEXP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0075 | AutoCAD: 75 | Modificación | TCOUNT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0076 | AutoCAD: 76 | Modificación | UNDO | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Edit/Undo/UndoInit.js) | sin coincidencia | prototype_partial | test_commands.Commands.test_line_alias_chain_z_undo |
| ACAD-0077 | AutoCAD: 77 | Modificación | REDO | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Edit/Redo/RedoInit.js) | sin coincidencia | prototype_partial | test_commands.Commands.test_line_alias_chain_z_undo |
| ACAD-0078 | AutoCAD: 78 | Modificación | OOPS | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Edit/Undo/UndoInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0079 | AutoCAD: 79 | Modificación | GROUP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0080 | AutoCAD: 80 | Modificación | UNGROUP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0081 | AutoCAD: 81 | Modificación | DRAWORDER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0082 | AutoCAD: 82 | Modificación | TEXTTOFRONT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0083 | AutoCAD: 83 | Modificación | HATCHTOBACK | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0084 | AutoCAD: 84 | Modificación | FLATTEN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0085 | AutoCAD: 85 | Modificación | CONVERTPLINE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0086 | AutoCAD: 86 | Selección, consulta y propiedades | SELECT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0087 | AutoCAD: 87 | Selección, consulta y propiedades | SELECTALL | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Select/SelectAll/SelectAllInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0088 | AutoCAD: 88 | Selección, consulta y propiedades | SELECTSIMILAR | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0089 | AutoCAD: 89 | Selección, consulta y propiedades | QSELECT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0090 | AutoCAD: 90 | Selección, consulta y propiedades | FILTER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0091 | AutoCAD: 91 | Selección, consulta y propiedades | PROPERTIES | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0092 | AutoCAD: 92 | Selección, consulta y propiedades | QUICKPROP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0093 | AutoCAD: 93 | Selección, consulta y propiedades | LIST | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0094 | AutoCAD: 94 | Selección, consulta y propiedades | ID | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0095 | AutoCAD: 95 | Selección, consulta y propiedades | DIST | 2d | sin coincidencia | sin coincidencia | prototype_partial | test_commands.Commands.test_dist_analytic |
| ACAD-0096 | AutoCAD: 96 | Selección, consulta y propiedades | AREA | 2d | sin coincidencia | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/actions/areaoperation.lua) | pending | pendiente |
| ACAD-0097 | AutoCAD: 97 | Selección, consulta y propiedades | MEASUREGEOM | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0098 | AutoCAD: 98 | Selección, consulta y propiedades | MASSPROP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0099 | AutoCAD: 99 | Selección, consulta y propiedades | CAL | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0100 | AutoCAD: 100 | Selección, consulta y propiedades | QUICKCALC | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0101 | AutoCAD: 101 | Selección, consulta y propiedades | DBLIST | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0102 | AutoCAD: 102 | Selección, consulta y propiedades | STATUS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0103 | AutoCAD: 103 | Selección, consulta y propiedades | TIME | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0104 | AutoCAD: 104 | Selección, consulta y propiedades | DWGPROPS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0105 | AutoCAD: 105 | Selección, consulta y propiedades | SETVAR | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0106 | AutoCAD: 106 | Selección, consulta y propiedades | UPDATEFIELD | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0107 | AutoCAD: 107 | Capas | LAYER | 2d | sin coincidencia | sin coincidencia | prototype_partial | test_commands.Commands.test_layer_visibility_undo |
| ACAD-0108 | AutoCAD: 108 | Capas | LAYERP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0109 | AutoCAD: 109 | Capas | LAYERPMODE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0110 | AutoCAD: 110 | Capas | LAYISO | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0111 | AutoCAD: 111 | Capas | LAYUNISO | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0112 | AutoCAD: 112 | Capas | LAYOFF | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0113 | AutoCAD: 113 | Capas | LAYON | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0114 | AutoCAD: 114 | Capas | LAYFRZ | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0115 | AutoCAD: 115 | Capas | LAYTHW | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0116 | AutoCAD: 116 | Capas | LAYLCK | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0117 | AutoCAD: 117 | Capas | LAYULK | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0118 | AutoCAD: 118 | Capas | LAYDEL | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0119 | AutoCAD: 119 | Capas | LAYMRG | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0120 | AutoCAD: 120 | Capas | LAYWALK | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0121 | AutoCAD: 121 | Capas | LAYMCUR | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0122 | AutoCAD: 122 | Capas | LAYCUR | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0123 | AutoCAD: 123 | Capas | LAYMATCH | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0124 | AutoCAD: 124 | Capas | LAYTRANS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0125 | AutoCAD: 125 | Capas | LAYERSTATE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0126 | AutoCAD: 126 | Capas | LAYVPI | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0127 | AutoCAD: 127 | Capas | COLOR | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0128 | AutoCAD: 128 | Capas | LINETYPE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0129 | AutoCAD: 129 | Capas | LTSCALE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0130 | AutoCAD: 130 | Capas | CELTSCALE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0131 | AutoCAD: 131 | Capas | LWEIGHT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0132 | AutoCAD: 132 | Capas | TRANSPARENCY | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0133 | AutoCAD: 133 | Visualización y navegación | ZOOM | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0134 | AutoCAD: 134 | Visualización y navegación | PAN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0135 | AutoCAD: 135 | Visualización y navegación | REGEN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0136 | AutoCAD: 136 | Visualización y navegación | REGENALL | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0137 | AutoCAD: 137 | Visualización y navegación | REDRAW | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0138 | AutoCAD: 138 | Visualización y navegación | REDRAWALL | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0139 | AutoCAD: 139 | Visualización y navegación | REGENAUTO | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0140 | AutoCAD: 140 | Visualización y navegación | VIEW | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0141 | AutoCAD: 141 | Visualización y navegación | VIEWRES | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0142 | AutoCAD: 142 | Visualización y navegación | VPORTS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0143 | AutoCAD: 143 | Visualización y navegación | NAVBAR | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0144 | AutoCAD: 144 | Visualización y navegación | NAVSWHEEL | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0145 | AutoCAD: 145 | Visualización y navegación | VSCURRENT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0146 | AutoCAD: 146 | Visualización y navegación | VISUALSTYLES | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0147 | AutoCAD: 147 | Visualización y navegación | SHADEMODE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0148 | AutoCAD: 148 | Visualización y navegación | HIDE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0149 | AutoCAD: 149 | Visualización y navegación | 3DORBIT | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0150 | AutoCAD: 150 | Visualización y navegación | 3DFORBIT | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0151 | AutoCAD: 151 | Visualización y navegación | 3DCORBIT | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0152 | AutoCAD: 152 | Visualización y navegación | DVIEW | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0153 | AutoCAD: 153 | Visualización y navegación | VPOINT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0154 | AutoCAD: 154 | Visualización y navegación | PLAN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0155 | AutoCAD: 155 | Visualización y navegación | CAMERA | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0156 | AutoCAD: 156 | Visualización y navegación | WALK / FLY | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0157 | AutoCAD: 157 | Visualización y navegación | SHOWMOTION | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0158 | AutoCAD: 158 | Visualización y navegación | STEERINGWHEELS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0159 | AutoCAD: 159 | Visualización y navegación | CLEANSCREENON | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0160 | AutoCAD: 160 | Visualización y navegación | CLEANSCREENOFF | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0161 | AutoCAD: 161 | UCS / Coordenadas | UCS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0162 | AutoCAD: 162 | UCS / Coordenadas | UCSMAN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0163 | AutoCAD: 163 | UCS / Coordenadas | UCSICON | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0164 | AutoCAD: 164 | UCS / Coordenadas | PLAN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0165 | AutoCAD: 165 | UCS / Coordenadas | ID | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0166 | AutoCAD: 166 | UCS / Coordenadas | UNITS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0167 | AutoCAD: 167 | UCS / Coordenadas | DWGUNITS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0168 | AutoCAD: 168 | UCS / Coordenadas | GEOGRAPHICLOCATION | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0169 | AutoCAD: 169 | UCS / Coordenadas | GEOMAP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0170 | AutoCAD: 170 | UCS / Coordenadas | GEOMARKPOSITION | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0171 | AutoCAD: 171 | UCS / Coordenadas | GEOLOCATEME | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0172 | AutoCAD: 172 | UCS / Coordenadas | GEOMAPIMAGE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0173 | AutoCAD: 173 | UCS / Coordenadas | GEOMAPIMAGEEXPORT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0174 | AutoCAD: 174 | UCS / Coordenadas | LATLONG | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0175 | AutoCAD: 175 | UCS / Coordenadas | LIMITS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0176 | AutoCAD: 176 | Cotas y anotación | DIMLINEAR | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Dimension/DimRotated/DimRotatedInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/createActions/dimlinearoperations.lua) | pending | pendiente |
| ACAD-0177 | AutoCAD: 177 | Cotas y anotación | DIMALIGNED | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Dimension/DimAligned/DimAlignedInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/createActions/dimalignedoperations.lua) | pending | pendiente |
| ACAD-0178 | AutoCAD: 178 | Cotas y anotación | DIMANGULAR | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Dimension/DimAngular/DimAngularInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/createActions/dimangularoperations.lua) | pending | pendiente |
| ACAD-0179 | AutoCAD: 179 | Cotas y anotación | DIMRADIUS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0180 | AutoCAD: 180 | Cotas y anotación | DIMDIAMETER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0181 | AutoCAD: 181 | Cotas y anotación | DIMARC | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0182 | AutoCAD: 182 | Cotas y anotación | DIMORDINATE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Draw/Dimension/DimOrdinate/DimOrdinateInit.js) | [registro](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lcUILua/createActions/dimordinateoperations.lua) | pending | pendiente |
| ACAD-0183 | AutoCAD: 183 | Cotas y anotación | DIMBASELINE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0184 | AutoCAD: 184 | Cotas y anotación | DIMCONTINUE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0185 | AutoCAD: 185 | Cotas y anotación | DIMJOGGED | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0186 | AutoCAD: 186 | Cotas y anotación | DIMCENTER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0187 | AutoCAD: 187 | Cotas y anotación | DIM | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0188 | AutoCAD: 188 | Cotas y anotación | QDIM | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0189 | AutoCAD: 189 | Cotas y anotación | DIMEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0190 | AutoCAD: 190 | Cotas y anotación | DIMTEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0191 | AutoCAD: 191 | Cotas y anotación | DIMSTYLE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0192 | AutoCAD: 192 | Cotas y anotación | DIMBREAK | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0193 | AutoCAD: 193 | Cotas y anotación | DIMSPACE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0194 | AutoCAD: 194 | Cotas y anotación | DIMINSPECT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0195 | AutoCAD: 195 | Cotas y anotación | DIMREASSOC | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0196 | AutoCAD: 196 | Cotas y anotación | DIMDISASSOCIATE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0197 | AutoCAD: 197 | Cotas y anotación | DIMOVERRIDE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0198 | AutoCAD: 198 | Cotas y anotación | DIMUPDATE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0199 | AutoCAD: 199 | Cotas y anotación | DIMTOLERANCE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0200 | AutoCAD: 200 | Cotas y anotación | TOLERANCE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0201 | AutoCAD: 201 | Cotas y anotación | MLEADERSTYLE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0202 | AutoCAD: 202 | Cotas y anotación | MLEADEREDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0203 | AutoCAD: 203 | Cotas y anotación | MLEADERALIGN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0204 | AutoCAD: 204 | Cotas y anotación | MLEADERCOLLECT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0205 | AutoCAD: 205 | Cotas y anotación | TEXTSTYLE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0206 | AutoCAD: 206 | Cotas y anotación | MLSTYLE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0207 | AutoCAD: 207 | Cotas y anotación | TABLESTYLE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0208 | AutoCAD: 208 | Cotas y anotación | TABLEEXPORT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0209 | AutoCAD: 209 | Cotas y anotación | TABLEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0210 | AutoCAD: 210 | Cotas y anotación | ANNOTATIONSCALE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0211 | AutoCAD: 211 | Cotas y anotación | ANNORESET | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0212 | AutoCAD: 212 | Cotas y anotación | ANNOALLVISIBLE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0213 | AutoCAD: 213 | Cotas y anotación | OBJECTSCALE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0214 | AutoCAD: 214 | Bloques, atributos y referencias | BLOCK | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0215 | AutoCAD: 215 | Bloques, atributos y referencias | WBLOCK | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0216 | AutoCAD: 216 | Bloques, atributos y referencias | INSERT | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/Block/InsertBlock/InsertBlockInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0217 | AutoCAD: 217 | Bloques, atributos y referencias | -INSERT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0218 | AutoCAD: 218 | Bloques, atributos y referencias | BEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0219 | AutoCAD: 219 | Bloques, atributos y referencias | BCLOSE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0220 | AutoCAD: 220 | Bloques, atributos y referencias | BATTMAN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0221 | AutoCAD: 221 | Bloques, atributos y referencias | ATTDEF | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0222 | AutoCAD: 222 | Bloques, atributos y referencias | ATTEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0223 | AutoCAD: 223 | Bloques, atributos y referencias | EATTEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0224 | AutoCAD: 224 | Bloques, atributos y referencias | ATTSYNC | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0225 | AutoCAD: 225 | Bloques, atributos y referencias | ATTDISP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0226 | AutoCAD: 226 | Bloques, atributos y referencias | ATTIPEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0227 | AutoCAD: 227 | Bloques, atributos y referencias | BCOUNT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0228 | AutoCAD: 228 | Bloques, atributos y referencias | BASE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0229 | AutoCAD: 229 | Bloques, atributos y referencias | BLOCKICON | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0230 | AutoCAD: 230 | Bloques, atributos y referencias | BLOCKSPALETTE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0231 | AutoCAD: 231 | Bloques, atributos y referencias | BCONSTRUCTION | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0232 | AutoCAD: 232 | Bloques, atributos y referencias | BPARAMETER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0233 | AutoCAD: 233 | Bloques, atributos y referencias | BACTION | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0234 | AutoCAD: 234 | Bloques, atributos y referencias | XREF | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0235 | AutoCAD: 235 | Bloques, atributos y referencias | XATTACH | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0236 | AutoCAD: 236 | Bloques, atributos y referencias | XBIND | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0237 | AutoCAD: 237 | Bloques, atributos y referencias | XCLIP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0238 | AutoCAD: 238 | Bloques, atributos y referencias | XOPEN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0239 | AutoCAD: 239 | Bloques, atributos y referencias | REFEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0240 | AutoCAD: 240 | Bloques, atributos y referencias | REFCLOSE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0241 | AutoCAD: 241 | Bloques, atributos y referencias | REFSET | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0242 | AutoCAD: 242 | Bloques, atributos y referencias | EXTERNALREFERENCES | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0243 | AutoCAD: 243 | Bloques, atributos y referencias | IMAGE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0244 | AutoCAD: 244 | Bloques, atributos y referencias | IMAGEATTACH | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0245 | AutoCAD: 245 | Bloques, atributos y referencias | IMAGECLIP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0246 | AutoCAD: 246 | Bloques, atributos y referencias | IMAGEADJUST | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0247 | AutoCAD: 247 | Bloques, atributos y referencias | IMAGEFRAME | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0248 | AutoCAD: 248 | Bloques, atributos y referencias | IMAGEQUALITY | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0249 | AutoCAD: 249 | Bloques, atributos y referencias | PDFATTACH | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0250 | AutoCAD: 250 | Bloques, atributos y referencias | PDFCLIP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0251 | AutoCAD: 251 | Bloques, atributos y referencias | PDFLAYERS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0252 | AutoCAD: 252 | Bloques, atributos y referencias | PDFIMPORT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0253 | AutoCAD: 253 | Bloques, atributos y referencias | DWFATTACH | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0254 | AutoCAD: 254 | Bloques, atributos y referencias | DGNATTACH | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0255 | AutoCAD: 255 | Bloques, atributos y referencias | DGNIMPORT / DGNEXPORT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0256 | AutoCAD: 256 | Bloques, atributos y referencias | OLE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0257 | AutoCAD: 257 | Bloques, atributos y referencias | DATAEXTRACTION | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0258 | AutoCAD: 258 | Bloques, atributos y referencias | DATALINK | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0259 | AutoCAD: 259 | Bloques, atributos y referencias | DATALINKUPDATE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0260 | AutoCAD: 260 | Bloques, atributos y referencias | ATTACH | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0261 | AutoCAD: 261 | Archivo, impresión y publicación | NEW | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/File/NewFile/NewFileInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0262 | AutoCAD: 262 | Archivo, impresión y publicación | OPEN | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/File/OpenFile/OpenFileInit.js) | sin coincidencia | prototype_partial | test_interop.Interop.test_geometry_layers_z |
| ACAD-0263 | AutoCAD: 263 | Archivo, impresión y publicación | QSAVE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0264 | AutoCAD: 264 | Archivo, impresión y publicación | SAVE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/File/Save/SaveInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0265 | AutoCAD: 265 | Archivo, impresión y publicación | SAVEAS | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/File/SaveAs/SaveAsInit.js) | sin coincidencia | prototype_partial | test_interop.Interop.test_geometry_layers_z |
| ACAD-0266 | AutoCAD: 266 | Archivo, impresión y publicación | SAVEALL | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0267 | AutoCAD: 267 | Archivo, impresión y publicación | CLOSE | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/File/CloseFile/CloseFileInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0268 | AutoCAD: 268 | Archivo, impresión y publicación | CLOSEALL | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0269 | AutoCAD: 269 | Archivo, impresión y publicación | QUIT | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/File/Quit/QuitInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0270 | AutoCAD: 270 | Archivo, impresión y publicación | RECOVER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0271 | AutoCAD: 271 | Archivo, impresión y publicación | RECOVERALL | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0272 | AutoCAD: 272 | Archivo, impresión y publicación | AUDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0273 | AutoCAD: 273 | Archivo, impresión y publicación | PURGE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0274 | AutoCAD: 274 | Archivo, impresión y publicación | DRAWINGRECOVERY | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0275 | AutoCAD: 275 | Archivo, impresión y publicación | DRAWINGUTILITIES | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0276 | AutoCAD: 276 | Archivo, impresión y publicación | PLOT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0277 | AutoCAD: 277 | Archivo, impresión y publicación | -PLOT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0278 | AutoCAD: 278 | Archivo, impresión y publicación | PREVIEW | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0279 | AutoCAD: 279 | Archivo, impresión y publicación | PAGESETUP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0280 | AutoCAD: 280 | Archivo, impresión y publicación | PLOTSTYLE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0281 | AutoCAD: 281 | Archivo, impresión y publicación | STYLESMANAGER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0282 | AutoCAD: 282 | Archivo, impresión y publicación | PLOTTERMANAGER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0283 | AutoCAD: 283 | Archivo, impresión y publicación | PUBLISH | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0284 | AutoCAD: 284 | Archivo, impresión y publicación | EXPORTPDF | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0285 | AutoCAD: 285 | Archivo, impresión y publicación | EXPORT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0286 | AutoCAD: 286 | Archivo, impresión y publicación | IMPORT | 2d | [registro](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/scripts/File/ImportFile/ImportFileInit.js) | sin coincidencia | pending | pendiente |
| ACAD-0287 | AutoCAD: 287 | Archivo, impresión y publicación | DXFOUT/DXFIN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0288 | AutoCAD: 288 | Archivo, impresión y publicación | EXPORTLAYOUT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0289 | AutoCAD: 289 | Archivo, impresión y publicación | LAYOUT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0290 | AutoCAD: 290 | Archivo, impresión y publicación | LAYOUTWIZARD | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0291 | AutoCAD: 291 | Archivo, impresión y publicación | MVIEW | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0292 | AutoCAD: 292 | Archivo, impresión y publicación | MSPACE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0293 | AutoCAD: 293 | Archivo, impresión y publicación | PSPACE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0294 | AutoCAD: 294 | Archivo, impresión y publicación | VPCLIP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0295 | AutoCAD: 295 | Archivo, impresión y publicación | VPMAX / VPMIN | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0296 | AutoCAD: 296 | Archivo, impresión y publicación | SHEETSET | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0297 | AutoCAD: 297 | Archivo, impresión y publicación | ETRANSMIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0298 | AutoCAD: 298 | Archivo, impresión y publicación | ARCHIVE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0299 | AutoCAD: 299 | Archivo, impresión y publicación | 3DPRINT | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0300 | AutoCAD: 300 | Archivo, impresión y publicación | SENDMAIL | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0301 | AutoCAD: 301 | Archivo, impresión y publicación | BROWSER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0302 | AutoCAD: 302 | Archivo, impresión y publicación | SHARE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0303 | AutoCAD: 303 | Archivo, impresión y publicación | CLOUD | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0304 | AutoCAD: 304 | Ayudas de dibujo y configuración | OSNAP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0305 | AutoCAD: 305 | Ayudas de dibujo y configuración | DSETTINGS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0306 | AutoCAD: 306 | Ayudas de dibujo y configuración | SNAP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0307 | AutoCAD: 307 | Ayudas de dibujo y configuración | GRID | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0308 | AutoCAD: 308 | Ayudas de dibujo y configuración | ORTHO | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0309 | AutoCAD: 309 | Ayudas de dibujo y configuración | POLAR | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0310 | AutoCAD: 310 | Ayudas de dibujo y configuración | OTRACK | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0311 | AutoCAD: 311 | Ayudas de dibujo y configuración | DYNMODE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0312 | AutoCAD: 312 | Ayudas de dibujo y configuración | SELECTIONCYCLING | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0313 | AutoCAD: 313 | Ayudas de dibujo y configuración | GRIPS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0314 | AutoCAD: 314 | Ayudas de dibujo y configuración | OPTIONS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0315 | AutoCAD: 315 | Ayudas de dibujo y configuración | CUI | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0316 | AutoCAD: 316 | Ayudas de dibujo y configuración | CUILOAD / CUIUNLOAD | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0317 | AutoCAD: 317 | Ayudas de dibujo y configuración | CUIIMPORT / CUIEXPORT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0318 | AutoCAD: 318 | Ayudas de dibujo y configuración | RIBBON / RIBBONCLOSE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0319 | AutoCAD: 319 | Ayudas de dibujo y configuración | MENUBAR | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0320 | AutoCAD: 320 | Ayudas de dibujo y configuración | TOOLPALETTES | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0321 | AutoCAD: 321 | Ayudas de dibujo y configuración | DESIGNCENTER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0322 | AutoCAD: 322 | Ayudas de dibujo y configuración | SHEETSETHIDE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0323 | AutoCAD: 323 | Ayudas de dibujo y configuración | MARKUP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0324 | AutoCAD: 324 | Ayudas de dibujo y configuración | QNEW | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0325 | AutoCAD: 325 | Ayudas de dibujo y configuración | ALIASEDIT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0326 | AutoCAD: 326 | Ayudas de dibujo y configuración | CMDLINE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0327 | AutoCAD: 327 | Ayudas de dibujo y configuración | COMMANDLINEHIDE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0328 | AutoCAD: 328 | Ayudas de dibujo y configuración | TEXTSCR | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0329 | AutoCAD: 329 | Ayudas de dibujo y configuración | GRAPHSCR | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0330 | AutoCAD: 330 | Ayudas de dibujo y configuración | INPUTSEARCHOPTIONS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0331 | AutoCAD: 331 | Ayudas de dibujo y configuración | COMMANDS | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0332 | AutoCAD: 332 | Ayudas de dibujo y configuración | HELP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0333 | AutoCAD: 333 | Ayudas de dibujo y configuración | ABOUT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0334 | AutoCAD: 334 | Ayudas de dibujo y configuración | INFO | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0335 | AutoCAD: 335 | Programación y automatización | APPLOAD | 2d | sin coincidencia | sin coincidencia | prototype_partial | test_lisp.Lisp.test_original_rectangle_and_c_command |
| ACAD-0336 | AutoCAD: 336 | Programación y automatización | VLISP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0337 | AutoCAD: 337 | Programación y automatización | LOAD | 2d | sin coincidencia | sin coincidencia | prototype_partial | test_lisp.Lisp.test_original_rectangle_and_c_command |
| ACAD-0338 | AutoCAD: 338 | Programación y automatización | SCRIPT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0339 | AutoCAD: 339 | Programación y automatización | RUN / SCRIPT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0340 | AutoCAD: 340 | Programación y automatización | ACTRECORD | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0341 | AutoCAD: 341 | Programación y automatización | ACTSTOP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0342 | AutoCAD: 342 | Programación y automatización | ACTUSERINPUT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0343 | AutoCAD: 343 | Programación y automatización | ACTBASE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0344 | AutoCAD: 344 | Programación y automatización | ACTMANAGER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0345 | AutoCAD: 345 | Programación y automatización | NETLOAD | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0346 | AutoCAD: 346 | Programación y automatización | ARX | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0347 | AutoCAD: 347 | Programación y automatización | VBARUN / VBAIDE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0348 | AutoCAD: 348 | Programación y automatización | VBALOAD | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0349 | AutoCAD: 349 | Programación y automatización | RECORDER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0350 | AutoCAD: 350 | Programación y automatización | DESIGNFEED | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0351 | AutoCAD: 351 | Programación y automatización | FONTALT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0352 | AutoCAD: 352 | Programación y automatización | FONTMAP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0353 | AutoCAD: 353 | Programación y automatización | STARTUP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0354 | AutoCAD: 354 | Sólidos 3D | BOX | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0355 | AutoCAD: 355 | Sólidos 3D | SPHERE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0356 | AutoCAD: 356 | Sólidos 3D | CYLINDER | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0357 | AutoCAD: 357 | Sólidos 3D | CONE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0358 | AutoCAD: 358 | Sólidos 3D | WEDGE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0359 | AutoCAD: 359 | Sólidos 3D | TORUS | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0360 | AutoCAD: 360 | Sólidos 3D | PYRAMID | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0361 | AutoCAD: 361 | Sólidos 3D | POLYSOLID | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0362 | AutoCAD: 362 | Sólidos 3D | EXTRUDE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0363 | AutoCAD: 363 | Sólidos 3D | REVOLVE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0364 | AutoCAD: 364 | Sólidos 3D | SWEEP | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0365 | AutoCAD: 365 | Sólidos 3D | LOFT | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0366 | AutoCAD: 366 | Sólidos 3D | PRESSPULL | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0367 | AutoCAD: 367 | Sólidos 3D | UNION | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0368 | AutoCAD: 368 | Sólidos 3D | SUBTRACT | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0369 | AutoCAD: 369 | Sólidos 3D | INTERSECT | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0370 | AutoCAD: 370 | Sólidos 3D | SLICE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0371 | AutoCAD: 371 | Sólidos 3D | SECTION | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0372 | AutoCAD: 372 | Sólidos 3D | SECTIONPLANE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0373 | AutoCAD: 373 | Sólidos 3D | LIVESECTION | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0374 | AutoCAD: 374 | Sólidos 3D | THICKEN | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0375 | AutoCAD: 375 | Sólidos 3D | INTERFERE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0376 | AutoCAD: 376 | Sólidos 3D | SOLIDEDIT | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0377 | AutoCAD: 377 | Sólidos 3D | FILLETEDGE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0378 | AutoCAD: 378 | Sólidos 3D | CHAMFEREDGE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0379 | AutoCAD: 379 | Sólidos 3D | SHELL | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0380 | AutoCAD: 380 | Sólidos 3D | 3DMOVE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0381 | AutoCAD: 381 | Sólidos 3D | 3DROTATE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0382 | AutoCAD: 382 | Sólidos 3D | 3DSCALE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0383 | AutoCAD: 383 | Sólidos 3D | 3DALIGN | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0384 | AutoCAD: 384 | Sólidos 3D | 3DMIRROR | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0385 | AutoCAD: 385 | Sólidos 3D | 3DARRAY | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0386 | AutoCAD: 386 | Sólidos 3D | 3DFACE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0387 | AutoCAD: 387 | Sólidos 3D | 3DMESH | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0388 | AutoCAD: 388 | Sólidos 3D | FLATSHOT | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0389 | AutoCAD: 389 | Sólidos 3D | SOLVIEW / SOLDRAW / SOLPROF | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0390 | AutoCAD: 390 | Sólidos 3D | VIEWBASE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0391 | AutoCAD: 391 | Sólidos 3D | CONVTOSOLID | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0392 | AutoCAD: 392 | Sólidos 3D | CONVTOSURFACE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0393 | AutoCAD: 393 | Sólidos 3D | CONVTOMESH | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0394 | AutoCAD: 394 | Sólidos 3D | MESH | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0395 | AutoCAD: 395 | Sólidos 3D | MESHSMOOTH | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0396 | AutoCAD: 396 | Sólidos 3D | MESHREFINE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0397 | AutoCAD: 397 | Sólidos 3D | MESHEXTRUDE | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0398 | AutoCAD: 398 | Sólidos 3D | SURFBLEND | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0399 | AutoCAD: 399 | Sólidos 3D | SURFPATCH | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0400 | AutoCAD: 400 | Sólidos 3D | SURFOFFSET | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0401 | AutoCAD: 401 | Sólidos 3D | SURFEXTEND | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0402 | AutoCAD: 402 | Sólidos 3D | SURFSCULPT | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0403 | AutoCAD: 403 | Sólidos 3D | PLANESURF | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0404 | AutoCAD: 404 | Sólidos 3D | NETWORKSURF | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0405 | AutoCAD: 405 | Sólidos 3D | RENDER | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0406 | AutoCAD: 406 | Sólidos 3D | MATERIALS | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0407 | AutoCAD: 407 | Sólidos 3D | LIGHT | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0408 | AutoCAD: 408 | Sólidos 3D | SUNPROPERTIES | excluded_3d | sin coincidencia | sin coincidencia | excluded | pendiente |
| ACAD-0409 | AutoCAD: 409 | Sólidos 3D | SKETCH | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0410 | AutoCAD: 410 | Nube de puntos y datos geoespaciales (CAD base) | POINTCLOUDATTACH | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0411 | AutoCAD: 411 | Nube de puntos y datos geoespaciales (CAD base) | POINTCLOUDINDEX | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0412 | AutoCAD: 412 | Nube de puntos y datos geoespaciales (CAD base) | POINTCLOUDCLIP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0413 | AutoCAD: 413 | Nube de puntos y datos geoespaciales (CAD base) | POINTCLOUDCROP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0414 | AutoCAD: 414 | Nube de puntos y datos geoespaciales (CAD base) | POINTCLOUDOSNAP | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0415 | AutoCAD: 415 | Nube de puntos y datos geoespaciales (CAD base) | POINTCLOUDMANAGER | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0416 | AutoCAD: 416 | Nube de puntos y datos geoespaciales (CAD base) | POINTCLOUDDENSITY | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0417 | AutoCAD: 417 | Nube de puntos y datos geoespaciales (CAD base) | POINTCLOUDVISIBILITY | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0418 | AutoCAD: 418 | Nube de puntos y datos geoespaciales (CAD base) | POINTCLOUDAUTOUPDATE | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0419 | AutoCAD: 419 | Nube de puntos y datos geoespaciales (CAD base) | POINTCLOUDEXTRACT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0420 | AutoCAD: 420 | Nube de puntos y datos geoespaciales (CAD base) | ATTACHURL | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0421 | AutoCAD: 421 | Nube de puntos y datos geoespaciales (CAD base) | HYPERLINK | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0422 | AutoCAD: 422 | Nube de puntos y datos geoespaciales (CAD base) | GEOGRAPHICLOCATION | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| ACAD-0423 | AutoCAD: 423 | Nube de puntos y datos geoespaciales (CAD base) | MAPCONNECT | 2d | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0002 | Civil 3D geoespacial: 2 | Sistemas de coordenadas | MAPCSASSIGN | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0003 | Civil 3D geoespacial: 3 | Sistemas de coordenadas | MAPCSLIBRARY | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0004 | Civil 3D geoespacial: 4 | Sistemas de coordenadas | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0005 | Civil 3D geoespacial: 5 | Sistemas de coordenadas | GEOGRAPHICLOCATION | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0006 | Civil 3D geoespacial: 6 | Sistemas de coordenadas | GEOMAP | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0007 | Civil 3D geoespacial: 7 | Sistemas de coordenadas | GEOMARKPOSITION | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0008 | Civil 3D geoespacial: 8 | Sistemas de coordenadas | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0009 | Civil 3D geoespacial: 9 | Sistemas de coordenadas | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0010 | Civil 3D geoespacial: 10 | Sistemas de coordenadas | MAPINSERT | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0011 | Civil 3D geoespacial: 11 | Importación/exportación GIS | MAPIINSERT | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0012 | Civil 3D geoespacial: 12 | Importación/exportación GIS | EXPORTTOAUTOCAD | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0013 | Civil 3D geoespacial: 13 | Sistemas de coordenadas | MAPWSPACE | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0014 | Civil 3D geoespacial: 14 | Importación/exportación GIS | MAPIMPORT | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0015 | Civil 3D geoespacial: 15 | Importación/exportación GIS | MAPEXPORT | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0016 | Civil 3D geoespacial: 16 | Importación/exportación GIS | MAPCONNECT | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0017 | Civil 3D geoespacial: 17 | Importación/exportación GIS | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0018 | Civil 3D geoespacial: 18 | Importación/exportación GIS | MAPCLEAN | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0019 | Civil 3D geoespacial: 19 | Importación/exportación GIS | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0020 | Civil 3D geoespacial: 20 | Importación/exportación GIS | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0021 | Civil 3D geoespacial: 21 | Importación/exportación GIS | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0022 | Civil 3D geoespacial: 22 | Puntos COGO | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0023 | Civil 3D geoespacial: 23 | Puntos COGO | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0024 | Civil 3D geoespacial: 24 | Puntos COGO | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0025 | Civil 3D geoespacial: 25 | Puntos COGO | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0026 | Civil 3D geoespacial: 26 | Puntos COGO | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0027 | Civil 3D geoespacial: 27 | Superficies / Modelos digitales de terreno | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0028 | Civil 3D geoespacial: 28 | Superficies / Modelos digitales de terreno | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0029 | Civil 3D geoespacial: 29 | Superficies / Modelos digitales de terreno | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0030 | Civil 3D geoespacial: 30 | Superficies / Modelos digitales de terreno | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0031 | Civil 3D geoespacial: 31 | Superficies / Modelos digitales de terreno | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0032 | Civil 3D geoespacial: 32 | Superficies / Modelos digitales de terreno | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0033 | Civil 3D geoespacial: 33 | Superficies / Modelos digitales de terreno | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0034 | Civil 3D geoespacial: 34 | Superficies / Modelos digitales de terreno | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0035 | Civil 3D geoespacial: 35 | Superficies / Modelos digitales de terreno | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0036 | Civil 3D geoespacial: 36 | Topografía (Survey) | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0037 | Civil 3D geoespacial: 37 | Topografía (Survey) | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0038 | Civil 3D geoespacial: 38 | Topografía (Survey) | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0039 | Civil 3D geoespacial: 39 | Topografía (Survey) | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0040 | Civil 3D geoespacial: 40 | Topografía (Survey) | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0041 | Civil 3D geoespacial: 41 | Alineamientos y geometría | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0042 | Civil 3D geoespacial: 42 | Alineamientos y geometría | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0043 | Civil 3D geoespacial: 43 | Alineamientos y geometría | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0044 | Civil 3D geoespacial: 44 | Parcelas y predios | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0045 | Civil 3D geoespacial: 45 | Parcelas y predios | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0046 | Civil 3D geoespacial: 46 | Parcelas y predios | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0047 | Civil 3D geoespacial: 47 | Etiquetas geodésicas | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0048 | Civil 3D geoespacial: 48 | Etiquetas geodésicas | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0049 | Civil 3D geoespacial: 49 | Nubes de puntos y LiDAR | POINTCLOUDATTACH | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0050 | Civil 3D geoespacial: 50 | Nubes de puntos y LiDAR | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
| CIV-0051 | Civil 3D geoespacial: 51 | Cuadrículas y sección | — | geospatial_2d_z | sin coincidencia | sin coincidencia | pending | pendiente |
