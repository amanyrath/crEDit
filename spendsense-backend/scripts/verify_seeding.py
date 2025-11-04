#!/usr/bin/env python3
"""
Quick verification script to check if demo data was seeded successfully.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import get_session
from app.models.profile import Profile
from app.models.account import Account
from app.models.transaction import Transaction

def verify_seeding():
    """Verify demo data was seeded successfully."""
    print("🔍 Checking database for seeded demo data...\n")
    
    try:
        with get_session() as session:
            # Check profiles
            profiles = session.query(Profile).filter(Profile.email.in_([
                'hannah@demo.com',
                'sam@demo.com', 
                'sarah@demo.com'
            ])).all()
            
            print(f"📊 Profiles: {len(profiles)}/3 demo users found")
            for profile in profiles:
                print(f"   ✅ {profile.email} ({profile.user_id})")
            
            if len(profiles) == 0:
                print("   ❌ No demo profiles found")
                return False
            
            # Check accounts
            total_accounts = session.query(Account).count()
            print(f"\n📊 Accounts: {total_accounts} total")
            for profile in profiles:
                user_accounts = session.query(Account).filter(
                    Account.user_id == profile.user_id
                ).all()
                print(f"   {profile.email}: {len(user_accounts)} accounts")
                for acc in user_accounts:
                    print(f"      - {acc.account_type}: ${acc.balance or 0:.2f}")
            
            # Check transactions
            total_transactions = session.query(Transaction).count()
            print(f"\n📊 Transactions: {total_transactions} total")
            for profile in profiles:
                user_txns = session.query(Transaction).filter(
                    Transaction.user_id == profile.user_id
                ).count()
                print(f"   {profile.email}: {user_txns} transactions")
            
            # Summary
            print(f"\n{'='*60}")
            if len(profiles) == 3 and total_accounts >= 9 and total_transactions > 400:
                print("✅ Seeding appears successful!")
                print(f"   - {len(profiles)}/3 users")
                print(f"   - {total_accounts} accounts (expected: 9)")
                print(f"   - {total_transactions} transactions (expected: ~530)")
                return True
            else:
                print("⚠️  Seeding may be incomplete:")
                print(f"   - Users: {len(profiles)}/3")
                print(f"   - Accounts: {total_accounts}/9")
                print(f"   - Transactions: {total_transactions}/~530")
                return False
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

if __name__ == "__main__":
    success = verify_seeding()
    sys.exit(0 if success else 1)


