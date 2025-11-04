#!/usr/bin/env python3
"""
Helper script to update the Cognito configuration secret after Cognito stack deployment.

This script retrieves the Cognito User Pool ID, ARN, and Client ID from CloudFormation
stack outputs and updates the Cognito configuration secret.
"""
import json
import sys
import boto3
from botocore.exceptions import ClientError


def get_stack_output(cloudformation_client, stack_name, output_key):
    """Get a specific output value from CloudFormation stack outputs."""
    try:
        response = cloudformation_client.describe_stacks(StackName=stack_name)
        outputs = response["Stacks"][0]["Outputs"]
        for output in outputs:
            if output["OutputKey"] == output_key:
                return output["OutputValue"]
        print(f"Error: {output_key} output not found in stack {stack_name}")
        sys.exit(1)
    except ClientError as e:
        print(f"Error retrieving stack outputs: {e}")
        sys.exit(1)


def update_cognito_config_secret(
    secrets_client, secret_id, user_pool_id, user_pool_arn, client_id, region
):
    """Update Cognito configuration secret with actual values."""
    secret_value = {
        "user_pool_id": user_pool_id,
        "user_pool_arn": user_pool_arn,
        "client_id": client_id,
        "region": region,
    }

    try:
        secrets_client.put_secret_value(
            SecretId=secret_id,
            SecretString=json.dumps(secret_value, indent=2),
        )
        print(f"✅ Successfully updated Cognito configuration secret: {secret_id}")
        return secret_value
    except ClientError as e:
        print(f"Error updating secret {secret_id}: {e}")
        sys.exit(1)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update Cognito configuration secret after Cognito stack deployment"
    )
    parser.add_argument(
        "--stack-name",
        default="SpendSense-Cognito-dev",
        help="CloudFormation stack name (default: SpendSense-Cognito-dev)",
    )
    parser.add_argument(
        "--config-secret-id",
        default="spendsense/cognito/configuration",
        help="Configuration secret ID (default: spendsense/cognito/configuration)",
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region (default: us-east-1)",
    )

    args = parser.parse_args()

    # Initialize AWS clients
    session = boto3.Session()
    secrets_client = session.client("secretsmanager", region_name=args.region)
    cloudformation_client = session.client("cloudformation", region_name=args.region)

    print(f"📋 Retrieving Cognito configuration from stack: {args.stack_name}")

    user_pool_id = get_stack_output(
        cloudformation_client, args.stack_name, "UserPoolId"
    )
    print(f"✅ User Pool ID: {user_pool_id}")

    user_pool_arn = get_stack_output(
        cloudformation_client, args.stack_name, "UserPoolArn"
    )
    print(f"✅ User Pool ARN: {user_pool_arn}")

    client_id = get_stack_output(
        cloudformation_client, args.stack_name, "UserPoolClientId"
    )
    print(f"✅ Client ID: {client_id}")

    print(f"📋 Updating Cognito configuration secret: {args.config_secret_id}")
    config = update_cognito_config_secret(
        secrets_client,
        args.config_secret_id,
        user_pool_id,
        user_pool_arn,
        client_id,
        args.region,
    )

    print("\n✅ Cognito configuration secret updated successfully!")
    print("\nConfiguration values:")
    print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()

