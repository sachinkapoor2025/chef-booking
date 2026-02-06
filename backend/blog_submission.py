import json
import boto3
import os
from datetime import datetime
import uuid

dynamodb = boto3.resource("dynamodb")

SUBMISSIONS_TABLE = os.environ["SUBMISSIONS_TABLE"]


def lambda_handler(event, context):

    # CORS Preflight
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({"message": "CORS preflight success"})
        }

    try:
        body = json.loads(event.get("body", "{}"))

        required_fields = [
            "fullName",
            "email",
            "profession",
            "blogTitle",
            "blogCategory",
            "blogContent",
            "blogSummary",
            "termsAgreement"
        ]

        for field in required_fields:
            if field not in body or str(body[field]).strip() == "":
                return {
                    "statusCode": 400,
                    "headers": {
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({
                        "success": False,
                        "message": f"Missing required field: {field}"
                    })
                }

        if body.get("termsAgreement") != True:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": False,
                    "message": "Terms agreement must be accepted."
                })
            }

        submission_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        submission_data = {
            "id": submission_id,
            "formType": "blog-submission",

            "fullName": body.get("fullName", "").strip(),
            "email": body.get("email", "").strip(),
            "phone": body.get("phone", "").strip(),
            "profession": body.get("profession", "").strip(),

            "blogTitle": body.get("blogTitle", "").strip(),
            "blogCategory": body.get("blogCategory", "").strip(),
            "blogContent": body.get("blogContent", "").strip(),
            "blogSummary": body.get("blogSummary", "").strip(),

            "termsAgreement": body.get("termsAgreement", False),
            "newsletterSignup": body.get("newsletterSignup", False),

            "status": "pending",
            "submittedAt": timestamp,

            "approvedAt": None,
            "rejectedAt": None,
            "approvedBy": None,
            "rejectedBy": None,
            "rejectionReason": None
        }

        table = dynamodb.Table(SUBMISSIONS_TABLE)
        table.put_item(Item=submission_data)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({
                "success": True,
                "message": "Blog submission received successfully",
                "submissionId": submission_id
            })
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": False,
                "message": "Internal server error"
            })
        }
