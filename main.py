# main.py
import readline
from executor import *
import shlex

def print_help():
    print("""Commands:
  ls [path]         - list directory
  pwd               - show workspace path
  mkdir <path>      - create directory
  rm <path>         - remove file/dir (irreversible)
  cat <file>        - print file contents
  touch <file>      - create empty file
  mv <src> <dst>    - move
  cp <src> <dst>    - copy
  ps                - show processes (top)
  stats             - CPU / Mem usage
  run <cmd...>      - run a subprocess (use with care)
  help              - show this message
  exit              - quit
""")

def repl():
    print("Welcome to CodeMate Terminal (workspace root only). Type 'help'.")
    while True:
        try:
            line = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        if not line:
            continue
        parts = shlex.split(line)
        cmd = parts[0]
        args = parts[1:]
        try:
            if cmd == "ls":
                print(list_dir(args[0] if args else "."))
            elif cmd == "pwd":
                print(print_pwd())
            elif cmd == "mkdir":
                print(make_dir(args[0]))
            elif cmd == "rm":
                print(remove_path(args[0]))
            elif cmd == "cat":
                print(read_file(args[0]))
            elif cmd == "touch":
                print(touch_file(args[0]))
            elif cmd == "mv":
                print(move(args[0], args[1]))
            elif cmd == "cp":
                print(copy(args[0], args[1]))
            elif cmd == "ps":
                print(list_processes())
            elif cmd == "stats":
                print(system_stats())
            elif cmd == "run":
                print(run_subprocess(" ".join(args)))
            elif cmd == "help":
                print_help()
            elif cmd in ("exit","quit"):
                break
            else:
                print(f"Unknown command '{cmd}' — type 'help'")
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    repl()
