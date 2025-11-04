#!/usr/bin/env python3
"""
Helper script to update the database connection string secret after RDS deployment.

This script retrieves the database endpoint and credentials from AWS Secrets Manager
and updates the connection string secret with the complete connection string.
Includes SSL support for RDS connections.
"""
import json
import sys
import urllib.parse
import boto3
from botocore.exceptions import ClientError


def get_secret_value(secrets_client, secret_id):
    """Get secret value from AWS Secrets Manager."""
    try:
        response = secrets_client.get_secret_value(SecretId=secret_id)
        return json.loads(response["SecretString"])
    except ClientError as e:
        print(f"Error retrieving secret {secret_id}: {e}")
        sys.exit(1)


def update_connection_string_secret(
    secrets_client, connection_secret_id, endpoint, credentials
):
    """Update connection string secret with actual database details."""
    username = credentials["username"]
    password = credentials["password"]
    
    # URL-encode the password to handle special characters
    encoded_password = urllib.parse.quote(password, safe='')
    
    # Include SSL mode for RDS connections
    connection_string = (
        f"postgresql://{username}:{encoded_password}@{endpoint}:5432/spendsense?sslmode=require"
    )

    secret_value = {
        "host": endpoint,
        "port": "5432",
        "database": "spendsense",
        "username": username,
        "password": password,
        "connection_string": connection_string,
    }

    try:
        secrets_client.put_secret_value(
            SecretId=connection_secret_id,
            SecretString=json.dumps(secret_value, indent=2),
        )
        print(f"✅ Successfully updated connection string secret: {connection_secret_id}")
        print(f"Connection string: {connection_string}")
        return connection_string
    except ClientError as e:
        print(f"Error updating secret {connection_secret_id}: {e}")
        sys.exit(1)


def get_database_endpoint(cloudformation_client, stack_name):
    """Get database endpoint from CloudFormation stack outputs."""
    try:
        response = cloudformation_client.describe_stacks(StackName=stack_name)
        outputs = response["Stacks"][0]["Outputs"]
        for output in outputs:
            if output["OutputKey"] == "DatabaseEndpoint":
                return output["OutputValue"]
        print(f"Error: DatabaseEndpoint output not found in stack {stack_name}")
        sys.exit(1)
    except ClientError as e:
        print(f"Error retrieving stack outputs: {e}")
        sys.exit(1)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update database connection string secret after RDS deployment"
    )
    parser.add_argument(
        "--stack-name",
        default="SpendSense-Database-dev",
        help="CloudFormation stack name (default: SpendSense-Database-dev)",
    )
    parser.add_argument(
        "--credentials-secret-id",
        default="spendsense/database/credentials",
        help="Credentials secret ID (default: spendsense/database/credentials)",
    )
    parser.add_argument(
        "--connection-secret-id",
        default="spendsense/database/connection",
        help="Connection string secret ID (default: spendsense/database/connection)",
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

    print(f"📋 Retrieving database endpoint from stack: {args.stack_name}")
    endpoint = get_database_endpoint(cloudformation_client, args.stack_name)
    print(f"✅ Database endpoint: {endpoint}")

    print(f"📋 Retrieving database credentials from: {args.credentials_secret_id}")
    credentials = get_secret_value(secrets_client, args.credentials_secret_id)
    print(f"✅ Credentials retrieved")

    print(f"📋 Updating connection string secret: {args.connection_secret_id}")
    connection_string = update_connection_string_secret(
        secrets_client, args.connection_secret_id, endpoint, credentials
    )

    print("\n✅ Connection string secret updated successfully!")
    print("\nYou can now use this connection string to connect to the database.")
    print("\nTo test the connection:")
    print(f"  psql '{connection_string}'")


if __name__ == "__main__":
    main()

