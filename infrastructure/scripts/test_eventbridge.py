#!/usr/bin/env python3
"""
Test script for EventBridge rules and Lambda function triggers

This script publishes test events to EventBridge and verifies that
Lambda functions are triggered correctly.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError


def print_header(text: str) -> None:
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_success(text: str) -> None:
    """Print success message"""
    print(f"✅ {text}")


def print_error(text: str) -> None:
    """Print error message"""
    print(f"❌ {text}")


def print_info(text: str) -> None:
    """Print info message"""
    print(f"ℹ️  {text}")


def get_region() -> str:
    """Get AWS region from environment or default"""
    return os.getenv("AWS_REGION", "us-east-1")


def publish_event(
    events_client,
    source: str,
    detail_type: str,
    event_detail: Dict[str, Any],
) -> bool:
    """
    Publish a custom event to EventBridge
    
    Args:
        events_client: boto3 EventBridge client
        source: Event source (e.g., "spendsense")
        detail_type: Detail type (e.g., "User Signup")
        event_detail: Event detail dictionary
        
    Returns:
        True if event was published successfully, False otherwise
    """
    try:
        response = events_client.put_events(
            Entries=[
                {
                    "Source": source,
                    "DetailType": detail_type,
                    "Detail": json.dumps(event_detail),
                }
            ]
        )
        
        if response.get("FailedEntryCount", 0) > 0:
            print_error(f"Failed to publish event: {response.get('Entries', [])}")
            return False
        
        entry_id = response.get("Entries", [{}])[0].get("EventId")
        print_success(f"Event published successfully (EventId: {entry_id})")
        return True
        
    except ClientError as e:
        print_error(f"Error publishing event: {e}")
        return False


def test_user_signup_event(events_client) -> None:
    """Test user signup event trigger"""
    print_header("Test 1: User Signup Event")
    
    event_detail = {
        "event_type": "user.signup",
        "user_id": f"test-user-{int(time.time())}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    
    print_info("Publishing user signup event...")
    print_info(f"Event detail: {json.dumps(event_detail, indent=2)}")
    
    success = publish_event(
        events_client,
        source="spendsense",
        detail_type="User Signup",
        event_detail=event_detail,
    )
    
    if success:
        print_info("This should trigger: compute-features Lambda")
        print_info("Wait 10-30 seconds, then check CloudWatch Logs:")
        print_info("  aws logs tail /aws/lambda/compute-features --follow")
    else:
        print_error("Failed to publish user signup event")


def test_features_computed_event(events_client) -> None:
    """Test features computed event trigger"""
    print_header("Test 2: Features Computed Event")
    
    event_detail = {
        "event_type": "features.computed",
        "user_id": f"test-user-{int(time.time())}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    
    print_info("Publishing features computed event...")
    print_info(f"Event detail: {json.dumps(event_detail, indent=2)}")
    
    success = publish_event(
        events_client,
        source="spendsense",
        detail_type="Features Computed",
        event_detail=event_detail,
    )
    
    if success:
        print_info("This should trigger: assign-persona Lambda")
        print_info("Wait 10-30 seconds, then check CloudWatch Logs:")
        print_info("  aws logs tail /aws/lambda/assign-persona --follow")
    else:
        print_error("Failed to publish features computed event")


def test_persona_assigned_event(events_client) -> None:
    """Test persona assigned event trigger"""
    print_header("Test 3: Persona Assigned Event")
    
    event_detail = {
        "event_type": "persona.assigned",
        "user_id": f"test-user-{int(time.time())}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    
    print_info("Publishing persona assigned event...")
    print_info(f"Event detail: {json.dumps(event_detail, indent=2)}")
    
    success = publish_event(
        events_client,
        source="spendsense",
        detail_type="Persona Assigned",
        event_detail=event_detail,
    )
    
    if success:
        print_info("This should trigger: generate-recommendations Lambda")
        print_info("Wait 10-30 seconds, then check CloudWatch Logs:")
        print_info("  aws logs tail /aws/lambda/generate-recommendations --follow")
    else:
        print_error("Failed to publish persona assigned event")


def test_event_chain(events_client) -> None:
    """Test the complete event chain (user signup → features → persona → recommendations)"""
    print_header("Test 4: Complete Event Chain")
    
    user_id = f"test-user-{int(time.time())}"
    
    print_info(f"Testing complete event chain for user: {user_id}")
    print_info("This will publish events in sequence with delays...")
    
    # Step 1: User signup
    print_info("\nStep 1: Publishing user signup event...")
    event_detail = {
        "event_type": "user.signup",
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    publish_event(
        events_client,
        source="spendsense",
        detail_type="User Signup",
        event_detail=event_detail,
    )
    
    print_info("Waiting 15 seconds for compute-features Lambda to complete...")
    time.sleep(15)
    
    # Step 2: Features computed (simulating what compute-features Lambda would emit)
    print_info("\nStep 2: Publishing features computed event...")
    event_detail = {
        "event_type": "features.computed",
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    publish_event(
        events_client,
        source="spendsense",
        detail_type="Features Computed",
        event_detail=event_detail,
    )
    
    print_info("Waiting 15 seconds for assign-persona Lambda to complete...")
    time.sleep(15)
    
    # Step 3: Persona assigned (simulating what assign-persona Lambda would emit)
    print_info("\nStep 3: Publishing persona assigned event...")
    event_detail = {
        "event_type": "persona.assigned",
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    publish_event(
        events_client,
        source="spendsense",
        detail_type="Persona Assigned",
        event_detail=event_detail,
    )
    
    print_info("\n✅ Event chain test completed!")
    print_info("Check CloudWatch Logs for all three Lambda functions:")
    print_info("  aws logs tail /aws/lambda/compute-features --follow")
    print_info("  aws logs tail /aws/lambda/assign-persona --follow")
    print_info("  aws logs tail /aws/lambda/generate-recommendations --follow")


def main() -> None:
    """Main function"""
    print_header("EventBridge Rules Test Script")
    
    region = get_region()
    print_info(f"Using AWS region: {region}")
    
    # Initialize EventBridge client
    try:
        events_client = boto3.client("events", region_name=region)
        print_success("EventBridge client initialized")
    except Exception as e:
        print_error(f"Failed to initialize EventBridge client: {e}")
        sys.exit(1)
    
    # Check if running interactively
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        if test_name == "signup":
            test_user_signup_event(events_client)
        elif test_name == "features":
            test_features_computed_event(events_client)
        elif test_name == "persona":
            test_persona_assigned_event(events_client)
        elif test_name == "chain":
            test_event_chain(events_client)
        else:
            print_error(f"Unknown test: {test_name}")
            print_info("Available tests: signup, features, persona, chain")
            sys.exit(1)
    else:
        # Run all tests
        print_info("Running all tests...")
        print_info("To run a specific test, use: python3 test_eventbridge.py <test_name>")
        print_info("Available tests: signup, features, persona, chain\n")
        
        test_user_signup_event(events_client)
        time.sleep(5)
        
        test_features_computed_event(events_client)
        time.sleep(5)
        
        test_persona_assigned_event(events_client)
        time.sleep(5)
        
        print_header("Test Summary")
        print_success("All individual tests completed!")
        print_info("To test the complete event chain, run:")
        print_info("  python3 test_eventbridge.py chain")
    
    print_header("Testing Complete")
    print_info("Remember to check CloudWatch Logs to verify Lambda execution")


if __name__ == "__main__":
    main()

