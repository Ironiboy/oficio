"""La skill se prueba a sí misma: lo que promete existe, lo que se carga siempre es corto y los ficheros del plugin
son válidos. Uso: python3 -m unittest discover -s tests"""
import json, os, re, subprocess, unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(RAIZ, 'skills', 'oficio')
leer = lambda *p: open(os.path.join(*p), encoding='utf-8').read()


def frontmatter(texto):
    m = re.match(r'^---\n(.*?)\n---\n', texto, re.S)
    assert m, 'SKILL.md sin frontmatter'
    cabecera = m.group(1)
    nombre = re.search(r'^name: (.+)$', cabecera, re.M).group(1).strip()
    desc = re.search(r'^description: >-\n((?:  .*\n?)+)', cabecera + '\n', re.M).group(1)
    return nombre, ' '.join(l.strip() for l in desc.splitlines()), texto[m.end():]


class Skill(unittest.TestCase):
    def setUp(self):
        self.texto = leer(SKILL, 'SKILL.md')
        self.nombre, self.desc, self.cuerpo = frontmatter(self.texto)

    def test_nombre_y_descripcion(self):
        self.assertEqual(self.nombre, 'oficio')
        self.assertLessEqual(len(self.desc), 1024, 'la descripción pasa del límite de 1.024 caracteres')
        self.assertIn('Úsala', self.desc, 'la descripción debe decir cuándo usarla')

    def test_lo_que_se_carga_siempre_es_corto(self):
        self.assertLessEqual(len(self.cuerpo.splitlines()), 150, 'SKILL.md crece: mueve detalle a referencias/')

    def test_las_rutas_citadas_existen(self):
        for ruta in set(re.findall(r'`((?:referencias|puertas-swift)/[^`\s]+)`', self.texto)):
            self.assertTrue(os.path.exists(os.path.join(SKILL, ruta)), ruta)

    def test_ninguna_referencia_huerfana(self):
        for f in os.listdir(os.path.join(SKILL, 'referencias')):
            self.assertIn(f'referencias/{f}', self.texto, f'{f} no se cita en SKILL.md')

    def test_referencias_a_un_nivel(self):
        for f in os.listdir(os.path.join(SKILL, 'referencias')):
            self.assertNotRegex(leer(SKILL, 'referencias', f), r'`referencias/[^`]+\.md`',
                                f'{f} enlaza otra referencia: un solo nivel desde SKILL.md')

    def test_sin_datos_personales(self):
        for base, _, ficheros in os.walk(RAIZ):
            if '.git' in base:
                continue
            for f in ficheros:
                if f.endswith(('.md', '.json', '.sh', '.py')) and f != 'test_skill.py':
                    self.assertNotRegex(leer(base, f), r'/Users/[a-z]|privaterelay|@icloud\.com', os.path.join(base, f))


class Plugin(unittest.TestCase):
    def test_manifiestos(self):
        plugin = json.loads(leer(RAIZ, '.claude-plugin', 'plugin.json'))
        mercado = json.loads(leer(RAIZ, '.claude-plugin', 'marketplace.json'))
        self.assertEqual(plugin['name'], 'oficio')
        self.assertEqual(mercado['plugins'][0]['name'], 'oficio')
        version = re.search(r'^## (\d+\.\d+\.\d+)', leer(RAIZ, 'CHANGELOG.md'), re.M).group(1)
        self.assertEqual(plugin['version'], version, 'la versión del plugin no coincide con el CHANGELOG')

    def test_hook_de_arranque(self):
        hooks = json.loads(leer(RAIZ, 'hooks', 'hooks.json'))['hooks']['SessionStart'][0]
        self.assertIn('compact', hooks['matcher'])
        script = os.path.join(RAIZ, 'hooks', 'arranque.sh')
        self.assertTrue(os.access(script, os.X_OK))
        salida = subprocess.run(['sh', script], capture_output=True, text=True, cwd='/', timeout=10)
        self.assertEqual(salida.returncode, 0)
        self.assertLessEqual(len(salida.stdout.splitlines()), 6, 'el arranque va al contexto cada vez: corto')


class Evals(unittest.TestCase):
    def test_tareas(self):
        e = json.loads(leer(RAIZ, 'evals', 'evals.json'))
        self.assertEqual(e['skill_name'], 'oficio')
        ids = [x['id'] for x in e['evals']]
        self.assertEqual(len(ids), len(set(ids)))
        for x in e['evals']:
            self.assertTrue(x['prompt'] and x['expectations'], x['id'])

    def test_disparo_equilibrado(self):
        q = json.loads(leer(RAIZ, 'evals', 'disparo.json'))
        si = sum(x['should_trigger'] for x in q)
        self.assertGreaterEqual(si, 8)
        self.assertGreaterEqual(len(q) - si, 8)


if __name__ == '__main__':
    unittest.main()
