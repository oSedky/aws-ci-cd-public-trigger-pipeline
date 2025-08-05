import boto3
import json
import os
import time
from datetime import datetime, timedelta

# Environment variables or placeholders for sensitive info
# This is a best practice to avoid hardcoding values
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME")
PIPELINE_NAME = os.environ.get("PIPELINE_NAME")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def lambda_handler(event, context):
    codepipeline = boto3.client("codepipeline")
    sns = boto3.client("sns")

    # Extract source IP from API Gateway
    ip_address = event["requestContext"]["identity"].get("sourceIp", "unknown")

    # Time range: past 7 days
    now = int(time.time())
    one_week_ago = now - (7 * 24 * 60 * 60)

    # Query items for this IP within the last 7 days
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("PK").eq(ip_address)
        )
        # Filter items for recent requests, as DynamoDB's query doesn't use the TTL
        recent_requests = [
            item for item in response["Items"]
            if int(item["timestamp"]) >= one_week_ago
        ]
    except Exception as e:
        print(f"[ERROR] DynamoDB query failed: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "DynamoDB query failed", "details": str(e)})
        }

    # Check if rate limit is exceeded
    if len(recent_requests) >= 3:
        print(f"[WARN] IP {ip_address} exceeded request limit. "
              f"{len(recent_requests)} requests in past 7 days.")
        return {
            "statusCode": 429,
            "body": json.dumps({
                "message": f"Rate limit exceeded. Max 3 requests per IP per week. ({ip_address})"
            })
        }

    # Record this request with a TTL of 7 days from now
    try:
        table.put_item(Item={
            "PK": ip_address,
            "SK": str(now),
            "timestamp": now,
            "ttl": now + (7 * 24 * 60 * 60)
        })
    except Exception as e:
        print(f"[ERROR] Failed to insert request record: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to insert request record", "details": str(e)})
        }

    # Start pipeline execution
    try:
        response = codepipeline.start_pipeline_execution(name=PIPELINE_NAME)
        execution_id = response["pipelineExecutionId"]

        # Notify via SNS
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="🚀 Pipeline Triggered via Public Endpoint",
            Message=f"Pipeline {PIPELINE_NAME} triggered by {ip_address}.\nExecution ID: {execution_id}"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Pipeline execution started",
                "executionId": execution_id
            })
        }

    except Exception as e:
        # Publish failure alert
        print(f"[ERROR] Failed to start pipeline: {str(e)}")
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="❌ Pipeline Trigger Failed",
            Message=f"Error triggering pipeline from {ip_address}: {str(e)}"
        )

        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }