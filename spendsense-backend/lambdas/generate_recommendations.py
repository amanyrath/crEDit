"""Lambda handler for generate-recommendations background job"""

import json
import logging
import os
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_secret(secret_name: str) -> Dict[str, Any]:
    """Retrieve secret from AWS Secrets Manager"""
    try:
        secrets_client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION", "us-east-1"))
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ClientError as e:
        logger.error(f"Error retrieving secret {secret_name}: {e}")
        raise


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for generate-recommendations background job
    
    This function is triggered by EventBridge and generates recommendations
    for users based on their persona and features.
    
    Args:
        event: EventBridge event containing user_id and other metadata
        context: Lambda context object
        
    Returns:
        Dict with status and results
    """
    logger.info(f"Starting generate-recommendations job. Event: {json.dumps(event)}")
    
    try:
        # Extract user_id from event
        user_id = event.get("user_id") or event.get("detail", {}).get("user_id")
        
        # Load database connection from Secrets Manager
        database_secret_name = os.getenv("DATABASE_SECRET_NAME", "spendsense/database/connection")
        db_secret = get_secret(database_secret_name)
        
        logger.info(f"Processing recommendations for user: {user_id}")
        
        # TODO: Implement recommendation generation logic
        # This will be implemented in future stories (Story 8.4-8.7)
        # For now, this is a placeholder that logs the event
        
        logger.info(f"Completed generate-recommendations job for user: {user_id}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Recommendations generation completed",
                "user_id": user_id,
            }),
        }
        
    except Exception as e:
        logger.error(f"Error in generate-recommendations handler: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
            }),
        }

