"""Pruebas de la puerta forma: `python3 -m unittest scripts/gates/test_forma.py`."""
import importlib.machinery, importlib.util, os, unittest

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'forma')
loader = importlib.machinery.SourceFileLoader('forma', path)
forma = importlib.util.module_from_spec(importlib.util.spec_from_loader('forma', loader))
loader.exec_module(forma)

SAMPLE = '''struct S {
    /// { una llave en un comentario no abre nada
    func short() { let s = "}"; _ = s }
    @concurrent
    private static func long(
        a: Int
    ) async -> Int {
        if a > 0 {
            return 1
        }
        /* } */
        return 0
    }
}'''


class Functions(unittest.TestCase):
    def test_lengths_ignore_braces_in_comments_and_strings(self):
        self.assertEqual(forma.functions(SAMPLE.split('\n')), [(3, 1), (5, 9)])


class Cycles(unittest.TestCase):
    def test_mutual_use_inside_a_module_is_a_cycle_and_one_way_is_not(self):
        texts = {'M/A.swift': 'struct A { let b: B }', 'M/B.swift': 'struct B { let a: A }',
                 'M/C.swift': 'struct C { let a: A }'}
        self.assertEqual(forma.cycles(texts, lambda p: 'M'), {'M': ['M/A.swift', 'M/B.swift']})

    def test_other_modules_do_not_close_a_cycle(self):
        texts = {'M/A.swift': 'struct A { let b: B }', 'N/B.swift': 'struct B { let a: A }'}
        self.assertEqual(forma.cycles(texts, lambda p: p[0]), {})


class Duplicates(unittest.TestCase):
    block = '\n'.join(f'let v{i} = f({i})' for i in range(6))

    def test_six_repeated_code_lines_count_in_both_files(self):
        texts = {'A.swift': self.block, 'B.swift': '// otro\n' + self.block}
        self.assertEqual(forma.duplicates(texts), {'A.swift': 6, 'B.swift': 6})

    def test_renamed_copy_of_a_function_is_a_structural_twin(self):
        body = """    func {name}(_ {a}: [Int], limit {b}: Int) -> [Int] {{
        var {c}: [Int] = []
        for {d} in {a} where {d} > 0 {{
            if {c}.count >= {b} {{ break }}
            {c}.append({d} * 2 + 1)
        }}
        guard !{c}.isEmpty else {{ return [] }}
        return {c}.sorted().reversed().map {{ $0 + {b} }}
    }}"""
        one = 'struct A {\n' + body.format(name='first', a='xs', b='n', c='out', d='x') + '\n}'
        two = 'struct B {\n' + body.format(name='second', a='ys', b='m', c='acc', d='y') + '\n}'
        self.assertEqual(forma.similar({'a.swift': one, 'b.swift': two}), {'a.swift': 1, 'b.swift': 1})

    def test_different_functions_are_not_twins(self):
        one = 'struct A {\n    func f(_ xs: [Int]) -> Int {\n' + '\n'.join(
            f'        let v{i} = xs.reduce({i}, +) * {i}' for i in range(12)) + '\n        return v0\n    }\n}'
        two = 'struct B {\n    func g(_ s: String) -> Bool {\n' + '\n'.join(
            f'        if s.hasPrefix("p{i}") {{ print(s.count) }}' for i in range(12)) + '\n        return true\n    }\n}'
        self.assertEqual(forma.similar({'a.swift': one, 'b.swift': two}), {})

    def test_five_lines_or_comments_do_not(self):
        five = '\n'.join(self.block.split('\n')[:5])
        comments = '\n'.join('// igual' for _ in range(8))
        self.assertEqual(forma.duplicates({'A.swift': five, 'B.swift': five,
                                           'C.swift': comments, 'D.swift': comments}), {})


class Regressions(unittest.TestCase):
    base = dict(files={'A.swift': 900}, functions={'A.swift:10': 60}, comment={'M': 0.30},
                dead=['Old (X.swift)'], cycles={'M': ['M/A.swift', 'M/B.swift']},
                duplicated={'A.swift': 12})

    def check(self, **now):
        return forma.regressions({**self.base, **now}, self.base)

    def test_same_state_passes(self):
        self.assertEqual(self.check(), [])

    def test_improving_passes(self):
        self.assertEqual(self.check(files={'A.swift': 500}, functions={}, comment={'M': 0.2},
                                    dead=[]), [])

    def test_growing_big_file_fails(self):
        self.assertEqual(len(self.check(files={'A.swift': 901})), 1)

    def test_new_big_file_fails(self):
        self.assertEqual(len(self.check(files={'A.swift': 900, 'B.swift': 401})), 1)

    def test_moved_long_function_passes_but_longer_fails(self):
        self.assertEqual(self.check(functions={'A.swift:12': 60}), [])
        self.assertEqual(len(self.check(functions={'A.swift:12': 61})), 1)

    def test_splitting_a_file_moves_its_debt_without_regressing(self):
        base = {**self.base, 'functions': {'M/A.swift:10': 60}}
        split = {**base, 'functions': {'M/B.swift:3': 60}}
        self.assertEqual(forma.regressions(split, base), [])
        longer = {**base, 'functions': {'M/B.swift:3': 61}}
        self.assertEqual(len(forma.regressions(longer, base)), 1)

    def test_new_long_function_fails(self):
        self.assertEqual(len(self.check(functions={'A.swift:10': 60, 'B.swift:1': 41})), 1)

    def test_comment_may_not_rise_above_base_or_goal(self):
        self.assertEqual(len(self.check(comment={'M': 0.31})), 1)
        self.assertEqual(self.check(comment={'M': 0.30, 'N': 0.15}), [])
        self.assertEqual(len(self.check(comment={'M': 0.30, 'N': 0.16})), 1)

    def test_a_file_joining_a_cycle_fails_and_leaving_passes(self):
        self.assertEqual(len(self.check(cycles={'M': ['M/A.swift', 'M/B.swift', 'M/C.swift']})), 1)
        self.assertEqual(self.check(cycles={}), [])

    def test_duplication_may_only_shrink(self):
        self.assertEqual(self.check(duplicated={'A.swift': 6}), [])
        self.assertEqual(len(self.check(duplicated={'A.swift': 13})), 1)
        self.assertEqual(len(self.check(duplicated={'A.swift': 12, 'B.swift': 6})), 1)

    def test_structural_twins_may_only_shrink(self):
        base = dict(files={}, functions={}, comment={}, dead=[], cycles={}, duplicated={}, similar={'a.swift': 2})
        now = dict(base, similar={'a.swift': 3})
        self.assertEqual(len(forma.regressions(now, base)), 1)
        self.assertEqual(forma.regressions(dict(base, similar={'a.swift': 1}), base), [])

    def test_new_dead_type_fails(self):
        self.assertEqual(len(self.check(dead=['Old (X.swift)', 'New (Y.swift)'])), 1)


if __name__ == '__main__':
    unittest.main()
