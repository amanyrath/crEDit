"""Lambda handler for Cognito Post-Confirmation trigger"""

import json
import logging
import os
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_cognito_config() -> Dict[str, Any]:
    """Retrieve Cognito configuration from AWS Secrets Manager"""
    try:
        secrets_client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION", "us-east-1"))
        secret_name = os.getenv("COGNITO_SECRET_NAME", "spendsense/cognito/configuration")
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ClientError as e:
        logger.error(f"Error retrieving Cognito secret: {e}")
        raise


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for Cognito Post-Confirmation trigger
    
    This function is automatically triggered by Cognito after a user successfully
    confirms their account (or in this case, after sign-up since email verification
    is disabled). It assigns the user to the "consumers" group.
    
    Args:
        event: Cognito Post-Confirmation event containing user information
        context: Lambda context object
        
    Returns:
        The original event (required for Post-Confirmation triggers)
    """
    logger.info(f"Post-Confirmation trigger invoked. Event: {json.dumps(event)}")
    
    try:
        # Extract user information from Cognito event
        user_pool_id = event["userPoolId"]
        username = event["userName"]
        
        # Get Cognito configuration (for user pool ID if not in event)
        # Note: userPoolId is already in the event, but we'll use it for consistency
        cognito_config = get_cognito_config()
        user_pool_id_from_config = cognito_config.get("user_pool_id")
        
        # Use user pool ID from event (more reliable)
        if user_pool_id != user_pool_id_from_config:
            logger.warning(
                f"User pool ID mismatch: event={user_pool_id}, config={user_pool_id_from_config}. "
                "Using event value."
            )
        
        # Create Cognito client
        cognito_client = boto3.client("cognito-idp", region_name=os.getenv("AWS_REGION", "us-east-1"))
        
        # Add user to "consumers" group
        group_name = "consumers"
        try:
            cognito_client.admin_add_user_to_group(
                UserPoolId=user_pool_id,
                Username=username,
                GroupName=group_name
            )
            logger.info(f"Successfully added user {username} to group: {group_name}")
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "ResourceNotFoundException":
                logger.error(f"Group {group_name} not found in user pool {user_pool_id}")
                # Don't fail the trigger - user is still created, just not in group
            elif error_code == "UserNotFoundException":
                logger.error(f"User {username} not found in user pool {user_pool_id}")
                # Don't fail the trigger - this shouldn't happen in Post-Confirmation
            else:
                logger.error(f"Error adding user to group: {e}")
                # Log but don't fail - user creation should still succeed
                
        # Return the original event (required for Post-Confirmation triggers)
        return event
        
    except Exception as e:
        logger.error(f"Error in Post-Confirmation handler: {e}", exc_info=True)
        # Return the event anyway - don't fail user creation
        # The trigger failing would prevent user from being created
        return event

