from flask import Flask, render_template, send_from_directory, url_for
import os
import time

app = Flask(__name__)

# Root directory of the file system
FILE_ROOT = "files"

@app.route("/")
def index():
    return serve_directory("")  # Serve files from the root directory


@app.route("/files/", defaults={"subpath": ""})
@app.route("/files/<path:subpath>")
def serve_directory(subpath):
    full_path = os.path.join(FILE_ROOT, subpath)
    current_time = int(time.time()) #Get timestamp

    # Breadcrumbs
    parts = subpath.split("/") if subpath else []
    breadcrumbs = [{"name": "Home", "path": url_for('serve_directory', subpath="")}] # Use url_for for correct paths
    for i, part in enumerate(parts):
        path = url_for('serve_directory', subpath='/'.join(parts[:i + 1]))
        breadcrumbs.append({"name": part, "path": path})

    if os.path.isdir(full_path):
        # List directory contents
        try:
            items = os.listdir(full_path)
        except OSError:  #Handle permission errors
            return render_template("404.html"), 404

        files = []
        for item in items:
            item_path = os.path.join(full_path, item)
            
            #Add timestamp to the URL
            file_path = url_for('serve_directory', subpath=os.path.join(subpath, item)) + f"?t={current_time}"

            files.append({
                "name": item,
                "is_dir": os.path.isdir(item_path),
                "path": file_path
            })

        # Render empty.html if the directory is empty
        if not files:
            return render_template("empty.html", breadcrumbs=breadcrumbs)

        return render_template("index.html", files=files, breadcrumbs=breadcrumbs)
    elif os.path.isfile(full_path):
        # Serve the file
        try:
            return send_from_directory(FILE_ROOT, subpath)  # Simpler and safer if FILE_ROOT is properly secured.
        except OSError:
            return render_template("404.html"), 404
    else:
        return render_template("404.html"), 404


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
