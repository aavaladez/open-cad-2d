"""Explicit, bounded AutoLISP subset; never Python eval or OS execution."""
import json
import operator
import re
from copy import deepcopy
from functools import reduce
from pathlib import Path


class Symbol(str):
    pass


def parse(source):
    if len(source) > 100_000:
        raise ValueError("LSP supera 100000 caracteres")
    tokens = re.findall(r';[^\n]*|"(?:\\.|[^"\\])*"|[()\']|[^\s()\';]+', source)
    tokens = [t for t in tokens if not t.startswith(";")]
    index = 0

    def read(depth=0):
        nonlocal index
        if depth > 80 or index >= len(tokens):
            raise ValueError("LSP incompleto o demasiado anidado")
        token = tokens[index]
        index += 1
        if token == "(":
            result = []
            while index < len(tokens) and tokens[index] != ")":
                result.append(read(depth+1))
            if index == len(tokens):
                raise ValueError("Falta paréntesis de cierre")
            index += 1
            return result
        if token == ")":
            raise ValueError("Paréntesis inesperado")
        if token == "'":
            return [Symbol("QUOTE"), read(depth+1)]
        if token.startswith('"'):
            return json.loads(token)
        try:
            return float(token) if any(c in token.lower() for c in ".e") else int(token)
        except ValueError:
            return Symbol(token.upper())
    forms = []
    while index < len(tokens):
        forms.append(read())
    return forms


class LispRuntime:
    allowed_commands = {"LINE", "CIRCLE", "MOVE", "ERASE", "LAYER", "DIST"}

    def __init__(self, bus):
        self.bus = bus
        bus.lisp = self
        self.globals = {"NIL": None, "T": True}
        self.functions = {}
        self.remaining = 10000
        self.output = []

    def run(self, source):
        forms = parse(source)
        state = deepcopy((self.globals, self.functions, self.output))
        self.remaining = 10000
        try:
            with self.bus.document.transaction():
                result = None
                for form in forms:
                    result = self.evaluate(form, self.globals)
                return result
        except Exception:
            self.globals, self.functions, self.output = state
            raise

    def load(self, path):
        p = Path(path)
        if p.suffix.lower() != ".lsp" or p.stat().st_size > 100_000:
            raise ValueError("Archivo .LSP de hasta 100000 bytes requerido")
        return self.run(p.read_text(encoding="utf-8-sig"))

    def call_command(self, name):
        return self.run("(C:" + name.upper() + ")")

    def evaluate(self, form, env, depth=0):
        self.remaining -= 1
        if self.remaining < 0 or depth > 80:
            raise ValueError("Límite de ejecución LSP alcanzado")
        if isinstance(form, Symbol):
            if form not in env:
                raise ValueError(f"Símbolo no definido: {form}")
            return env[form]
        if not isinstance(form, list):
            return form
        if not form:
            return None
        name = str(form[0]).upper()
        args = form[1:]
        ev = lambda x: self.evaluate(x, env, depth+1)
        if name == "QUOTE" and len(args) == 1:
            return None if args[0] == [] else args[0]
        if name == "SETQ":
            if not args or len(args) % 2:
                raise ValueError("SETQ requiere pares símbolo/valor")
            for key, value in zip(args[::2], args[1::2]):
                if not isinstance(key, Symbol) or key in ("NIL", "T"):
                    raise ValueError("Variable SETQ inválida")
                env[key] = ev(value)
            return env[args[-2]]
        if name == "DEFUN":
            if len(args) < 3 or not isinstance(args[0], Symbol) or not isinstance(args[1], list):
                raise ValueError("DEFUN nombre (argumentos / locales) cuerpo")
            if not all(isinstance(x, Symbol) for x in args[1]):
                raise ValueError("Argumentos DEFUN inválidos")
            self.functions[args[0]] = (args[1], args[2:])
            return args[0]
        if name == "IF" and len(args) in (2, 3):
            condition = ev(args[0])
            return ev(args[1]) if condition is not None and condition is not False and condition != [] else (ev(args[2]) if len(args) == 3 else None)
        if name == "PROGN":
            result = None
            for a in args:
                result = ev(a)
            return result
        values = [ev(a) for a in args]
        if name in self.functions:
            params, body = self.functions[name]
            split = params.index("/") if "/" in params else len(params)
            formal = params[:split]
            if len(values) != len(formal):
                raise ValueError("Número de argumentos incorrecto")
            local = dict(self.globals)
            local.update(zip(formal, values))
            local.update({p: None for p in params[split+1:]})
            result = None
            for a in body:
                result = self.evaluate(a, local, depth+1)
            # Prototype SETQ within DEFUN is local; document this deviation.
            return result
        if name == "COMMAND":
            if not values or not isinstance(values[0], str):
                raise ValueError("COMMAND requiere un nombre")
            command = values[0].upper().removeprefix("_")
            command = self.bus.aliases.get(command, command)
            if command not in self.allowed_commands:
                raise ValueError("Comando LSP no permitido: " + command)
            tail = values[1:]
            if tail and tail[-1] == "":
                tail = tail[:-1]
            self.bus.execute(command, *tail)
            return None
        if name == "PRINC" and len(values) <= 1:
            if values:
                self.output.append(str(values[0]))
            return values[0] if values else None
        if name == "LIST":
            return values or None
        if name == "CAR" and len(values) == 1:
            return values[0][0] if values[0] else None
        if name == "CDR" and len(values) == 1:
            return values[0][1:] or None if values[0] else None
        if name == "CONS" and len(values) == 2:
            return [values[0]] + (values[1] or [])
        if name == "LENGTH" and len(values) == 1:
            return len(values[0] or [])
        if name == "+":
            return sum(values)
        if name == "*":
            return reduce(operator.mul, values, 1)
        if name in ("-", "/") and values:
            if len(values) == 1:
                return -values[0] if name == "-" else 1/values[0]
            return reduce(operator.sub if name == "-" else operator.truediv, values)
        if name == "=" and len(values) == 2:
            return True if values[0] == values[1] else None
        raise ValueError("Función AutoLISP no implementada: " + name)
