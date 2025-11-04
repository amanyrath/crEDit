#!/usr/bin/env python3
"""
AWS CDK App for SpendSense Infrastructure
"""
import os
import aws_cdk as cdk
from stacks.database_stack import DatabaseStack
from stacks.cognito_stack import CognitoStack
from stacks.lambda_stack import LambdaStack
from stacks.s3_stack import S3Stack

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

# Cognito Stack - User Pool and Groups
cognito_stack = CognitoStack(
    app,
    f"SpendSense-Cognito-{env_name}",
    env=env,
    description="Cognito User Pool, groups, and Secrets Manager configuration for SpendSense"
)

# Lambda Stack - Lambda Functions and API Gateway
lambda_stack = LambdaStack(
    app,
    f"SpendSense-Lambda-{env_name}",
    env=env,
    description="Lambda functions and API Gateway for SpendSense"
)

# S3 Stack - S3 Buckets and CloudFront Distribution
s3_stack = S3Stack(
    app,
    f"SpendSense-S3-{env_name}",
    env=env,
    description="S3 buckets and CloudFront distribution for SpendSense frontend hosting"
)

app.synth()

