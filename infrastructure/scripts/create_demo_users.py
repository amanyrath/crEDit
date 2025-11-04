#!/usr/bin/env python3
"""
Script to create pre-seeded demo accounts in Cognito User Pool.

This script creates demo users and adds them to appropriate groups:
- hannah@demo.com / Demo123! (Consumer)
- sam@demo.com / Demo123! (Consumer)
- operator@demo.com / Demo123! (Operator)

Note: Uses password "Demo123!" which meets Cognito password policy requirements.
"""
import json
import sys
import boto3
from botocore.exceptions import ClientError


def get_cognito_config(secrets_client, secret_id):
    """Get Cognito configuration from Secrets Manager."""
    try:
        response = secrets_client.get_secret_value(SecretId=secret_id)
        return json.loads(response["SecretString"])
    except ClientError as e:
        print(f"Error retrieving secret {secret_id}: {e}")
        sys.exit(1)


def create_demo_user(
    cognito_client, user_pool_id, email, password, group_name, role
):
    """Create a demo user and add to group."""
    try:
        # Create user with permanent password
        cognito_client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
                {"Name": "custom:role", "Value": role},
            ],
            TemporaryPassword=password,
            MessageAction="SUPPRESS",  # Suppress welcome email
            DesiredDeliveryMediums=["EMAIL"],  # Required but suppressed
        )
        print(f"✅ Created user: {email}")

        # Set permanent password (since we can't set it directly in admin_create_user)
        # We'll use admin_set_user_password to set permanent password
        cognito_client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=email,
            Password=password,
            Permanent=True,
        )
        print(f"✅ Set permanent password for: {email}")

        # Add user to group
        cognito_client.admin_add_user_to_group(
            UserPoolId=user_pool_id, Username=email, GroupName=group_name
        )
        print(f"✅ Added {email} to group: {group_name}")

        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "UsernameExistsException":
            print(f"⚠️  User {email} already exists, skipping...")
            # Try to add to group anyway in case user exists but isn't in group
            try:
                cognito_client.admin_add_user_to_group(
                    UserPoolId=user_pool_id, Username=email, GroupName=group_name
                )
                print(f"✅ Added existing user {email} to group: {group_name}")
            except ClientError as group_error:
                print(f"⚠️  Could not add {email} to group: {group_error}")
            return True
        else:
            print(f"❌ Error creating user {email}: {e}")
            return False


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create demo users in Cognito User Pool"
    )
    parser.add_argument(
        "--config-secret-id",
        default="spendsense/cognito/configuration",
        help="Cognito configuration secret ID (default: spendsense/cognito/configuration)",
    )
    parser.add_argument(
        "--user-pool-id",
        help="User Pool ID (overrides secret value if provided)",
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
    cognito_client = session.client("cognito-idp", region_name=args.region)

    # Get Cognito configuration
    if args.user_pool_id:
        user_pool_id = args.user_pool_id
        print(f"📋 Using provided User Pool ID: {user_pool_id}")
    else:
        print(f"📋 Retrieving Cognito configuration from: {args.config_secret_id}")
        config = get_cognito_config(secrets_client, args.config_secret_id)
        user_pool_id = config["user_pool_id"]
        print(f"✅ User Pool ID: {user_pool_id}")

    # Demo users configuration
    # Using password "Demo123!" which meets Cognito password policy:
    # - Minimum 8 characters
    # - At least one uppercase letter
    # - At least one lowercase letter
    # - At least one number
    # - At least one special character
    demo_password = "Demo123!"

    demo_users = [
        {
            "email": "hannah@demo.com",
            "password": demo_password,
            "group": "consumers",
            "role": "consumer",
        },
        {
            "email": "sam@demo.com",
            "password": demo_password,
            "group": "consumers",
            "role": "consumer",
        },
        {
            "email": "operator@demo.com",
            "password": demo_password,
            "group": "operators",
            "role": "operator",
        },
    ]

    print("\n📋 Creating demo users...")
    print("=" * 60)

    success_count = 0
    for user in demo_users:
        print(f"\nCreating user: {user['email']}")
        if create_demo_user(
            cognito_client,
            user_pool_id,
            user["email"],
            user["password"],
            user["group"],
            user["role"],
        ):
            success_count += 1

    print("\n" + "=" * 60)
    print(f"\n✅ Demo users creation complete: {success_count}/{len(demo_users)} users")

    print("\n📋 Demo Account Credentials:")
    print("=" * 60)
    for user in demo_users:
        print(f"Email: {user['email']}")
        print(f"Password: {user['password']}")
        print(f"Role: {user['role']} (Group: {user['group']})")
        print("-" * 60)

    print("\n✅ All demo users are ready to use!")


if __name__ == "__main__":
    main()

