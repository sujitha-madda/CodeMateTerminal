from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from executor import *
import re

app = Flask(__name__, static_folder='web')
CORS(app)

# -------------------
# AI/NL Command Parser
# -------------------
def parse_nl_command(text: str):
    text = text.lower()
    commands = []

    # Create folder
    folder_patterns = [
        r'(?:create|make|add) (?:a )?folder(?: called)? (\S+)',
    ]
    for pat in folder_patterns:
        m = re.search(pat, text)
        if m:
            commands.append(f"mkdir {m.group(1)}")

    # Create/touch files
    file_patterns = [
        r'(?:touch|create|make) (\S+)(?: inside (\S+))?'
    ]
    for pat in file_patterns:
        m = re.search(pat, text)
        if m:
            file_path = m.group(2) + '/' + m.group(1) if m.group(2) else m.group(1)
            commands.append(f"touch {file_path}")

    # Delete/remove files or folders
    delete_patterns = [
        r'(?:delete|remove|rm) (\S+)'
    ]
    for pat in delete_patterns:
        m = re.search(pat, text)
        if m:
            commands.append(f"rm {m.group(1)}")

    # Move files
    move_patterns = [
        r'(?:move|transfer) (\S+) to (\S+)'
    ]
    for pat in move_patterns:
        m = re.search(pat, text)
        if m:
            commands.append(f"mv {m.group(1)} {m.group(2)}")

    # Copy files
    copy_patterns = [
        r'(?:copy|duplicate) (\S+) to (\S+)'
    ]
    for pat in copy_patterns:
        m = re.search(pat, text)
        if m:
            commands.append(f"cp {m.group(1)} {m.group(2)}")

    # Navigation
    if 'current path' in text or 'pwd' in text:
        commands.append("pwd")
    if 'list' in text or 'ls' in text:
        commands.append("ls")
    if 'go into' in text or 'cd' in text:
        m = re.search(r'go into (\S+)', text)
        if m:
            commands.append(f"cd {m.group(1)}")
    if 'move up' in text or 'cd ..' in text:
        commands.append("cd ..")

    # System stats/processes
    if 'cpu' in text or 'memory' in text or 'stats' in text:
        commands.append("stats")
    if 'processes' in text or 'running processes' in text or 'ps' in text:
        commands.append("ps")

    # Default fallback
    if not commands:
        commands.append(text)

    return commands


# -------------------
# API route
# -------------------
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
            if parts[0] == 'ls': out = list_dir(parts[1] if len(parts)>1 else ".")
            elif parts[0] == 'pwd': out = print_pwd()
            elif parts[0] == 'mkdir': out = make_dir(parts[1])
            elif parts[0] == 'rm': out = remove_path(parts[1])
            elif parts[0] == 'cat': out = read_file(parts[1])
            elif parts[0] == 'touch': out = touch_file(parts[1])
            elif parts[0] == 'mv': out = move(parts[1], parts[2])
            elif parts[0] == 'cp': out = copy(parts[1], parts[2])
            elif parts[0] == 'ps': out = list_processes()
            elif parts[0] == 'stats': out = system_stats()
            elif parts[0] == 'run': out = run_subprocess(" ".join(parts[1:]))
            elif parts[0] == 'cd': out = change_dir(parts[1] if len(parts)>1 else ".")
            else: out = f"Unknown command {parts[0]}"
        except Exception as e:
            out = f"Error: {e}"
        output.append(out)

    return jsonify({'ok': True, 'output': "\n".join(output)})

# -------------------
# Serve Frontend
# -------------------
@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/static/app.js')
def serve_js():
    return send_from_directory('web', 'app.js')

# -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
