from flask import Blueprint, render_template, request, jsonify
import subprocess

bp = Blueprint('userTerminal', __name__)

@bp.route("/user/terminal", methods=["GET", "POST"])
def terminal():
    if request.method == "POST":
        # Execute terminal command
        command = request.get_json().get("command", "")
        if not command:
            return jsonify({"error": "No command provided"}), 400
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout if result.returncode == 0 else result.stderr
            return jsonify({"output": output}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Render the terminal interface
    return render_template("/user-terminal/index.html")