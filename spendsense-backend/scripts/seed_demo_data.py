#!/usr/bin/env python3
"""
Database seeding script for demo data.

This script creates demo users in Cognito and seeds the database with:
- 3 demo user profiles
- Accounts for each user (checking, savings, credit cards)
- Transaction history (~200 for Hannah, ~180 for Sam, ~150 for Sarah)
- Realistic transaction patterns matching PRD specifications

Usage:
    python scripts/seed_demo_data.py

Environment Variables Required:
    - COGNITO_USER_POOL_ID: AWS Cognito User Pool ID
    - DATABASE_URL: Database connection string (or Secrets Manager configured)
    - AWS_REGION: AWS region (default: us-east-1)
    - DEMO_PASSWORD: Optional demo password (defaults to "Demo123!")

Security Notes:
    - ⚠️ FOR DEVELOPMENT/TESTING ONLY - Never use in production
    - All secrets retrieved from environment variables or AWS Secrets Manager
    - No hardcoded credentials or connection strings
    - Demo passwords are clearly marked as test data
    - Uses Faker library - no real PII in generated data

The script is idempotent - it can be run multiple times safely.

See scripts/README_SEEDING.md for detailed documentation.
"""

import json
import logging
import os
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import boto3
from botocore.exceptions import ClientError
from faker import Faker

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import get_session
from app.models.account import Account
from app.models.profile import Profile
from app.models.transaction import Transaction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()
Faker.seed(42)  # Seed for reproducible results

# Demo users configuration
DEMO_USERS = [
    {
        "email": "hannah@demo.com",
        "name": "Hannah Martinez",
        "role": "consumer",
        "persona": "high_utilization",
        "accounts": [
            {"type": "checking", "balance": Decimal("850.00"), "limit": None},
            {"type": "savings", "balance": Decimal("1200.00"), "limit": None},
            {"type": "credit_card", "balance": Decimal("3400.00"), "limit": Decimal("5000.00")},
        ],
        "transaction_count": 200,
        "subscriptions": ["Netflix", "Spotify", "Planet Fitness", "Adobe"],
        "has_interest_charges": True,
        "interest_amount": Decimal("87.00"),
    },
    {
        "email": "sam@demo.com",
        "name": "Sam Patel",
        "role": "consumer",
        "persona": "subscription_heavy",
        "accounts": [
            {"type": "checking", "balance": Decimal("2400.00"), "limit": None},
            {"type": "savings", "balance": Decimal("5000.00"), "limit": None},
            {"type": "credit_card", "balance": Decimal("800.00"), "limit": Decimal("8000.00")},
        ],
        "transaction_count": 180,
        "subscriptions": ["Netflix", "Hulu", "Disney+", "Spotify", "Apple iCloud", "NYT", "Peloton", "HelloFresh"],
        "has_interest_charges": False,
        "interest_amount": None,
    },
    {
        "email": "sarah@demo.com",
        "name": "Sarah Chen",
        "role": "consumer",
        "persona": "savings_builder",
        "accounts": [
            {"type": "checking", "balance": Decimal("3200.00"), "limit": None},
            {"type": "high_yield_savings", "balance": Decimal("8500.00"), "limit": None},
            {"type": "credit_card", "balance": Decimal("400.00"), "limit": Decimal("3000.00")},
        ],
        "transaction_count": 150,
        "subscriptions": [],
        "has_interest_charges": False,
        "interest_amount": None,
        "savings_transfer_amount": Decimal("500.00"),
    },
]

# Transaction categories
CATEGORIES = {
    "Food & Drink": {"min": 5.00, "max": 75.00, "weight": 0.25},
    "Shopping": {"min": 15.00, "max": 200.00, "weight": 0.20},
    "Bills": {"min": 30.00, "max": 150.00, "weight": 0.25},
    "Subscriptions": {"min": 10.00, "max": 30.00, "weight": 0.15},
    "Transportation": {"min": 10.00, "max": 50.00, "weight": 0.10},
    "Entertainment": {"min": 8.00, "max": 100.00, "weight": 0.05},
}

# Subscription amounts (monthly)
SUBSCRIPTION_AMOUNTS = {
    "Netflix": Decimal("15.99"),
    "Spotify": Decimal("10.99"),
    "Hulu": Decimal("12.99"),
    "Disney+": Decimal("10.99"),
    "Apple iCloud": Decimal("9.99"),
    "NYT": Decimal("17.00"),
    "Peloton": Decimal("39.00"),
    "HelloFresh": Decimal("69.99"),
    "Planet Fitness": Decimal("10.00"),
    "Adobe": Decimal("52.99"),
}


