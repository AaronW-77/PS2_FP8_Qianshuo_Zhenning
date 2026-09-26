"""Re-run from a clean output directory and compare all recorded CSV cells."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
subprocess.run([sys.executable, '-m', 'unittest', '-v', 'test_simulation.py'], cwd=ROOT, check=True)
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([sys.executable, str(ROOT/'simulation.py'), '--out', tmp], check=True,
                   stdout=subprocess.DEVNULL)
    with zipfile.ZipFile(ROOT/'reference_outputs.zip') as archive:
        manifest = json.loads(archive.read('results/fresh_run.json'))
        assert hashlib.sha256((ROOT/'simulation.py').read_bytes()).hexdigest() == manifest['simulation_sha256']
        cells = 0
        for name in manifest['outputs_sha256']:
            reference = archive.read('results/'+name)
            assert hashlib.sha256(reference).hexdigest() == manifest['outputs_sha256'][name]
            expected = list(csv.reader(io.StringIO(reference.decode())))
            actual = list(csv.reader((Path(tmp)/name).open()))
            assert len(expected) == len(actual), name
            for a,b in zip(expected, actual):
                assert len(a) == len(b), name
                for x,y in zip(a,b):
                    cells += 1
                    if x != y:
                        assert math.isclose(float(x), float(y), rel_tol=1e-10, abs_tol=1e-10), (name,x,y)
        print(f'PASS: six tests; source fingerprint; five reference CSV fingerprints; {cells} CSV cells reproduced.')
