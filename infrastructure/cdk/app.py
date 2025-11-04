#!/usr/bin/env python3
"""
AWS CDK App for SpendSense Infrastructure
"""
import os
import aws_cdk as cdk
from stacks.database_stack import DatabaseStack

app = cdk.App()

# Get environment from context or default to dev
env_name = app.node.try_get_context("environment") or "dev"
region = app.node.try_get_context("region") or os.getenv("AWS_REGION", "us-east-1")

# AWS Account and Region
env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=region
)

# Database Stack - RDS PostgreSQL
database_stack = DatabaseStack(
    app,
    f"SpendSense-Database-{env_name}",
    env=env,
    description="RDS PostgreSQL database and Secrets Manager configuration for SpendSense"
)

app.synth()

