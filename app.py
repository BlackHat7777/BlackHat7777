import os
from flask import Flask, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__, static_folder="static", static_url_path="")

# Use a writable directory path for Render
STORAGE_PATH = os.environ.get("STORAGE_PATH", "/tmp/data/uploads")
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "changeme")  # set in Render env

# Ensure the storage directory exists
os.makedirs(STORAGE_PATH, exist_ok=True)

def require_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "missing bearer token"}), 401
        token = auth.split(" ", 1)[1]
        if token != SECRET_TOKEN:
            return jsonify({"error": "invalid token"}), 403
        return f(*args, **kwargs)
    return wrapper

@app.route("/upload", methods=["POST"])
@require_token
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "no file part"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "empty filename"}), 400
    # sanitize filename
    filename = secure_filename(f.filename)
    path = os.path.join(STORAGE_PATH, filename)
    # naive size check (example): limit to 50 MB
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0)
    if size > 50 * 1024 * 1024:
        return jsonify({"error": "file too large"}), 413
    f.save(path)
    return jsonify({"status": "ok", "filename": filename}), 201

@app.route("/files", methods=["GET"])
@require_token
def list_files():
    files = sorted(os.listdir(STORAGE_PATH))
    return jsonify({"files": files})

@app.route("/files/<path:filename>", methods=["GET"])
@require_token
def get_file(filename):
    filename = secure_filename(filename)
    full = os.path.join(STORAGE_PATH, filename)
    if not os.path.exists(full):
        return abort(404)
    return send_from_directory(STORAGE_PATH, filename, as_attachment=False)

# serve the static UI at root
@app.route("/")
def index():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