def get_cognito_config(secrets_client, secret_id: str) -> Dict:
    """Get Cognito configuration from Secrets Manager."""
    try:
        response = secrets_client.get_secret_value(SecretId=secret_id)
        return json.loads(response["SecretString"])
    except ClientError as e:
        logger.error(f"Error retrieving secret {secret_id}: {e}")
        raise


def get_cognito_user_pool_id() -> str:
    """Get Cognito User Pool ID from environment or Secrets Manager."""
    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    if user_pool_id:
        return user_pool_id
    
    # Try to get from Secrets Manager
    secret_id = os.getenv("COGNITO_CONFIG_SECRET_ID", "spendsense/cognito/configuration")
    region = os.getenv("AWS_REGION", "us-east-1")
    secrets_client = boto3.client("secretsmanager", region_name=region)
    
    try:
        config = get_cognito_config(secrets_client, secret_id)
        user_pool_id = config.get("user_pool_id")
        if not user_pool_id:
            logger.error(f"user_pool_id not found in config. Available keys: {list(config.keys())}")
            raise ValueError("user_pool_id not found in Cognito configuration secret")
        # Validate format: Cognito User Pool IDs have format: region_XXXXXXXX
        if "_" not in user_pool_id:
            logger.error(f"Invalid User Pool ID format: {user_pool_id}. Expected format: region_XXXXXXXX")
            raise ValueError(f"Invalid User Pool ID format: {user_pool_id}")
        return user_pool_id
    except Exception as e:
        logger.error(f"Could not retrieve Cognito User Pool ID: {e}")
        raise ValueError(
            "COGNITO_USER_POOL_ID environment variable required or "
            "Cognito configuration secret must be accessible"
        )


def create_cognito_user(cognito_client, user_pool_id: str, email: str, name: str, role: str) -> Optional[str]:
    """Create user in Cognito if not exists. Returns user_id (sub)."""
    try:
        # Check if user exists
        try:
            response = cognito_client.admin_get_user(
                UserPoolId=user_pool_id,
                Username=email
            )
            logger.info(f"User {email} already exists in Cognito")
            # Extract user_id from attributes
            for attr in response.get("UserAttributes", []):
                if attr["Name"] == "sub":
                    return attr["Value"]
            return None
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") != "UserNotFoundException":
                raise
        
        # Create user
        # SECURITY: Demo password for test users only - never use in production
        # Password can be overridden via DEMO_PASSWORD environment variable
        # Default password "Demo123!" meets Cognito password policy requirements
        demo_password = os.getenv("DEMO_PASSWORD", "Demo123!")
        
        response = cognito_client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
                {"Name": "custom:role", "Value": role},
                {"Name": "name", "Value": name},
            ],
            TemporaryPassword=demo_password,
            MessageAction="SUPPRESS",
            DesiredDeliveryMediums=["EMAIL"],
        )
        
        # Set permanent password
        cognito_client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=email,
            Password=demo_password,
            Permanent=True,
        )
        
        # Extract user_id (sub)
        user_id = None
        for attr in response["User"].get("Attributes", []):
            if attr["Name"] == "sub":
                user_id = UUID(attr["Value"])
                break
        
        logger.info(f"Created Cognito user: {email} (user_id: {user_id})")
        return str(user_id) if user_id else None
        
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "UsernameExistsException":
            logger.info(f"User {email} already exists, retrieving user_id")
            # Get existing user
            response = cognito_client.admin_get_user(
                UserPoolId=user_pool_id,
                Username=email
            )
            for attr in response.get("UserAttributes", []):
                if attr["Name"] == "sub":
                    return attr["Value"]
            return None
        else:
            logger.error(f"Error creating Cognito user {email}: {e}")
            raise


def create_or_get_profile(session, user_id: UUID, email: str, role: str) -> Profile:
    """Create or get profile record in database."""
    profile = session.query(Profile).filter(Profile.user_id == user_id).first()
    
    if profile:
        logger.info(f"Profile already exists for {email}")
        return profile
    
    profile = Profile(
        user_id=user_id,
        email=email,
        role=role,
    )
    session.add(profile)
    session.flush()
    logger.info(f"Created profile for {email}")
    return profile


def create_accounts(session, profile: Profile, accounts_config: List[Dict]) -> List[Account]:
    """Create accounts for a user. Returns list of created/existing accounts."""
    created_accounts = []
    
    for acc_config in accounts_config:
        # Check if account type already exists
        existing = session.query(Account).filter(
            Account.user_id == profile.user_id,
            Account.account_type == acc_config["type"]
        ).first()
        
        if existing:
            logger.info(f"Account {acc_config['type']} already exists for {profile.email}")
            created_accounts.append(existing)
            continue
        
        # Generate last 4 digits
        account_number_last4 = fake.numerify("####")
        
        account = Account(
            user_id=profile.user_id,
            account_type=acc_config["type"],
            account_number_last4=account_number_last4,
            balance=acc_config["balance"],
            limit=acc_config.get("limit"),
        )
        session.add(account)
        created_accounts.append(account)
        logger.info(f"Created {acc_config['type']} account for {profile.email}")
    
    session.flush()
    return created_accounts


