# server.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from executor import *

import re  # For AI command parsing

app = Flask(__name__, static_folder='web')
CORS(app)

# ------------------------------
# AI/Natural Language Command Parser
# ------------------------------
def parse_nl_command(text: str):
    """
    Convert simple natural language commands to actual terminal commands.
    Example:
        "Create folder demo and touch file1.txt inside it"
        -> ["mkdir demo", "touch demo/file1.txt"]
    """
    text = text.lower()
    commands = []

    # Create folder
    folder_match = re.search(r'create (a )?folder called (\S+)', text)
    if folder_match:
        folder_name = folder_match.group(2)
        commands.append(f"mkdir {folder_name}")

    # Touch file(s)
    file_matches = re.findall(r'touch (\S+)', text)
    for f in file_matches:
        commands.append(f"touch {f}")

    # Move command
    move_match = re.search(r'move (\S+) to (\S+)', text)
    if move_match:
        src, dst = move_match.groups()
        commands.append(f"mv {src} {dst}")

    # Copy command
    copy_match = re.search(r'copy (\S+) to (\S+)', text)
    if copy_match:
        src, dst = copy_match.groups()
        commands.append(f"cp {src} {dst}")

    return commands if commands else [text]  # fallback to raw command

# ------------------------------
# API Route
# ------------------------------
@app.route('/api/command', methods=['POST'])
def api_command():
    body = request.json or {}
    raw_cmd = body.get('command','').strip()
    if not raw_cmd:
        return jsonify({'ok': False, 'output': 'No command provided'}), 400

    parsed_cmds = parse_nl_command(raw_cmd)
    output = []

    for cmd in parsed_cmds:
        parts = cmd.split()
        try:
            if parts[0] == 'ls':
                out = list_dir(parts[1] if len(parts) > 1 else ".")
            elif parts[0] == 'pwd':
                out = print_pwd()
            elif parts[0] == 'mkdir':
                out = make_dir(parts[1])
            elif parts[0] == 'rm':
                out = remove_path(parts[1])
            elif parts[0] == 'cat':
                out = read_file(parts[1])
            elif parts[0] == 'touch':
                out = touch_file(parts[1])
            elif parts[0] == 'mv':
                out = move(parts[1], parts[2])
            elif parts[0] == 'cp':
                out = copy(parts[1], parts[2])
            elif parts[0] == 'ps':
                out = list_processes()
            elif parts[0] == 'stats':
                out = system_stats()
            elif parts[0] == 'run':
                out = run_subprocess(" ".join(parts[1:]))
            elif parts[0] == 'cd':
                out = change_dir(parts[1] if len(parts) > 1 else ".")
            else:
                out = f"Unknown command {parts[0]}"
        except Exception as e:
            out = f"Error: {e}"
        output.append(out)

    return jsonify({'ok': True, 'output': "\n".join(output)})

# ------------------------------
# Serve HTML & JS
# ------------------------------
@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/static/app.js')
def serve_js():
    return send_from_directory('web', 'app.js')

# ------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
