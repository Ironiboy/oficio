"""Pruebas de la lógica pura de las puertas. Sin swift: `python3 -m unittest scripts/gates/test_gates.py`."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gates  # noqa: E402

SAMPLE = '''func f(a: Int, b: Int?, c: Bool) -> Int {
    // if this were code it would count: if && ||
    let s = "if a && b || c ? 1 : 2"
    /* if
       guard */
    if a > 0 && c {
        return 1
    } else if a < 0 {
        return b ?? 0
    }
    for i in 0..<a where i > 2 { _ = i }
    switch a {
    case 1: return 1
    default: break
    }
    #if DEBUG
    print(s)
    #endif
    let t: Int? = c ? 1 : nil
    return t ?? 3
}
'''


class ComplexityTests(unittest.TestCase):
    def test_counts_decision_points_ignoring_comments_and_strings(self):
        # 1 + if + && + else-if + ?? + for + case + ternario + ?? = 9
        self.assertEqual(gates.complexity(SAMPLE.splitlines()), 9)

    def test_repeat_while_is_one_loop(self):
        self.assertEqual(gates.complexity(["repeat {", "x += 1", "} while x < 3"]), 2)

    def test_if_case_counts_once(self):
        self.assertEqual(gates.complexity(["if case .a = x {", "}"]), 2)

    def test_optional_types_and_try_are_not_ternaries(self):
        self.assertEqual(gates.complexity(["let x: Int? = try? f(a?.b)"]), 1)


class CrapTests(unittest.TestCase):
    def test_formula(self):
        self.assertEqual(gates.crap(5, 0.0), 30)
        self.assertEqual(gates.crap(5, 1.0), 5)


class ArgsTests(unittest.TestCase):
    def test_base_is_required(self):
        with self.assertRaisesRegex(gates.GateError, "uso"):
            gates.args_of(["--filter", "X"], "uso: x <base>")

    def test_repeated_options_accumulate(self):
        base, opts = gates.args_of(["HEAD~1", "--allow-uncovered", "A", "--allow-uncovered", "B"], "uso")
        self.assertEqual((base, opts["allow-uncovered"]), ("HEAD~1", ["A", "B"]))


class TestsRanTests(unittest.TestCase):
    def test_counts_from_real_swiftpm_output(self):
        self.assertEqual(gates.tests_ran("warning: No matching test cases were run\n"), 0)
        self.assertEqual(gates.tests_ran(
            "✔ Test run with 53 tests in 5 suites passed after 0.033 seconds."), 53)
        self.assertEqual(gates.tests_ran("Executed 0 tests, with 0 failures\n"
                                         "Executed 3 tests, with 1 failure (0 unexpected)"), 3)


class TouchedTests(unittest.TestCase):
    DIFF = """diff --git a/MiAppKit/Sources/X/A.swift b/MiAppKit/Sources/X/A.swift
