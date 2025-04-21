from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import os
import uuid
import threading
from werkzeug.utils import secure_filename
from processing.processor import process_pdf

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

progress_status = {}  # Task ID to progress mapping
output_files = {}     # Task ID to output file mapping

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
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

        return render_template("processing.html", task_id=task_id)

    return render_template("index.html")

@app.route("/progress/<task_id>")
def progress(task_id):
    percent = progress_status.get(task_id, 0)
    return jsonify({"progress": percent})

@app.route("/download/<task_id>")
def download(task_id):
    path = output_files.get(task_id)
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5050)
