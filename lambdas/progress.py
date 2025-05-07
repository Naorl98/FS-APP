import json

# נניח שזו מפת המעקב המרכזית — בלמדה אמיתי צריך להעביר זאת למאגר (כמו Redis / DynamoDB)
progress_status = {}


def progress_handler(event, context):
    try:
        task_id = event["pathParameters"]["task_id"]

        progress = progress_status.get(task_id, 0)

        return {
            "statusCode": 200,
            "body": json.dumps({"progress": progress}),
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
