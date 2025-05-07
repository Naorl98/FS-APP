import os
import base64
import mimetypes

def download_handler(event, context):
    try:
        task_id = event["pathParameters"]["task_id"]
        filename = f"output/{task_id}.pdf"

        if not os.path.exists(filename):
            return {
                "statusCode": 404,
                "body": "File not found",
                "headers": {"Content-Type": "text/plain"}
            }

        with open(filename, "rb") as f:
            file_data = f.read()
            encoded = base64.b64encode(file_data).decode('utf-8')

        return {
            "statusCode": 200,
            "body": encoded,
            "isBase64Encoded": True,
            "headers": {
                "Content-Type": mimetypes.guess_type(filename)[0] or "application/pdf",
                "Content-Disposition": f"attachment; filename=formula_sheet.pdf"
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}",
            "headers": {"Content-Type": "text/plain"}
        }