--- a/MiAppKit/Sources/X/A.swift
+++ b/MiAppKit/Sources/X/A.swift
@@ -4 +4 @@ func f() {
-    old()
+    new()
@@ -20,2 +19,0 @@
-    gone()
-    gone()
"""

    def test_parse_diff(self):
        touched = gates.parse_diff(self.DIFF)
        self.assertEqual(touched, {"MiAppKit/Sources/X/A.swift": {4, 19, 20}})
        self.assertEqual(gates.parse_diff(self.DIFF, added_only=True),
                         {"MiAppKit/Sources/X/A.swift": {4}})

    def test_diff_pins_prefixes_against_user_git_config(self):
        # `diff.noprefix` o `diff.mnemonicPrefix` en la config del usuario cambiarían `b/`.
        for flag in ("--no-ext-diff", "--src-prefix=a/", "--dst-prefix=b/", "-U0"):
            self.assertIn(flag, gates.DIFF_ARGS)
        self.assertEqual(set(gates.parse_diff(self.DIFF)), {"MiAppKit/Sources/X/A.swift"})

    def test_restrict_keeps_only_files_under_prefixes(self):
        touched = {"MiAppKit/Sources/Core/A.swift": {1}, "MiAppKit/Sources/Design/B.swift": {2}}
        self.assertEqual(gates.restrict(touched, []), touched)
        self.assertEqual(gates.restrict(touched, ["MiAppKit/Sources/Design"]),
                         {"MiAppKit/Sources/Design/B.swift": {2}})

    def test_only_overlapping_function_is_touched(self):
        f = gates.Function("F", "A.swift", 1, 10, 1.0)
        g = gates.Function("G", "A.swift", 12, 30, 1.0)
        self.assertEqual([x.name for x in gates.touched_functions([f, g], {"A.swift": {4}})], ["F"])

    def test_file_with_touched_lines_but_no_function_is_reported(self):
        f = gates.Function("F", "A.swift", 1, 10, 1.0)
        touched = {"A.swift": {4}, "B.swift": {2}, "A2.swift": {50}}
        self.assertEqual(gates.uncovered_files([f], touched), ["A2.swift", "B.swift"])


class LineCoverageTests(unittest.TestCase):
    def test_inner_zero_region_uncovers_its_lines(self):
        # Segmentos de llvm-cov [línea, col, cuenta, tieneCuenta, entraRegión, hueco]:
        # región exterior 1:1-5:2 ejecutada 7 veces, interior 3:10-4:6 nunca.
        segs = [[1, 1, 7, True, True, False], [3, 10, 0, True, True, False],
                [4, 6, 7, True, False, False], [5, 2, 0, False, False, False]]
        # La línea 3 empieza ejecutada; la 4 está entera dentro de la interior.
        self.assertAlmostEqual(gates.line_coverage(segs, 1, 5), 4 / 5)


class MutantTests(unittest.TestCase):
    def test_if_line_mutants(self):
        line = "    if a == b && c {"
        ms = gates.mutate_line(line)
        ops = {op for op, _, _ in ms}
        self.assertTrue({"==->!=", "&&->||", "negate"} <= ops, ops)
        for _, _, m in ms:
            self.assertNotEqual(m, line)
        self.assertIn(("negate", 8, "    if !(a == b && c) {"), ms)
        self.assertIn(("==->!=", 10, "    if a != b && c {"), ms)

    def test_no_mutants_inside_strings_or_generics(self):
        self.assertEqual(gates.mutate_line('    let x: Array<Int> = ["a == b"]'), [])

    def test_comparison_gets_negation_and_boundary_mutants(self):
        ms = gates.mutate_line("    if p >= t {")
        self.assertIn((">=-><", 10, "    if p < t {"), ms)
        self.assertIn((">=->>", 10, "    if p > t {"), ms)
        ops = {op for op, _, _ in gates.mutate_line("    x = a <= b")}
        self.assertEqual(ops, {"<=->>", "<=-><"})
        ops = {op for op, _, _ in gates.mutate_line("    x = a < b")}
        self.assertEqual(ops, {"<->>=", "<-><="})
        ops = {op for op, _, _ in gates.mutate_line("    x = a > b")}
        self.assertEqual(ops, {">-><=", ">->>="})

    def test_no_boundary_mutants_on_ranges_generics_arrows_shifts_strings(self):
        for line in ["    for i in a ..< b {", "    for i in a ... b {", "    let x: Array<Int>",
                     "    func f() -> Bool {", "    let y = x >> 1", '    let s = "a >= b"',
                     "    let z = 1 // a >= b"]:
            self.assertEqual(gates.mutate_line(line), [], line)

    def test_whole_file_is_masked_before_mutating(self):
        lines = ["/*", "a == b", "*/", 'let s = """', "x == y", '"""', "if a == b {", "}"]
        found = gates.file_mutants(lines, set(range(1, 9)))
        self.assertEqual({n for n, *_ in found}, {7})

    def test_delete_call_only_without_value(self):
        self.assertIn(("delete", 5, ""), gates.mutate_line("    try store.save()"))
        self.assertNotIn("delete", {op for op, _, _ in gates.mutate_line("    let x = f()")})
        self.assertNotIn("delete", {op for op, _, _ in gates.mutate_line("    return f()")})


class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "A.swift")
        self.original = "let ñ = 1\r\nif a == 1 { }\n".encode("utf-8")
        Path(self.path).write_bytes(self.original)
        self.backup = os.path.join(self.dir, "backup")

    def test_file_restored_on_interruption(self):
        def boom():
            raise KeyboardInterrupt

        with self.assertRaises(KeyboardInterrupt):
            gates.run_mutant(self.path, 2, "if a != 1 { }", boom, self.backup)
        self.assertEqual(Path(self.path).read_bytes(), self.original)
        self.assertIsNone(gates.recover(self.backup))

    def test_death_mid_mutant_is_restored_on_next_start(self):
        # Muerte de verdad: `os._exit` no ejecuta ningún `finally`.
        code = ("import os, sys; sys.path.insert(0, %r); import gates; "
                "gates.run_mutant(%r, 2, 'if a != 1 { }', lambda: os._exit(9), %r)"
                % (os.path.dirname(os.path.abspath(gates.__file__)), self.path, self.backup))
        self.assertEqual(subprocess.run([sys.executable, "-c", code]).returncode, 9)
        self.assertNotEqual(Path(self.path).read_bytes(), self.original)
        self.assertEqual(gates.recover(self.backup), self.path)
        self.assertEqual(Path(self.path).read_bytes(), self.original)
        self.assertIsNone(gates.recover(self.backup))


class LeftoverMutantTests(unittest.TestCase):
    def test_both_gates_restore_and_abort_if_a_previous_run_died(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "A.swift")
        old_backup = gates.BACKUP
        gates.BACKUP = os.path.join(d, "gates-mutant")
        try:
            for gate in (gates.crap_main, gates.mutants_main):
                Path(path).write_bytes(b"mutado")
                Path(gates.BACKUP + ".orig").write_bytes(b"original")
                Path(gates.BACKUP + ".path").write_text(path, encoding="utf-8")
                with self.assertRaisesRegex(gates.GateError, "restaurado"):
                    gate(["HEAD", "--filter", "X"])
                self.assertEqual(Path(path).read_bytes(), b"original")
        finally:
            gates.BACKUP = old_backup


class EquivalentTests(unittest.TestCase):
    def test_entry_without_reason_fails(self):
        with self.assertRaisesRegex(gates.GateError, "motivo"):
            gates.parse_equivalents(["A.swift:3:9:==->!="])

    def test_entry_without_column_fails(self):
        with self.assertRaisesRegex(gates.GateError, "columna"):
            gates.parse_equivalents(["A.swift:3:==->!=  # simétrico"])

    def test_entries_with_reason(self):
        self.assertEqual(
            gates.parse_equivalents(["# cabecera", "", "A.swift:3:9:==->!=  # simétrico"]),
            {"A.swift:3:9:==->!="})


if __name__ == "__main__":
    unittest.main()
