; Rutina original GPL-3.0-or-later OPEN CAD. Entradas completas del subconjunto.
; La carga define comandos; PLANO_A1 dibuja en la capa vigente con Z=7.
; COMMAND devuelve NIL. No depende de IDs temporales ni de acceso al sistema.
(defun c:plano_a1 ()
  (command "LINE" '(120 0 7) '(150 0 7) "")
  (command "CIRCLE" '(80 20 7) 10)
  (command "ARC" '(50 0 7) '(60 10 7) '(70 0 7))
  (command "PLINE" '(0 0 7) '(40 0 7) '(40 30 7) '(0 30 7) "CLOSE")
  (command "DIMLINEAR" '(0 0 7) '(40 0 7) '(0 -10 7))
  (command "DIMALIGNED" '(0 0 7) '(40 30 7) '(-10 10 7))
  (command "DIMRADIUS" '(80 20 7) '(90 20 7))
  (princ "Plano LSP creado"))

; Los IDs numéricos del bridge OPEN CAD no son ENAME AutoLISP.
; Esta función permite probar modificación sobre un dibujo existente conocido.
(defun cad_ajustar (objetivo corte limite)
  (command "TRIM" corte objetivo '(9 0))
  (command "EXTEND" limite objetivo '(5 0))
  (command "OFFSET" objetivo 2 '(0 2))
  (command "COPY" objetivo '(0 5 3))
  (command "ROTATE" objetivo '(0 0 100) 90)
  (command "SCALE" objetivo '(0 0 100) 2)
  (princ "Ajuste LSP creado"))
