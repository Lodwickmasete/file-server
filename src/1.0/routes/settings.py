from flask import Blueprint, render_template, request, jsonify
import json

bp = Blueprint('settings', __name__)
CONFIG_FILE = "config/config.json"

@bp.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        try:
            data = request.get_json()
            with open(CONFIG_FILE, "w") as config_file:
                json.dump(data, config_file, indent=4)
            return jsonify({"message": "Settings updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    try:
        with open(CONFIG_FILE, "r") as config_file:
            settings = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}

    return render_template("settings.html", settings=settings)