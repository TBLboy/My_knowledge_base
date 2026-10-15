"""Reproducible unchanged-source compiler verification; does not edit the paper."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / 'Transformer-Koopman' / '\u8bba\u6587' / '\u65b0\u7248\u672c'
COMPILER = Path(r'C:\Users\12187\AppData\Local\Temp\opencode\tectonic\tectonic.exe')
OUT = PAPER / 'build_current'
DOCS = ROOT / '.project-log' / 'docs'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


OUT.mkdir(exist_ok=True)
source_before = digest(PAPER / 'Main.tex')
version = subprocess.check_output([str(COMPILER), '--version']).decode().strip()
command = [str(COMPILER), '--only-cached', '--keep-logs', '--keep-intermediates',
           '--reruns', '2', '--outdir', str(OUT), 'Main.tex']
runs = []
for number in (1, 2):
    process = subprocess.run(command, cwd=PAPER, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    console = DOCS / f'task051-compile-pass{number}.txt'
    console.write_bytes(process.stdout)
    log = OUT / 'Main.log'
    if log.exists():
        (DOCS / f'task051-final-pass{number}.log').write_bytes(log.read_bytes())
    runs.append({'run': number, 'returncode': process.returncode,
                 'console': str(console.relative_to(ROOT))})
    if process.returncode:
        break
text = (OUT / 'Main.log').read_text(encoding='utf-8', errors='replace') if (OUT / 'Main.log').exists() else ''
patterns = {
    'undefined_reference_or_citation': r'[^\n]*(?:(?:Reference|Citation)[^\n]*(?:undefined|multiply defined)|There were undefined (?:references|citations)|Label[^\n]*multiply defined)[^\n]*',
    'rerun': r'[^\n]*(?:Rerun to get|Label\(s\) may have changed|Please rerun)[^\n]*',
    'overfull': r'[^\n]*Overfull[^\n]*',
    'underfull': r'[^\n]*Underfull[^\n]*',
    'font_warning': r'[^\n]*(?:Font Warning|font shapes|font shape)[^\n]*',
    'latex_error': r'(?m)^![^\n]*',
}
report = {'compiler': version, 'compiler_path': str(COMPILER), 'cwd': str(PAPER),
          'command': command, 'runs': runs, 'source_before_sha256': source_before,
          'source_after_sha256': digest(PAPER / 'Main.tex'),
          'source_unchanged': source_before == digest(PAPER / 'Main.tex'),
          'final_log_findings': {k: re.findall(v, text, re.I) for k, v in patterns.items()},
          'limitations': ['Compilation does not establish submission readiness or visual layout quality.',
                          'Experiments, figures, theoretical claims and source semantics were not modified.']}
files = [PAPER / 'Main.tex', PAPER / 'IEEEtran.cls', COMPILER, Path(__file__),
         OUT / 'Main.pdf', OUT / 'Main.log']
files += list(DOCS.glob('task051-compile-pass*.txt'))
files += list(DOCS.glob('task051-final-pass*.log'))
binding = {'file_hashes': {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): digest(p)
                          for p in files if p.exists()}}
(DOCS / 'task051-compile-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
binding['file_hashes']['.project-log/docs/task051-compile-report.json'] = digest(DOCS / 'task051-compile-report.json')
(DOCS / 'task051-binding.json').write_text(json.dumps(binding, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=True, indent=2))
