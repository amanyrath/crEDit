#!/usr/bin/env python3
"""
Test script to verify database connection.

This script retrieves the connection string from AWS Secrets Manager
and tests the connection to the RDS PostgreSQL database.
"""
import json
import sys
import boto3
from botocore.exceptions import ClientError

try:
    import psycopg2
except ImportError:
    print("Error: psycopg2 not installed. Install it with: pip install psycopg2-binary")
    sys.exit(1)


def get_connection_string(secrets_client, secret_id):
    """Get connection string from AWS Secrets Manager."""
    try:
        response = secrets_client.get_secret_value(SecretId=secret_id)
        secret_value = json.loads(response["SecretString"])
        return secret_value.get("connection_string")
    except ClientError as e:
        print(f"Error retrieving secret {secret_id}: {e}")
        sys.exit(1)
    except KeyError:
        print(f"Error: connection_string not found in secret {secret_id}")
        print("Make sure you've run update_connection_string.py first")
        sys.exit(1)


def test_connection(connection_string):
    """Test database connection."""
    try:
        print("🔌 Attempting to connect to database...")
        conn = psycopg2.connect(connection_string)
        print("✅ Successfully connected to database!")

        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📊 PostgreSQL version: {version}")

        # Test database name
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"📊 Current database: {db_name}")

        cursor.close()
        conn.close()
        print("✅ Connection test completed successfully!")
        return True
    except psycopg2.Error as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Test database connection")
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

    # Initialize AWS client
    session = boto3.Session()
    secrets_client = session.client("secretsmanager", region_name=args.region)

    print(f"📋 Retrieving connection string from: {args.connection_secret_id}")
    connection_string = get_connection_string(secrets_client, args.connection_secret_id)
    print("✅ Connection string retrieved")

    # Test connection
    success = test_connection(connection_string)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

