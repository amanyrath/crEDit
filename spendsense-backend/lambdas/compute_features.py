"""Lambda handler for compute-features background job"""

import json
import logging
import os
from datetime import datetime
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


def emit_event(event_type: str, user_id: str = None) -> None:
    """
    Emit custom event to EventBridge
    
    Args:
        event_type: Type of event (e.g., "features.computed")
        user_id: User ID associated with the event (optional)
    """
    try:
        events_client = boto3.client("events", region_name=os.getenv("AWS_REGION", "us-east-1"))
        
        event_detail = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        if user_id:
            event_detail["user_id"] = user_id
        
        response = events_client.put_events(
            Entries=[
                {
                    "Source": "spendsense",
                    "DetailType": "Features Computed",
                    "Detail": json.dumps(event_detail),
                }
            ]
        )
        
        if response.get("FailedEntryCount", 0) > 0:
            logger.error(f"Failed to emit event: {response.get('Entries', [])}")
        else:
            logger.info(f"Successfully emitted event: {event_type} for user: {user_id}")
            
    except Exception as e:
        # Log error but don't fail the Lambda execution
        logger.error(f"Error emitting event to EventBridge: {e}", exc_info=True)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for compute-features background job
    
    This function is triggered by EventBridge and computes features
    for users based on their transaction history.
    
    Args:
        event: EventBridge event containing user_id and other metadata
        context: Lambda context object
        
    Returns:
        Dict with status and results
    """
    logger.info(f"Starting compute-features job. Event: {json.dumps(event)}")
    
    try:
        # Extract user_id from event
        user_id = event.get("user_id") or event.get("detail", {}).get("user_id")
        
        # Load database connection from Secrets Manager
        database_secret_name = os.getenv("DATABASE_SECRET_NAME", "spendsense/database/connection")
        db_secret = get_secret(database_secret_name)
        
        logger.info(f"Processing features for user: {user_id}")
        
        # TODO: Implement feature computation logic
        # This will be implemented in future stories (Story 7.1-7.4)
        # For now, this is a placeholder that logs the event
        
        logger.info(f"Completed compute-features job for user: {user_id}")
        
        # Emit event to EventBridge to trigger assign-persona Lambda
        # Only emit if processing a specific user (not scheduled batch)
        if user_id:
            emit_event("features.computed", user_id)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Features computation completed",
                "user_id": user_id,
            }),
        }
        
    except Exception as e:
        logger.error(f"Error in compute-features handler: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
            }),
        }

