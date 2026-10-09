; Rutina original OPEN CAD. Subconjunto: quote, command, defun, princ.
(defun c:marco ()
  (command "_LINE" '(0 0 2) '(120 0 2) '(120 80 2) '(0 80 2) '(0 0 2) "")
  (command "_CIRCLE" '(60 40 2) 18)
  (princ "Marco creado"))
(c:marco)

