"""Puertas deterministas del guantelete (CRAP y mutantes) sobre un paquete Swift (`OFICIO_PKG`).

Lógica pura arriba (la prueban `test_gates.py`), CLI abajo. Solo stdlib de python3 3.9.
"""
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from collections import namedtuple

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                      cwd=os.path.dirname(os.path.abspath(__file__))).stdout.strip()
# El paquete Swift a medir, relativo a la raíz del repo (p. ej. `MiAppKit`; `.` si el paquete es el repo).
PKG = os.environ.get("OFICIO_PKG", ".")
SOURCES = ("" if PKG == "." else PKG.rstrip("/") + "/") + "Sources/"
# Respaldo del fichero mutado (`.orig`) y su ruta (`.path`); dentro de `.build/`, ya ignorado.
BACKUP = os.path.join(ROOT, ".build", "gates-mutant")
ENV = dict(os.environ, DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer")


class GateError(Exception):
    pass


# ---------------------------------------------------------------- texto Swift

def mask(lines):
    """Cambia comentarios y literales de cadena por espacios, conservando columnas y líneas.

    ponytail: no entiende interpolación anidada con comillas (`"\\(f("x"))"`) ni cadenas
    raw con `#` dentro; basta para contar y para no mutar dentro de cadenas.
    """
    out, state, depth, raw = [], None, 0, ""
    for line in lines:
        res, i = [], 0
        while i < len(line):
            ch, rest = line[i], line[i:]
            if state is None:
                if rest.startswith("//"):
                    res.append(" " * (len(line) - i)); break
                if rest.startswith("/*"):
                    state, depth = "block", 1; res.append("  "); i += 2; continue
                m = re.match(r'(#*)("""|")', rest)
                if m:
                    raw, quote = m.group(1), m.group(2)
                    state = "multi" if quote == '"""' else "str"
                    res.append(m.group(0)); i += len(m.group(0)); continue
                res.append(ch); i += 1
            elif state == "block":
                if rest.startswith("/*"):
                    depth += 1; res.append("  "); i += 2
                elif rest.startswith("*/"):
                    depth -= 1; res.append("  "); i += 2
                    if depth == 0: state = None
                else:
                    res.append(" "); i += 1
            else:
                close = ('"""' if state == "multi" else '"') + raw
                if ch == "\\" and not raw:
                    res.append("  "[: len(rest[:2])]); i += 2; continue
                if rest.startswith(close):
                    state = None; res.append(close); i += len(close); continue
                res.append(" "); i += 1
        if state == "str":  # una cadena simple no cruza líneas
            state = None
        out.append("".join(res))
    return out


DECISIONS = [
    r"(?<![#\w])if\b", r"\bguard\b", r"\bfor\b", r"\brepeat\b", r"^\s*case\b", r"\bcatch\b",
    r"&&", r"\|\|", r"\?\?",
    r"(?<!\}\s)(?<!\})\bwhile\b",  # el `while` de `repeat { } while` ya lo contó `repeat`
    r"\s\?\s",                      # ternario: `?` con espacio a ambos lados
]


def complexity(lines):
    """1 + puntos de decisión. ponytail: léxico, no sintáctico; `else if` cuenta por su `if`."""
    return 1 + sum(len(re.findall(p, l)) for l in mask(lines) for p in DECISIONS)


def crap(c, cov):
    return c * c * (1 - cov) ** 3 + c


def line_coverage(segments, start, end):
    """Cobertura de línea de [start, end] con la regla de llvm-cov (LineCoverageStats)."""
    mapped = covered = 0
    segs = sorted(segments, key=lambda s: (s[0], s[1]))
    wrapped, k = None, 0
    for line in range(1, end + 1):
        on_line = []
        while k < len(segs) and segs[k][0] == line:
            on_line.append(segs[k]); k += 1
        if line >= start:
            starts = [s for s in on_line if s[3] and s[4] and not s[5]]
            skipped = bool(on_line) and not on_line[0][3] and on_line[0][4]
            if not skipped and ((wrapped and wrapped[3]) or starts):
                mapped += 1
                count = max([wrapped[2] if wrapped else 0] + [s[2] for s in starts])
                covered += count > 0
        if on_line:
            wrapped = on_line[-1]
    return covered / mapped if mapped else 1.0


# ---------------------------------------------------------------- diff

# Fijados a mano: `diff.noprefix`, `diff.mnemonicPrefix` o un `diff.external` del usuario cambiarían
# la cabecera `+++ b/…` que lee parse_diff.
DIFF_ARGS = ["diff", "--no-ext-diff", "--no-color", "--src-prefix=a/", "--dst-prefix=b/", "-U0"]


def parse_diff(text, added_only=False):
    """{fichero: líneas nuevas tocadas}. Un borrado puro marca la línea que lo rodea."""
    touched, path = {}, None
    for l in text.splitlines():
        if l.startswith("+++ "):
            path = None if l.endswith("/dev/null") else l[6:]
        m = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", l)
        if m and path:
            start, n = int(m.group(1)), int(m.group(2) or 1)
            lines = set(range(start, start + n)) if n else (set() if added_only else {start, start + 1})
            if lines:
                touched.setdefault(path, set()).update(lines)
    return touched


def changed_lines(base, added_only=False):
    touched = parse_diff(git(*DIFF_ARGS, base, "--", SOURCES), added_only)
    for path in git("ls-files", "--others", "--exclude-standard", "--", SOURCES).split():
        if path.endswith(".swift"):
            touched[path] = set(range(1, len(read_lines(path)) + 1))
    return {p: ls for p, ls in touched.items() if p.endswith(".swift")}


Function = namedtuple("Function", "name file start end cov")


def restrict(touched, prefixes):
    """Solo los ficheros bajo alguna de `prefixes`; sin prefijos, todos."""
    if not prefixes:
        return touched
    return {p: ls for p, ls in touched.items() if any(p.startswith(x) for x in prefixes)}


def touched_functions(functions, touched):
    return [f for f in functions if any(f.start <= l <= f.end for l in touched.get(f.file, ()))]


def uncovered_files(functions, touched):
    """Ficheros con líneas tocadas donde no casa ninguna función del export: no se pueden medir."""
    hit = {f.file for f in touched_functions(functions, touched)}
    return sorted(set(touched) - hit)


def tests_ran(output):
    """Tests ejecutados según la salida de `swift test` (swift-testing y XCTest).

    Con un filtro que no casa, SwiftPM sale con 0 e imprime solo «No matching test cases were run».
    """
    counts = re.findall(r"Test run with (\d+) tests?|Executed (\d+) tests?", output)
    return max((int(a or b) for a, b in counts), default=0)


# ---------------------------------------------------------------- mutantes

# Comparaciones: negación y frontera (`>=`↔`>`, `<=`↔`<`); las fronteras son las que un test sin
# caso límite no ve.
SWAPS = {"==": ["!="], "!=": ["=="], "<": [">=", "<="], ">=": ["<", ">"], ">": ["<=", ">="],
         "<=": [">", "<"], "&&": ["||"], "||": ["&&"], "+": ["-"], "-": ["+"]}
SPACED = {"<", ">", "+", "-"}  # sin espacios alrededor son genéricos, flechas o signos
COND = re.compile(r"^(\s*(?:\}\s*else\s+)?)(if|guard)\s+(.+?)(\s+(?:else\s*)?\{\s*)$")
CALL = re.compile(r"^(?:(?:try[?!]?|await)\s+)*[A-Za-z_][\w.?!]*\(.*\)$")


def mutate_line(line, masked=None):
    """[(operador, columna 1-based, línea mutada)]. `masked`: la línea ya sin comentarios ni cadenas."""
    masked = mask([line])[0] if masked is None else masked
    out = []
    for m in re.finditer(r"[=!<>&|+\-*/%^~?.]+", masked):
        op = m.group(0)
        if op not in SWAPS:
            continue
        a, b = m.start(), m.end()
        if op in SPACED and not (line[a - 1:a] == " " and line[b:b + 1] == " "):
            continue
        out += [(f"{op}->{s}", a + 1, line[:a] + s + line[b:]) for s in SWAPS[op]]
    for m in re.finditer(r"\b(true|false)\b", masked):
        flip = "false" if m.group(1) == "true" else "true"
        out.append((f"{m.group(1)}->{flip}", m.start() + 1, line[:m.start()] + flip + line[m.end():]))
    c = COND.match(masked)
    if c and not re.match(r"(let|var|case)\b", c.group(3)) and not re.search(r",\s*(let|var|case)\b", c.group(3)):
        cond = line[c.start(3):c.end(3)]
        out.append(("negate", c.start(3) + 1, f"{line[:c.start(3)]}!({cond}){line[c.end(3):]}"))
    stripped = masked.strip()
    if CALL.match(stripped) and not re.match(r"(return|throw|super\.init|self\.init|init|precondition|assert)\b", stripped):
        out.append(("delete", len(masked) - len(masked.lstrip()) + 1, ""))
    return out


def file_mutants(lines, touched):
    """[(línea, operador, columna, mutada)] de las líneas tocadas, con el fichero entero enmascarado."""
    masked = mask(lines)
    return [(n, *m) for n in sorted(touched) if n <= len(lines) for m in mutate_line(lines[n - 1], masked[n - 1])]


def write_atomic(path, data):
    """Temporal en el mismo directorio + `os.replace`: el fichero nunca queda a medias."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".gates-")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        if os.path.exists(path):  # mkstemp crea 0600; el fichero conserva sus permisos
            os.chmod(tmp, os.stat(path).st_mode & 0o7777)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def recover(backup):
    """Si una ejecución anterior murió con un mutante puesto, devuelve el original. → ruta o None."""
    if not os.path.exists(backup + ".path"):
        return None
    with open(backup + ".path", encoding="utf-8") as fh:
        path = fh.read()
    with open(backup + ".orig", "rb") as fh:
        write_atomic(path, fh.read())
    os.unlink(backup + ".path")
    os.unlink(backup + ".orig")
    return path


def run_mutant(path, lineno, mutated, check, backup):
    """Aplica el mutante, llama a `check()` y restaura el fichero pase lo que pase.

    Antes de tocar nada deja un respaldo en `backup.orig`/`backup.path` (en ese orden: `.path`
    es la marca de que hay algo que restaurar), para que `recover` lo arregle si el proceso muere
    sin pasar por el `finally` (SIGKILL, apagón).
    """
    with open(path, "rb") as fh:
        original = fh.read()
    lines = original.decode("utf-8").splitlines(keepends=True)
    old = lines[lineno - 1]
    lines[lineno - 1] = mutated + old[len(old.rstrip("\r\n")):]
    write_atomic(backup + ".orig", original)
    write_atomic(backup + ".path", path.encode("utf-8"))
    try:
        write_atomic(path, "".join(lines).encode("utf-8"))
        return check()
    finally:
        recover(backup)


EQUIVALENT = re.compile(r"^\S+\.swift:\d+:\d+:\S+$")


def parse_equivalents(lines):
    keys = set()
    for n, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, reason = line.partition("#")
        if not sep or not reason.strip():
            raise GateError(f"equivalent-mutants.txt:{n}: falta el `# motivo` en «{line}»")
        if not EQUIVALENT.match(key.strip()):
            raise GateError(f"equivalent-mutants.txt:{n}: se espera fichero:línea:columna:operador en «{line}»")
        keys.add(key.strip())
    return keys


# ---------------------------------------------------------------- utilidades de CLI

def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True,
                          encoding="utf-8").stdout


def read_lines(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read().splitlines()


def swift(*args, timeout=None):
    """("ok" | "fail" | "timeout", salida).

    Grupo de procesos propio para poder matar entero lo que cuelga (swift-test lanza hijos);
    por eso también hay que matarlo a mano si nos interrumpen a nosotros.
    """
    p = subprocess.Popen(["swift", *args, "--package-path", PKG], cwd=ROOT, env=ENV, text=True,
                         encoding="utf-8", errors="replace", stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, start_new_session=True)
    try:
        out, _ = p.communicate(timeout=timeout)
        return ("ok" if p.returncode == 0 else "fail"), out
    except subprocess.TimeoutExpired:
        kill_group(p)
        return "timeout", p.communicate()[0]
    except BaseException:
        kill_group(p)
        p.wait()
        raise


def kill_group(p):
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:  # ya había terminado
        pass
    kill_orphan_helpers()


def kill_orphan_helpers():
    """`swiftpm-testing-helper` se va a su propio grupo: matar el de swift lo deja huérfano y,
    con un mutante que cuelga, gastando núcleos sin fin. Solo los de este árbol."""
    ps = subprocess.run(["ps", "-Ao", "pid=,ppid=,command="], capture_output=True, text=True).stdout
    for line in ps.splitlines():
        pid, ppid, command = line.split(None, 2)
        if ppid == "1" and "swiftpm-testing-helper" in command and os.path.join(ROOT, PKG) + "/" in command:
            try:
                os.kill(int(pid), signal.SIGKILL)
            except ProcessLookupError:
                pass


def args_of(argv, usage):
    """(base, {opción: [valores]}). La base es obligatoria: contra qué se mide no se adivina."""
    base, opts, it = None, {}, iter(argv)
    for a in it:
        if a.startswith("--"):
            value = next(it, None)
            if value is None:
                raise GateError(usage)
            opts.setdefault(a[2:], []).append(value)
        elif base is None:
            base = a
        else:
            raise GateError(usage)
    if base is None:
        raise GateError(usage)
    return base, opts


def functions_from_export(export):
    """Funciones de `SOURCES` con sus límites y cobertura de línea."""
    data = export["data"][0]
    segments = {f["filename"]: f["segments"] for f in data["files"]}
    seen = {}
    for fn in data["functions"]:
        path = fn["filenames"][0]
        rel = os.path.relpath(path, ROOT)
        own = [r for r in fn["regions"] if r[5] == 0]
        if not rel.startswith(SOURCES) or not own:
            continue
        start, end = min(r[0] for r in own), max(r[2] for r in own)
        # Una genérica sale una vez por especialización, con los mismos segmentos de fichero.
        seen.setdefault((rel, start, end), Function(fn["name"], rel, start, end,
                                                    line_coverage(segments.get(path, []), start, end)))
    funcs = list(seen.values())
    names = subprocess.run(["xcrun", "swift-demangle", "--simplified"], input="\n".join(f.name for f in funcs),
                           capture_output=True, text=True, encoding="utf-8", env=ENV).stdout.splitlines()
    return [f._replace(name=n) for f, n in zip(funcs, names)] if len(names) == len(funcs) else funcs


def coverage_export():
    """`llvm-cov export` de todos los bundles de tests.

    El JSON que deja SwiftPM (`--show-codecov-path`) solo cubre el primer `.xctest`: con un bundle
    por target de tests, se pierden los demás módulos.
    """
    _, out = swift("test", "--show-codecov-path")
    codecov = os.path.dirname(out.strip().splitlines()[-1])
    products = os.path.dirname(codecov)
    objects = []
    for b in sorted(os.listdir(products)):
        if b.endswith(".xctest"):
            binary = os.path.join(products, b, "Contents", "MacOS", b[:-len(".xctest")])
            if os.path.exists(binary):
                objects += ["-object", binary]
    p = subprocess.run(["xcrun", "llvm-cov", "export", "-instr-profile",
                        os.path.join(codecov, "default.profdata")] + objects[1:],
                       capture_output=True, text=True, encoding="utf-8", env=ENV)
    if p.returncode:
        raise GateError("crap: llvm-cov export falló:\n" + p.stderr[-2000:])
    return json.loads(p.stdout)


def abort_if_leftover_mutant(gate):
    restored = recover(BACKUP)
    if restored:
        raise GateError(f"{gate}: una ejecución anterior de mutants murió con un mutante puesto en "
                        f"{restored}; lo he restaurado. Comprueba `git diff` y vuelve a lanzar.")


def nothing_touched(gate, base):
    raise GateError(f"{gate}: nada tocado en {SOURCES} desde {base}; ¿base equivocada?")


# ---------------------------------------------------------------- crap

def crap_main(argv):
    usage = "uso: crap <base> [--filter TargetDeTests] [--max 8] [--allow-uncovered fichero]…"
    base, opts = args_of(argv, usage)
    abort_if_leftover_mutant("crap")
    limit = float(opts.get("max", ["8"])[-1])
    touched = changed_lines(base)
    if not touched:
        nothing_touched("crap", base)
    test = ["test", "--enable-code-coverage"] + (["--filter", opts["filter"][-1]] if "filter" in opts else [])
    print("crap: swift " + " ".join(test), flush=True)
    status, out = swift(*test)
    if tests_ran(out) == 0:
        raise GateError("crap: `swift test` no ejecutó ningún test; ¿el --filter casa con algo?\n" + out[-1000:])
    if status != "ok":
        print(out[-3000:])
        print("crap: los tests fallan; la cobertura de abajo es la de una pasada rota.")
    funcs = functions_from_export(coverage_export())
    allowed = set(opts.get("allow-uncovered", []))
    unmeasured = uncovered_files(funcs, touched)
    blind = [f for f in unmeasured if f not in allowed]
    rows = []
    for f in touched_functions(funcs, touched):
        c = complexity(read_lines(f.file)[f.start - 1:f.end])
        rows.append((crap(c, f.cov), c, f))
    rows.sort(key=lambda r: -r[0])
    print(f"{'CRAP':>7} {'compl':>5} {'cob':>5}  función  (fichero:línea)")
    for score, c, f in rows:
        flag = " ✗" if score > limit else ""
        print(f"{score:7.1f} {c:5d} {f.cov:5.0%}  {f.name[:70]}  ({f.file[len(SOURCES):]}:{f.start}){flag}")
    bad = [r for r in rows if r[0] > limit]
    print(f"crap: {len(rows)} funciones tocadas, {len(bad)} por encima de {limit:g}.")
    for f in sorted(set(unmeasured) & allowed):
        print(f"crap: {f} tiene líneas tocadas sin medir; eximido con --allow-uncovered.")
    for f in blind:
        # Un `#if os(iOS)` no se compila en macOS y no sale en el export: se dice, no se aprueba.
        print(f"crap: {f} tiene líneas tocadas sin ninguna función medida (¿#if de otra plataforma, "
              f"solo declaraciones?). Revísalo o pasa --allow-uncovered {f}.")
    return 1 if bad or blind or status != "ok" else 0


# ---------------------------------------------------------------- mutants

def mutants_main(argv):
    usage = "uso: mutants <base> --filter TargetDeTests [--only <Paquete>/Sources/Módulo]…"
    base, opts = args_of(argv, usage)
    if "filter" not in opts:
        raise GateError(usage)
    abort_if_leftover_mutant("mutants")
    os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
    eq_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "equivalent-mutants.txt")
    equivalents = set()
    if os.path.exists(eq_path):
        with open(eq_path, encoding="utf-8") as fh:
            equivalents = parse_equivalents(fh.read().splitlines())
    status_before = git("status", "--porcelain") + git("diff", "--no-ext-diff", "--no-color")
    # SIGTERM como Ctrl-C, para que el `finally` de run_mutant restaure también entonces.
    signal.signal(signal.SIGTERM, signal.default_int_handler)

    touched = restrict(changed_lines(base, added_only=True), opts.get("only", []))
    if not touched:
        nothing_touched("mutants", base)
    plan = []
    for rel, lines in sorted(touched.items()):
        src = read_lines(rel)
        plan += [(rel, n, op, col, src[n - 1], m) for n, op, col, m in file_mutants(src, lines)]
    if not plan:
        print(f"mutants: ningún mutante sobre las líneas tocadas desde {base}.")
        return 0

    t0 = time.time()
    test = ["test", "--skip-build", "--filter", opts["filter"][-1]]
    status, out = swift("build", "--build-tests")
    if status != "ok":
        raise GateError("mutants: no compila sin mutantes.\n" + out[-2000:])
    status, out = swift(*test)
    if status != "ok":
        raise GateError("mutants: la suite no pasa sin mutantes; no hay nada que medir.\n" + out[-3000:])
    if tests_ran(out) == 0:
        raise GateError("mutants: `swift test` no ejecutó ningún test; ¿el --filter casa con algo?")
    timeout = 10 * (time.time() - t0) + 60
    print(f"mutants: {len(plan)} mutantes, filtro {opts['filter'][-1]}", flush=True)

    tally = {"equivalent": 0, "killed": 0, "compile": 0, "timeout": 0, "survived": 0}
    survivors, timeouts = [], []
    try:
        for i, (rel, n, op, col, old, new) in enumerate(plan, 1):
            def check():
                built, _ = swift("build", "--build-tests", timeout=timeout)
                if built != "ok":
                    return "compile" if built == "fail" else "timeout"
                ran, _ = swift(*test, timeout=timeout)
                return {"ok": "survived", "fail": "killed", "timeout": "timeout"}[ran]
            result = run_mutant(os.path.join(ROOT, rel), n, new, check, BACKUP)
            print(f"  [{i}/{len(plan)}] {rel[len(SOURCES):]}:{n}:{col} {op}: {result}", flush=True)
            key = f"{rel}:{n}:{col}:{op}"
            # Declarado también vale para un cuelgue: el test que no termina lo ha detectado.
            if result in ("survived", "timeout") and key in equivalents:
                result = "equivalent"
            tally[result] += 1
            if result == "survived":
                survivors.append((key, old, new))
            elif result == "timeout":
                timeouts.append(key)
    finally:
        if git("status", "--porcelain") + git("diff", "--no-ext-diff", "--no-color") != status_before:
            print("mutants: ¡EL ÁRBOL NO QUEDÓ COMO ESTABA! Revisa `git diff`.", file=sys.stderr)
            sys.exit(3)

    print(f"mutants: {len(plan)} generados, {tally['killed']} muertos, {tally['compile']} muertos por "
          f"compilación, {tally['timeout']} sin veredicto (timeout), {tally['equivalent']} equivalentes declarados, "
          f"{tally['survived']} supervivientes "
          f"({time.time() - t0:.0f} s).")
    for key, old, new in survivors:
        print(f"  {key}\n    - {old.strip()}\n    + {new.strip() or '(línea borrada)'}")
    for key in timeouts:
        print(f"  sin veredicto (timeout {timeout:.0f} s): {key}")
    return 1 if survivors or timeouts else 0


def main(name, argv):
    try:
        sys.exit({"crap": crap_main, "mutants": mutants_main}[name](argv))
    except GateError as e:
        print(e, file=sys.stderr)
        sys.exit(2)
