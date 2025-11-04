#!/usr/bin/env python3
"""
Get a valid Bearer token from Cognito for testing

This script authenticates with Cognito using a demo user and returns
a JWT token that can be used for testing API endpoints.

Usage:
    python scripts/get_auth_token.py [email]
    
    Example:
        python scripts/get_auth_token.py hannah@demo.com
        python scripts/get_auth_token.py  # Uses hannah@demo.com by default

Environment Variables Required:
    - COGNITO_USER_POOL_ID: AWS Cognito User Pool ID
    - COGNITO_CLIENT_ID: AWS Cognito Client ID
    - AWS_REGION: AWS region (default: us-east-1)
    - DEMO_PASSWORD: Optional demo password (defaults to "Demo123!")
"""

import os
import sys
import json
import boto3
from botocore.exceptions import ClientError

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings


def get_cognito_config():
    """Get Cognito configuration from environment or Secrets Manager"""
    user_pool_id = settings.cognito_user_pool_id
    client_id = settings.cognito_client_id
    region = settings.aws_region
    
    if not user_pool_id or not client_id:
        # Try to get from Secrets Manager
        try:
            secrets_client = boto3.client('secretsmanager', region_name=region)
            secret_name = "spendsense/cognito/configuration"
            response = secrets_client.get_secret_value(SecretId=secret_name)
            config = json.loads(response['SecretString'])
            user_pool_id = config.get('user_pool_id') or user_pool_id
            client_id = config.get('client_id') or client_id
        except Exception as e:
            print(f"Warning: Could not fetch from Secrets Manager: {e}")
    
    if not user_pool_id:
        raise ValueError("COGNITO_USER_POOL_ID not configured")
    if not client_id:
        raise ValueError("COGNITO_CLIENT_ID not configured")
    
    return user_pool_id, client_id, region


def authenticate_user(email: str, password: str):
    """Authenticate user with Cognito and return JWT tokens"""
    user_pool_id, client_id, region = get_cognito_config()
    
    cognito_client = boto3.client('cognito-idp', region_name=region)
    
    try:
        # Authenticate using USER_PASSWORD_AUTH flow
        response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password,
            }
        )
        
        authentication_result = response['AuthenticationResult']
        
        return {
            'access_token': authentication_result['AccessToken'],
            'id_token': authentication_result['IdToken'],
            'refresh_token': authentication_result['RefreshToken'],
            'token_type': authentication_result.get('TokenType', 'Bearer'),
            'expires_in': authentication_result['ExpiresIn'],
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'NotAuthorizedException':
            raise ValueError(f"Authentication failed: Wrong password or user not found")
        elif error_code == 'UserNotFoundException':
            raise ValueError(f"User not found: {email}")
        elif error_code == 'UserNotConfirmedException':
            raise ValueError(f"User not confirmed: {email}")
        else:
            raise ValueError(f"Authentication error: {error_message}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {str(e)}")


def main():
    """Main function"""
    # Default demo users
    demo_users = {
        'hannah@demo.com': 'Hannah Martinez',
        'sam@demo.com': 'Sam Patel',
        'sarah@demo.com': 'Sarah Chen',
    }
    
    # Get email from command line or use default
    email = sys.argv[1] if len(sys.argv) > 1 else 'hannah@demo.com'
    
    if email not in demo_users:
        print(f"Warning: {email} is not in the list of known demo users")
        print(f"Known demo users: {', '.join(demo_users.keys())}")
    
    # Get password from environment or use default
    password = os.getenv('DEMO_PASSWORD', 'Demo123!')
    
    print(f"Authenticating as {email}...")
    print(f"User Pool ID: {settings.cognito_user_pool_id}")
    print(f"Client ID: {settings.cognito_client_id}")
    print()
    
    try:
        tokens = authenticate_user(email, password)
        
        print("=" * 60)
        print("✅ Authentication Successful!")
        print("=" * 60)
        print()
        print("Bearer Token (ID Token):")
        print("-" * 60)
        print(tokens['id_token'])
        print()
        print("=" * 60)
        print("Usage:")
        print("=" * 60)
        print()
        print("1. Copy the token above")
        print("2. Use it in Swagger UI:")
        print("   - Go to http://localhost:8000/docs")
        print("   - Click 'Authorize' button")
        print("   - Paste token (without 'Bearer ' prefix)")
        print("   - Click 'Authorize'")
        print()
        print("3. Or use with curl:")
        print(f"   curl -X GET 'http://localhost:8000/api/v1/users/me/recommendations' \\")
        print(f"     -H 'Authorization: Bearer {tokens['id_token'][:50]}...'")
        print()
        print("=" * 60)
        print("Token Info:")
        print("=" * 60)
        print(f"Token Type: {tokens['token_type']}")
        print(f"Expires In: {tokens['expires_in']} seconds ({tokens['expires_in'] // 3600} hours)")
        print()
        
        # Save token to file for easy access
        token_file = '.test_token.txt'
        with open(token_file, 'w') as f:
            f.write(tokens['id_token'])
        print(f"✅ Token saved to {token_file} for easy access")
        print(f"   You can use: export TEST_TOKEN=$(cat {token_file})")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

