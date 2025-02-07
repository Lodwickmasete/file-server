from flask import Blueprint, jsonify, request
import os
import shutil
from urllib.parse import unquote

bp = Blueprint('api', __name__)
FILE_ROOT = "files"


@bp.route("/api/create-folder", methods=["GET"])
def create_folder():
    folder_path = request.args.get("path")
    if not folder_path:
        return jsonify({"error": "Missing 'path' parameter"}), 400

    # Decode URL-encoded characters in the path
    decoded_path = unquote(folder_path)

    full_path = os.path.normpath(os.path.join(FILE_ROOT, decoded_path))
    if not full_path.startswith(FILE_ROOT):
        return jsonify({"error": "Invalid path"}), 400

    try:
        os.makedirs(full_path, exist_ok=True)
        return jsonify({"message": f"Folder '{decoded_path}' created successfully"}), 201
    except OSError as e:
        return jsonify({"error": f"OS error: {e.strerror}"}), 500

@bp.route("/api/rename", methods=["POST"])
def rename():
    data = request.get_json()
    if not data or "path" not in data or "new_name" not in data:
        return jsonify({"error": "Missing 'path' or 'new_name' parameter"}), 400

    # Decode URL-encoded characters in the path
    decoded_path = unquote(data["path"])
    new_name = unquote(data["new_name"])

    current_path = os.path.normpath(os.path.join(FILE_ROOT, decoded_path))
    if not current_path.startswith(FILE_ROOT):
        return jsonify({"error": "Invalid path"}), 400

    new_path = os.path.join(os.path.dirname(current_path), new_name)

    try:
        os.rename(current_path, new_path)
        return jsonify({"message": f"Renamed to '{new_name}' successfully"}), 200
    except OSError as e:
        return jsonify({"error": f"OS error: {e.strerror}"}), 500
        
@bp.route("/api/upload", methods=["POST"])
def upload_file():
    # Check if the request contains a file
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    # Check if a file was uploaded
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Decode optional destination path
    dest_path = request.form.get("path", "")
    decoded_dest_path = os.path.normpath(os.path.join(FILE_ROOT, unquote(dest_path)))

    # Validate the destination path
    if not decoded_dest_path.startswith(FILE_ROOT):
        return jsonify({"error": "Invalid destination path"}), 400

    # Ensure the destination folder exists
    os.makedirs(decoded_dest_path, exist_ok=True)

    try:
        # Save the file
        file.save(os.path.join(decoded_dest_path, file.filename))
        return jsonify({"message": f"File '{file.filename}' uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to upload file: {str(e)}"}), 500



LOG_FILE = "deleted_files_log.txt"  # Path to the log file


def log_deletion(path, status, message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"Path: {path}, Status: {status}, Message: {message}\n")

@bp.route("/api/delete", methods=["POST"])
def delete():
    data = request.get_json()
    if not data or "paths" not in data:
        return jsonify({"error": "Missing 'paths' parameter"}), 400

    # List to store the results of each deletion
    results = []

    for path in data["paths"]:
        # Decode URL-encoded characters in the path
        decoded_path = unquote(path)

        # Combine and validate path
        full_path = os.path.normpath(os.path.join(FILE_ROOT, decoded_path))
        if not full_path.startswith(FILE_ROOT):
            result = {"path": path, "status": "error", "message": "Invalid path"}
            results.append(result)
            log_deletion(path, "error", "Invalid path")
            continue

        # Prevent deletion of the root directory
        if full_path == os.path.normpath(FILE_ROOT):
            result = {"path": path, "status": "error", "message": "Cannot delete the root directory"}
            results.append(result)
            log_deletion(path, "error", "Cannot delete the root directory")
            continue

        if not os.path.exists(full_path):
            result = {"path": path, "status": "error", "message": "File or folder does not exist"}
            results.append(result)
            log_deletion(path, "error", "File or folder does not exist")
            continue

        try:
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)  # Delete folder and its contents
            else:
                os.remove(full_path)  # Delete file
            result = {"path": path, "status": "success", "message": f"'{decoded_path}' deleted successfully"}
            results.append(result)
            log_deletion(path, "success", f"'{decoded_path}' deleted successfully")
        except OSError as e:
            result = {"path": path, "status": "error", "message": f"OS error: {e.strerror}"}
            results.append(result)
            log_deletion(path, "error", f"OS error: {e.strerror}")
        except Exception as e:
            result = {"path": path, "status": "error", "message": str(e)}
            results.append(result)
            log_deletion(path, "error", str(e))

    # Return results of all deletions
    return jsonify(results), 200