def generate_transaction_date(start_date: date, days_ago: int) -> date:
    """Generate a transaction date within the last 90 days."""
    return start_date - timedelta(days=days_ago)


def generate_transaction_amount(category: str) -> Decimal:
    """Generate realistic transaction amount for category."""
    cat_info = CATEGORIES.get(category, {"min": 10.00, "max": 100.00, "weight": 0.1})
    amount = fake.pyfloat(min_value=float(cat_info["min"]), max_value=float(cat_info["max"]), right_digits=2)
    return Decimal(str(round(amount, 2)))


def select_category_with_weights() -> str:
    """Select category based on weights."""
    import random
    categories = list(CATEGORIES.keys())
    weights = [CATEGORIES[cat]["weight"] for cat in categories]
    return random.choices(categories, weights=weights)[0]


def generate_transactions(
    session,
    profile: Profile,
    accounts: List[Account],
    user_config: Dict,
    start_date: date = None
) -> int:
    """Generate transactions for a user. Returns count of created transactions."""
    if start_date is None:
        start_date = date.today()
    
    # Check if transactions already exist
    existing_count = session.query(Transaction).filter(
        Transaction.user_id == profile.user_id
    ).count()
    
    expected_count = user_config["transaction_count"]
    
    if existing_count >= expected_count:
        logger.info(f"Transactions already exist for {profile.email} ({existing_count} transactions, expected {expected_count})")
        return existing_count
    
    if existing_count > 0:
        logger.info(f"Partial transactions found for {profile.email} ({existing_count}/{expected_count}). Will complete missing transactions.")
        # Note: For simplicity, we'll regenerate all transactions
        # In a production scenario, you might want to delete and recreate or append only missing ones
        session.query(Transaction).filter(Transaction.user_id == profile.user_id).delete()
        session.flush()
        logger.info(f"Cleared existing transactions to regenerate complete set")
    
    checking_account = next((acc for acc in accounts if acc.account_type == "checking"), None)
    savings_account = next((acc for acc in accounts if acc.account_type in ["savings", "high_yield_savings"]), None)
    credit_account = next((acc for acc in accounts if acc.account_type == "credit_card"), None)
    
    transactions = []
    transaction_count = user_config["transaction_count"]
    
    # Generate subscription transactions (monthly recurring)
    subscriptions = user_config.get("subscriptions", [])
    subscription_dates = []
    if subscriptions:
        # Generate subscription dates for last 3 months
        for month_offset in range(3):
            for subscription in subscriptions:
                sub_date = start_date - timedelta(days=month_offset * 30)
                subscription_dates.append((sub_date, subscription))
    
    # Generate interest charges for Hannah (monthly)
    interest_dates = []
    if user_config.get("has_interest_charges") and credit_account:
        for month_offset in range(3):
            interest_date = start_date - timedelta(days=month_offset * 30 + 1)
            interest_dates.append(interest_date)
    
    # Generate savings transfers for Sarah (monthly)
    savings_transfer_dates = []
    if user_config.get("savings_transfer_amount") and checking_account and savings_account:
        for month_offset in range(3):
            transfer_date = start_date - timedelta(days=month_offset * 30 + 5)
            savings_transfer_dates.append(transfer_date)
    
    # Generate other transactions
    used_dates = set()
    
    # Add subscription transactions
    for sub_date, subscription_name in subscription_dates:
        if subscription_name in SUBSCRIPTION_AMOUNTS:
            amount = -SUBSCRIPTION_AMOUNTS[subscription_name]
            transactions.append({
                "user_id": profile.user_id,
                "account_id": credit_account.id if credit_account else checking_account.id,
                "date": sub_date,
                "merchant": subscription_name,
                "amount": amount,
                "category": "Subscriptions",
            })
            used_dates.add(sub_date)
    
    # Add interest charges
    for interest_date in interest_dates:
        transactions.append({
            "user_id": profile.user_id,
            "account_id": credit_account.id,
            "date": interest_date,
            "merchant": "Credit Card Interest",
            "amount": -user_config["interest_amount"],
            "category": "Bills",
        })
        used_dates.add(interest_date)
    
    # Add savings transfers
    for transfer_date in savings_transfer_dates:
        transactions.append({
            "user_id": profile.user_id,
            "account_id": checking_account.id,
            "date": transfer_date,
            "merchant": "Automatic Savings Transfer",
            "amount": -user_config["savings_transfer_amount"],
            "category": "Bills",
        })
        # Also add as credit to savings
        transactions.append({
            "user_id": profile.user_id,
            "account_id": savings_account.id,
            "date": transfer_date,
            "merchant": "Automatic Savings Transfer",
            "amount": user_config["savings_transfer_amount"],
            "category": "Bills",
        })
        used_dates.add(transfer_date)
    
    # Generate remaining transactions
    remaining_count = transaction_count - len(transactions)
    
    logger.info(f"Generating {remaining_count} transactions for {profile.email}...")
    
    # Generate dates - allow multiple transactions per day (realistic)
    # Spread transactions over 90 days, but allow duplicates
    date_list = []
    for _ in range(remaining_count):
        days_ago = fake.random_int(min=0, max=90)
        tx_date = generate_transaction_date(start_date, days_ago)
        date_list.append(tx_date)
    
    # Sort dates for realistic chronological order (most recent first)
    date_list = sorted(date_list, reverse=True)
    
    logger.info(f"Generated {remaining_count} transaction dates (allowing multiple per day)...")
    
    for i, tx_date in enumerate(date_list):
        if i % 50 == 0 and i > 0:
            logger.info(f"  Progress: {i}/{remaining_count} transactions generated...")
        
        # Select category
        category = select_category_with_weights()
        
        # Select account based on category and user persona
        if category == "Subscriptions" and credit_account:
            account = credit_account
        elif category in ["Bills", "Shopping"] and credit_account and fake.boolean(chance_of_getting_true=60):
            account = credit_account
        elif checking_account:
            account = checking_account
        else:
            account = accounts[0]
        
        # Generate amount
        amount = generate_transaction_amount(category)
        # Make it negative (debit)
        amount = -abs(amount)
        
        # Generate merchant name using faker
        merchant = fake.company()
        
        transactions.append({
            "user_id": profile.user_id,
            "account_id": account.id,
            "date": tx_date,
            "merchant": merchant,
            "amount": amount,
            "category": category,
        })
    
    # Batch insert transactions
    logger.info(f"Inserting {len(transactions)} transactions into database...")
    transaction_objects = [
        Transaction(**tx) for tx in transactions
    ]
    session.bulk_save_objects(transaction_objects)
    session.flush()
    
    logger.info(f"✅ Created {len(transactions)} transactions for {profile.email}")
    return len(transactions)


