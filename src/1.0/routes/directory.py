from flask import Blueprint, render_template, send_from_directory, url_for, request
import os
import time

bp = Blueprint('directory', __name__)

FILE_ROOT = "files"
FILE_ICONS = {
    'py': 'exclamation.svg',
    'html': 'html.png',
    # Add other extensions here
}




# Helper function to calculate size
def get_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)  # File size in bytes
    elif os.path.isdir(path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size  # Total folder size in bytes
    return 0

# Helper function to format size
def format_size(size_in_bytes):
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024**2:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024**3:
        return f"{size_in_bytes / 1024**2:.2f} MB"
    else:
        return f"{size_in_bytes / 1024**3:.2f} GB"


@bp.route("/")
def index():
    return serve_directory("")

@bp.route("/files/", defaults={"subpath": ""})
@bp.route("/files/<path:subpath>")
def serve_directory(subpath):
    full_path = os.path.join(FILE_ROOT, subpath)
    current_time = int(time.time())
    parts = subpath.split("/") if subpath else []
    breadcrumbs = [{"name": "Home", "path": url_for('directory.serve_directory', subpath="")}]

    for i, part in enumerate(parts):
        path = url_for('directory.serve_directory', subpath='/'.join(parts[:i + 1]))
        breadcrumbs.append({"name": part, "path": path})

    if os.path.isdir(full_path):
        try:
            items = os.listdir(full_path)
        except OSError:
            return render_template("404.html"), 404

        files = []
        for item in items:
            item_path = os.path.join(full_path, item)
            ext = item.split('.')[-1].lower() if '.' in item else ''
            icon = FILE_ICONS.get(ext, 'file.png')
            file_path = url_for('directory.serve_directory', subpath=os.path.join(subpath, item)) + f"?t={current_time}"
            
            size_in_bytes = get_size(item_path)
            formatted_size = format_size(size_in_bytes)


            files.append({
                "name": item,
                "is_dir": os.path.isdir(item_path),
                "path": file_path,
                "icon": icon,
                "size": formatted_size
            })

        if not files:
            return render_template("empty.html", breadcrumbs=breadcrumbs)

        return render_template("index.html", files=files, breadcrumbs=breadcrumbs)
    elif os.path.isfile(full_path):
        try:
            return send_from_directory(FILE_ROOT, subpath)
        except OSError:
            return render_template("404.html"), 404
    else:
        return render_template("404.html"), 404