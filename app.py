from flask import Flask, render_template, request, send_file
import os
import uuid
from werkzeug.utils import secure_filename
from processing.processor import process_pdf  # Make sure this function is implemented

# Initialize Flask app
app = Flask(__name__)

# Define folders
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/watch_ad")
def watch_ad():
    return render_template("watch_ad.html")

@app.route("/generate", methods=["POST"])
def generate():
    # Get files and form data
    files = request.files.getlist("pdfs")
    output_name = request.form.get("output_name", "").strip()
    scale = int(request.form.get("scale", 100))
    highlight = request.form.get("highlight", "None")
    clean = request.form.get("clean") == "on"

    # Save uploaded files
    upload_paths = []
    for file in files:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)
        upload_paths.append(upload_path)

    # Generate output filename
    if not output_name:
        base_name = os.path.splitext(os.path.basename(upload_paths[0]))[0]
        output_name = f"NEW-{base_name}-{scale}.pdf"
    if not output_name.endswith(".pdf"):
        output_name += ".pdf"

    output_path = os.path.join(OUTPUT_FOLDER, secure_filename(output_name))

    # Run PDF processing
    process_pdf(
        file_paths=upload_paths,
        output_path=output_path,
        scale_percent=scale,
        highlight_color=highlight,
        clean_whitespace=clean
    )

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)