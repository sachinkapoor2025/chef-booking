import json
import datetime
from pathlib import Path


class BlogSubmissionHandler:
    def __init__(self):
        # Lambda can only write in /tmp directory
        self.submissions_dir = Path("/tmp/submissions")
        self.submissions_dir.mkdir(exist_ok=True)

    def submit_blog(self, blog_data):
        """
        Handle blog submission and save it as JSON file
        """
        try:
            # Required fields based on your submit-blog.html
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
                if field not in blog_data:
                    return {
                        "success": False,
                        "message": f"Missing required field: {field}"
                    }

                # Skip empty check for boolean field
                if field != "termsAgreement" and not str(blog_data[field]).strip():
                    return {
                        "success": False,
                        "message": f"Field cannot be empty: {field}"
                    }

            # Terms must be accepted
            if blog_data.get("termsAgreement") != True:
                return {
                    "success": False,
                    "message": "Terms agreement must be accepted."
                }

            # Add optional fields if not present
            if "phone" not in blog_data:
                blog_data["phone"] = ""

            if "newsletterSignup" not in blog_data:
                blog_data["newsletterSignup"] = False

            # Generate unique submission ID
            submission_id = f"blog_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Prepare submission object
            submission_data = {
                "submission_id": submission_id,
                "status": "pending_review",
                "submitted_at": datetime.datetime.now().isoformat(),
                "approved_at": None,
                "data": {
                    "fullName": blog_data.get("fullName", "").strip(),
                    "email": blog_data.get("email", "").strip(),
                    "phone": blog_data.get("phone", "").strip(),
                    "profession": blog_data.get("profession", "").strip(),
                    "blogTitle": blog_data.get("blogTitle", "").strip(),
                    "blogCategory": blog_data.get("blogCategory", "").strip(),
                    "blogContent": blog_data.get("blogContent", "").strip(),
                    "blogSummary": blog_data.get("blogSummary", "").strip(),
                    "termsAgreement": blog_data.get("termsAgreement", False),
                    "newsletterSignup": blog_data.get("newsletterSignup", False)
                }
            }

            # Save submission JSON
            submission_file = self.submissions_dir / f"{submission_id}.json"
            with open(submission_file, "w", encoding="utf-8") as f:
                json.dump(submission_data, f, indent=2)

            return {
                "success": True,
                "message": "Blog submission received successfully",
                "submission_id": submission_id
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error submitting blog: {str(e)}"
            }


# ✅ MAIN AWS LAMBDA HANDLER
def lambda_handler(event, context):
    """
    AWS Lambda entry point
    """

    # Handle OPTIONS preflight request (CORS)
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
        # Read request body
        if not event.get("body"):
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": False,
                    "message": "Request body is missing"
                })
            }

        body = json.loads(event["body"])

        # Submit blog
        handler = BlogSubmissionHandler()
        result = handler.submit_blog(body)

        # If success
        if result["success"]:
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST,OPTIONS"
                },
                "body": json.dumps({
                    "success": True,
                    "message": result["message"],
                    "submissionId": result["submission_id"]
                })
            }

        # If validation error
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({
                "success": False,
                "message": result["message"]
            })
        }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({
                "success": False,
                "message": "Invalid JSON in request body"
            })
        }

    except Exception as e:
        print("Lambda Error:", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({
                "success": False,
                "message": f"Internal server error: {str(e)}"
            })
        }