def seed_demo_data():
    """Main function to seed demo data."""
    logger.info("Starting database seeding script")
    
    # Get Cognito User Pool ID
    try:
        user_pool_id = get_cognito_user_pool_id()
        logger.info(f"Using Cognito User Pool ID: {user_pool_id}")
    except Exception as e:
        logger.error(f"Failed to get Cognito User Pool ID: {e}")
        sys.exit(1)
    
    # Initialize Cognito client
    region = os.getenv("AWS_REGION", "us-east-1")
    cognito_client = boto3.client("cognito-idp", region_name=region)
    
    # Process each demo user
    with get_session() as session:
        for user_config in DEMO_USERS:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing user: {user_config['email']}")
            logger.info(f"{'='*60}")
            
            try:
                # Step 1: Create Cognito user
                user_id_str = create_cognito_user(
                    cognito_client,
                    user_pool_id,
                    user_config["email"],
                    user_config["name"],
                    user_config["role"]
                )
                
                if not user_id_str:
                    logger.error(f"Could not get user_id for {user_config['email']}")
                    continue
                
                user_id = UUID(user_id_str)
                
                # Step 2: Create or get profile
                profile = create_or_get_profile(
                    session,
                    user_id,
                    user_config["email"],
                    user_config["role"]
                )
                
                # Step 3: Create accounts
                accounts = create_accounts(session, profile, user_config["accounts"])
                
                # Step 4: Generate transactions
                transaction_count = generate_transactions(
                    session,
                    profile,
                    accounts,
                    user_config
                )
                
                logger.info(f"✅ Completed seeding for {user_config['email']}")
                logger.info(f"   - Profile: {profile.email}")
                logger.info(f"   - Accounts: {len(accounts)}")
                logger.info(f"   - Transactions: {transaction_count}")
                
            except Exception as e:
                logger.error(f"Error processing user {user_config['email']}: {e}")
                session.rollback()
                raise
        
        # Commit all changes
        session.commit()
        logger.info("\n✅ Database seeding completed successfully!")


if __name__ == "__main__":
    try:
        seed_demo_data()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Seeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Seeding failed: {e}")
        sys.exit(1)

