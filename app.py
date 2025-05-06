from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import os
import uuid
import threading
from werkzeug.utils import secure_filename
from processing.processor import process_pdf
from flask import after_this_request

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

progress_status = {}
output_files = {}

def _del(path, delay=10):
    """Deletes a file after a delay (in seconds)."""
    try:
        time.sleep(delay)
        if os.path.exists(path):
            os.remove(path)
            print(f"🧹 Deleted file after delay: {path}")
    except Exception as e:
        print(f"⚠️ Error deleting file {path}: {e}")

# 🧹 Utility: delete file after delay
# def delete_later(path, delay=10):
#     def _del():
#         time.sleep(delay)
#         try:
#             os.remove(path)
#             print(f"🧹 Deleted: {path}")
#         except Exception as e:
#             print(f"⚠️ Could not delete file: {e}")
#     threading.Thread(target=_del).start()
#

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    scale = int(request.form.get("scale", 100))
    highlight = request.form.get("highlight", "None")
    clean = request.form.get("clean") == "on"
    files = request.files.getlist("pdfs")

    raw_output_name = request.form.get("output_name", "").strip()
    first_file_name = secure_filename(files[0].filename) if files else "output"
    base_name = os.path.splitext(first_file_name)[0]

    if raw_output_name:
        output_name = secure_filename(raw_output_name)
        if not output_name.lower().endswith(".pdf"):
            output_name += ".pdf"
    else:
        output_name = f"NEW-{base_name}-SIZE{scale}.pdf"

    task_id = str(uuid.uuid4())
    progress_status[task_id] = 0

    upload_paths = []
    for f in files:
        path = os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))
        f.save(path)
        upload_paths.append(path)

    output_path = os.path.join(OUTPUT_FOLDER, output_name)
    output_files[task_id] = output_path

    thread = threading.Thread(
        target=process_pdf,
        args=(upload_paths, output_path, scale, highlight, clean, progress_status, task_id)
    )
    thread.start()

    return f"/processing/{task_id}"


@app.route("/processing/<task_id>")
def processing(task_id):
    return render_template("processing.html", task_id=task_id)


@app.route("/progress/<task_id>")
def progress(task_id):
    return jsonify({"progress": progress_status.get(task_id, 0)})



@app.route("/download/<task_id>")
def download(task_id):
    path = output_files.get(task_id)
    if path and os.path.exists(path):
        @after_this_request
        def remove_file(response):
            try:
                os.remove(path)
                print(f"🧹 Deleted: {path}")
            except Exception as e:
                print(f"⚠️ Failed to delete {path}: {e}")
            return response

        return send_file(path, as_attachment=True)
    return "File not found", 404


@app.route("/how_to_use.html")
def how_to_use():
    return render_template("how_to_use.html")

@app.route("/watch_ad")
def watch_ad():
    return render_template("watch_ad.html")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=True, host="0.0.0.0", port=port)
