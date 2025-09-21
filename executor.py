import os
import shlex
import shutil
import subprocess
from pathlib import Path
import psutil

WORKSPACE = Path(__file__).parent / "workspace"
WORKSPACE.mkdir(exist_ok=True)

# Track current working directory inside workspace
CWD = WORKSPACE.resolve()

class UnsafePathError(Exception):
    pass

def resolve_safe(path: str) -> Path:
    global CWD
    p = Path(path)
    if not p.is_absolute():
        p = CWD / p
    p = p.resolve()
    if WORKSPACE.resolve() not in p.parents and p != WORKSPACE.resolve():
        raise UnsafePathError(f"Path {p} is outside the workspace.")
    return p

def change_dir(path: str):
    global CWD
    p = Path(path)
    if not p.is_absolute():
        p = CWD / p
    p = p.resolve()
    # If path is outside workspace, clamp to workspace root
    if WORKSPACE.resolve() not in p.parents and p != WORKSPACE.resolve():
        p = WORKSPACE.resolve()
    if not p.is_dir():
        return f"{path} is not a directory"
    CWD = p
    return f"Current directory: {CWD.relative_to(WORKSPACE)}"


def list_dir(path="."):
    p = resolve_safe(path)
    if p.is_dir():
        return "\n".join(sorted([f.name + ("/" if f.is_dir() else "") for f in p.iterdir()]))
    return f"{p} is not a directory"

def print_pwd():
    global CWD
    return str(CWD.relative_to(WORKSPACE))

def make_dir(path):
    p = resolve_safe(path)
    p.mkdir(parents=True, exist_ok=True)
    return f"Created {p.relative_to(WORKSPACE)}"

def remove_path(path):
    p = resolve_safe(path)
    if p == WORKSPACE.resolve():
        return "Refusing to remove workspace root"
    if p.is_dir():
        shutil.rmtree(p)
        return f"Removed directory {p.relative_to(WORKSPACE)}"
    elif p.exists():
        p.unlink()
        return f"Removed file {p.relative_to(WORKSPACE)}"
    else:
        return "No such file or directory"

def read_file(path):
    p = resolve_safe(path)
    if not p.exists() or p.is_dir():
        return "File not found or is a directory"
    return p.read_text()

def touch_file(path):
    p = resolve_safe(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch(exist_ok=True)
    return f"Touched {p.relative_to(WORKSPACE)}"

def move(src, dst):
    s = resolve_safe(src)
    d = resolve_safe(dst)
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(s), str(d))
    return f"Moved {s.relative_to(WORKSPACE)} -> {d.relative_to(WORKSPACE)}"

def copy(src, dst):
    s = resolve_safe(src)
    d = resolve_safe(dst)
    d.parent.mkdir(parents=True, exist_ok=True)
    if s.is_dir():
        shutil.copytree(s, d)
    else:
        shutil.copy2(s, d)
    return f"Copied {s.relative_to(WORKSPACE)} -> {d.relative_to(WORKSPACE)}"

def run_subprocess(command: str):
    args = shlex.split(command)
    try:
        res = subprocess.run(args, capture_output=True, text=True, timeout=15, cwd=CWD)
        out = res.stdout.strip()
        err = res.stderr.strip()
        return (out if out else "") + ("\n" + err if err else "")
    except Exception as e:
        return f"Error running command: {e}"

def list_processes(limit=20):
    procs = []
    for p in psutil.process_iter(['pid','name','username','cpu_percent','memory_percent']):
        procs.append(p.info)
    procs = sorted(procs, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:limit]
    lines = []
    for p in procs:
        lines.append(f"{p['pid']:6} {p['name'][:25]:25} CPU:{p['cpu_percent']:5} MEM:{p['memory_percent']:5.1f}")
    return "\n".join(lines)

def system_stats():
    return f"CPU: {psutil.cpu_percent(interval=0.5)}% | Mem: {psutil.virtual_memory().percent}%"
