import os
import uuid
import json
import base64
from werkzeug.utils import secure_filename
from processing.processor import process_pdf

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

def generate_handler(event, context):
    try:
        body = event.get("body")
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body)

        # Get multipart form-data using AWS Lambda parser (simulate Werkzeug or use multipart decoder)
        # This is a simplified logic assuming JSON input instead of multipart for now
        # Real Lambda requires `multipart/form-data` parsing via library like `requests_toolbelt`

        data = json.loads(body)
        scale = int(data.get("scale", 100))
        highlight = data.get("highlight", "None")
        clean = data.get("clean", False)
        file_name = data.get("output_name", "").strip()
        pdf_base64 = data["pdf_base64"]  # Expect base64 string of the file
        original_filename = data.get("filename", "uploaded.pdf")

        task_id = str(uuid.uuid4())
        filename = secure_filename(original_filename)
        upload_path = os.path.join(UPLOAD_FOLDER, filename)

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        with open(upload_path, "wb") as f:
            f.write(base64.b64decode(pdf_base64))

        base_name = os.path.splitext(filename)[0]
        output_name = secure_filename(file_name) if file_name else f"NEW-{base_name}-SIZE{scale}.pdf"
        if not output_name.lower().endswith(".pdf"):
            output_name += ".pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_name)

        progress_status = {task_id: 0}

        # Directly call (non-threaded version for lambda)
        process_pdf([upload_path], output_path, scale, highlight, clean, progress_status, task_id)

        # Return link to /download/<task_id>
        return {
            "statusCode": 200,
            "body": json.dumps({
                "redirect_url": f"/processing/{task_id}"
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
