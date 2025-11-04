"""
Lambda Stack - Lambda Functions, API Gateway, and EventBridge Rules
"""
import os
from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_cognito as cognito,
    aws_secretsmanager as secretsmanager,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
    CfnOutput,
    Fn,
)
from constructs import Construct


class LambdaStack(Stack):
    """
    Creates Lambda functions, API Gateway, and EventBridge Rules with:
    - API Lambda function for FastAPI (using Mangum)
    - Background job Lambda functions (compute-features, assign-persona, generate-recommendations)
    - API Gateway REST API with /api/v1/* routes
    - EventBridge rules for triggering background jobs (scheduled and event-based)
    - IAM roles with VPC, Secrets Manager, and CloudWatch Logs permissions
    - CORS configuration for frontend
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get environment from context
        env_name = self.node.try_get_context("environment") or "dev"
        region = self.node.try_get_context("region") or os.getenv("AWS_REGION", "us-east-1")

        # Get VPC - use default VPC for MVP, can be parameterized later
        vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)

        # Import Lambda security group from database stack
        # The database stack exports this as: {stack_name}-LambdaSecurityGroupId
        database_stack_name = f"SpendSense-Database-{env_name}"
        lambda_security_group_id = Fn.import_value(
            f"{database_stack_name}-LambdaSecurityGroupId"
        )
        lambda_security_group = ec2.SecurityGroup.from_security_group_id(
            self,
            "ImportedLambdaSecurityGroup",
            security_group_id=lambda_security_group_id,
        )

        # Import secret ARNs from other stacks
        database_secret_arn = Fn.import_value(
            f"{database_stack_name}-ConnectionStringSecretArn"
        )
        cognito_stack_name = f"SpendSense-Cognito-{env_name}"
        cognito_secret_arn = Fn.import_value(
            f"{cognito_stack_name}-CognitoConfigSecretArn"
        )
        user_pool_id = Fn.import_value(
            f"{cognito_stack_name}-UserPoolId"
        )

        # Create IAM role for API Lambda function
        api_lambda_role = iam.Role(
            self,
            "ApiLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="IAM role for API Lambda function",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaVPCAccessExecutionRole"
                ),
            ],
        )

        # Grant Secrets Manager read permissions
        api_lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["secretsmanager:GetSecretValue"],
                resources=[
                    database_secret_arn,
                    cognito_secret_arn,
                ],
            )
        )

        # Grant CloudWatch Logs permissions (additional to VPC execution role)
        api_lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                resources=["arn:aws:logs:*:*:*"],
            )
        )

        # Create IAM role for background job Lambda functions
        background_job_role = iam.Role(
            self,
            "BackgroundJobLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="IAM role for background job Lambda functions",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaVPCAccessExecutionRole"
                ),
            ],
        )

        # Grant Secrets Manager read permissions
        background_job_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["secretsmanager:GetSecretValue"],
                resources=[
                    database_secret_arn,
                    cognito_secret_arn,
                ],
            )
        )

        # Grant CloudWatch Logs permissions
        background_job_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                resources=["arn:aws:logs:*:*:*"],
            )
        )

        # Grant EventBridge permissions for emitting custom events
        background_job_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["events:PutEvents"],
                resources=["*"],  # EventBridge PutEvents requires * resource
            )
        )

        # Get subnets for Lambda VPC configuration
        # Prefer private subnets (with NAT Gateway for internet access)
        # If only public subnets exist (e.g., default VPC), use them with allowPublicSubnet=True
        # Note: Lambda in public subnets cannot access internet, but can access VPC resources
        if vpc.private_subnets:
            subnets = vpc.private_subnets
            allow_public_subnet = False
        else:
            # Default VPC might only have public subnets
            subnets = vpc.public_subnets
            allow_public_subnet = True

        # Create API Lambda function
        # Use PythonFunction for automatic dependency bundling
        api_lambda = lambda_.Function(
            self,
            "ApiLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="app.handler.handler",
            code=lambda_.Code.from_asset("../../spendsense-backend"),
            timeout=Duration.seconds(30),
            memory_size=512,
            role=api_lambda_role,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=subnets),
            security_groups=[lambda_security_group],
            allow_public_subnet=allow_public_subnet,
            environment={
                "DATABASE_SECRET_ARN": database_secret_arn,
                "DATABASE_SECRET_NAME": "spendsense/database/connection",
                "COGNITO_SECRET_ARN": cognito_secret_arn,
                "COGNITO_SECRET_NAME": "spendsense/cognito/configuration",
                "ENVIRONMENT": env_name,
            },
            description="FastAPI application Lambda function using Mangum adapter",
        )

        # Create background job Lambda functions
        compute_features_lambda = lambda_.Function(
            self,
            "ComputeFeaturesLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambdas.compute_features.handler",
            code=lambda_.Code.from_asset("../../spendsense-backend"),
            timeout=Duration.minutes(5),
            memory_size=1024,
            role=background_job_role,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=subnets),
            security_groups=[lambda_security_group],
            allow_public_subnet=allow_public_subnet,
            environment={
                "DATABASE_SECRET_ARN": database_secret_arn,
                "DATABASE_SECRET_NAME": "spendsense/database/connection",
                "COGNITO_SECRET_ARN": cognito_secret_arn,
                "COGNITO_SECRET_NAME": "spendsense/cognito/configuration",
                "ENVIRONMENT": env_name,
            },
            description="Background job: Compute user features from transactions",
        )

        assign_persona_lambda = lambda_.Function(
            self,
            "AssignPersonaLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambdas.assign_persona.handler",
            code=lambda_.Code.from_asset("../../spendsense-backend"),
            timeout=Duration.minutes(5),
            memory_size=512,
            role=background_job_role,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=subnets),
            security_groups=[lambda_security_group],
            allow_public_subnet=allow_public_subnet,
            environment={
                "DATABASE_SECRET_ARN": database_secret_arn,
                "DATABASE_SECRET_NAME": "spendsense/database/connection",
                "COGNITO_SECRET_ARN": cognito_secret_arn,
                "COGNITO_SECRET_NAME": "spendsense/cognito/configuration",
                "ENVIRONMENT": env_name,
            },
            description="Background job: Assign persona to users based on features",
        )

        generate_recommendations_lambda = lambda_.Function(
            self,
            "GenerateRecommendationsLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambdas.generate_recommendations.handler",
            code=lambda_.Code.from_asset("../../spendsense-backend"),
            timeout=Duration.minutes(5),
            memory_size=512,
            role=background_job_role,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=subnets),
            security_groups=[lambda_security_group],
            allow_public_subnet=allow_public_subnet,
            environment={
                "DATABASE_SECRET_ARN": database_secret_arn,
                "DATABASE_SECRET_NAME": "spendsense/database/connection",
                "COGNITO_SECRET_ARN": cognito_secret_arn,
                "COGNITO_SECRET_NAME": "spendsense/cognito/configuration",
                "ENVIRONMENT": env_name,
            },
            description="Background job: Generate recommendations for users",
        )

        # Create API Gateway REST API
        api = apigateway.RestApi(
            self,
            "ApiGateway",
            rest_api_name=f"spendsense-api-{env_name}",
            description="SpendSense API Gateway",
            deploy_options=apigateway.StageOptions(
                stage_name=env_name,
                throttling_burst_limit=100,
                throttling_rate_limit=100,
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"] if env_name == "dev" else ["https://spendsense.com"],  # Configure for production
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization", "X-Amz-Date", "X-Api-Key"],
                allow_credentials=True,
            ),
        )

        # Import User Pool from Cognito stack using the user pool ID
        # Note: This creates a reference to the User Pool in another stack
        # This will be used when creating the Cognito authorizer
        user_pool_ref = cognito.UserPool.from_user_pool_id(
            self,
            "ImportedUserPool",
            user_pool_id=user_pool_id,
        )
        
        # Cognito authorizer for API Gateway
        # Note: Authorizer is not created yet since it's not being used
        # To enable authentication, uncomment the following and use it in default_method_options:
        # cognito_authorizer = apigateway.CognitoUserPoolsAuthorizer(
        #     self,
        #     "CognitoAuthorizer",
        #     cognito_user_pools=[user_pool_ref],
        #     identity_source="method.request.header.Authorization",
        # )

        # Create /api/v1 proxy resource
        api_v1 = api.root.add_resource("api").add_resource("v1")
        
        # Create health endpoint (public, no auth required)
        health_resource = api_v1.add_resource("health")
        health_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(api_lambda, proxy=True),
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True
                    },
                )
            ],
        )
        
        # Create proxy resource for all other /api/v1/* routes
        # Note: Authorizer can be added later when authentication is needed
        # For now, routes are public (can be secured later)
        # CORS is handled by the API Gateway-level default_cors_preflight_options
        api_v1_proxy = api_v1.add_proxy(
            any_method=True,
            default_integration=apigateway.LambdaIntegration(
                api_lambda,
                proxy=True,
            ),
            # Uncomment to enable Cognito authorizer for protected routes:
            # default_method_options=apigateway.MethodOptions(
            #     authorizer=cognito_authorizer,
            #     authorization_type=apigateway.AuthorizationType.COGNITO,
            # ),
        )

        # Grant API Gateway permission to invoke Lambda
        api_lambda.add_permission(
            "ApiGatewayInvoke",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            source_arn=f"arn:aws:execute-api:{region}:{self.account}:{api.rest_api_id}/*/*",
        )

        # EventBridge Rules for Background Jobs
        # Scheduled rules use default event bus automatically
        # Event pattern rules use default event bus (no explicit bus needed)

        # EventBridge Rule 1: Compute Features Lambda
        # Scheduled: Daily at 1 AM UTC
        compute_features_scheduled_rule = events.Rule(
            self,
            "ComputeFeaturesScheduledRule",
            rule_name=f"spendsense-compute-features-scheduled-{env_name}",
            description="Daily scheduled trigger for compute-features Lambda",
            schedule=events.Schedule.cron(minute="0", hour="1", day="*", month="*", year="*"),
            targets=[
                targets.LambdaFunction(
                    compute_features_lambda,
                    event=events.RuleTargetInput.from_object({
                        "event_type": "scheduled",
                        "user_id": None,  # Process all users
                        "timestamp": events.EventField.from_path("$.time")
                    })
                )
            ]
        )

        # Event pattern: User signup event (uses default event bus)
        compute_features_event_rule = events.Rule(
            self,
            "ComputeFeaturesEventRule",
            rule_name=f"spendsense-compute-features-event-{env_name}",
            description="Trigger compute-features Lambda on user signup",
            event_pattern=events.EventPattern(
                source=["spendsense"],
                detail_type=["User Signup"],
                detail={
                    "event_type": ["user.signup"]
                }
            ),
            targets=[
                targets.LambdaFunction(
                    compute_features_lambda,
                    event=events.RuleTargetInput.from_object({
                        "event_type": events.EventField.from_path("$.detail.event_type"),
                        "user_id": events.EventField.from_path("$.detail.user_id"),
                        "timestamp": events.EventField.from_path("$.time")
                    })
                )
            ]
        )

        # EventBridge Rule 2: Assign Persona Lambda
        # Scheduled: Daily at 1:05 AM UTC (5 minutes after compute-features)
        assign_persona_scheduled_rule = events.Rule(
            self,
            "AssignPersonaScheduledRule",
            rule_name=f"spendsense-assign-persona-scheduled-{env_name}",
            description="Daily scheduled trigger for assign-persona Lambda",
            schedule=events.Schedule.cron(minute="5", hour="1", day="*", month="*", year="*"),
            targets=[
                targets.LambdaFunction(
                    assign_persona_lambda,
                    event=events.RuleTargetInput.from_object({
                        "event_type": "scheduled",
                        "user_id": None,  # Process all users
                        "timestamp": events.EventField.from_path("$.time")
                    })
                )
            ]
        )

        # Event pattern: Features computed event (uses default event bus)
        assign_persona_event_rule = events.Rule(
            self,
            "AssignPersonaEventRule",
            rule_name=f"spendsense-assign-persona-event-{env_name}",
            description="Trigger assign-persona Lambda after features are computed",
            event_pattern=events.EventPattern(
                source=["spendsense"],
                detail_type=["Features Computed"],
                detail={
                    "event_type": ["features.computed"]
                }
            ),
            targets=[
                targets.LambdaFunction(
                    assign_persona_lambda,
                    event=events.RuleTargetInput.from_object({
                        "event_type": events.EventField.from_path("$.detail.event_type"),
                        "user_id": events.EventField.from_path("$.detail.user_id"),
                        "timestamp": events.EventField.from_path("$.time")
                    })
                )
            ]
        )

        # EventBridge Rule 3: Generate Recommendations Lambda
        # Scheduled: Daily at 1:10 AM UTC (10 minutes after compute-features)
        generate_recommendations_scheduled_rule = events.Rule(
            self,
            "GenerateRecommendationsScheduledRule",
            rule_name=f"spendsense-generate-recommendations-scheduled-{env_name}",
            description="Daily scheduled trigger for generate-recommendations Lambda",
            schedule=events.Schedule.cron(minute="10", hour="1", day="*", month="*", year="*"),
            targets=[
                targets.LambdaFunction(
                    generate_recommendations_lambda,
                    event=events.RuleTargetInput.from_object({
                        "event_type": "scheduled",
                        "user_id": None,  # Process all users
                        "timestamp": events.EventField.from_path("$.time")
                    })
                )
            ]
        )

        # Event pattern: Persona assigned event (uses default event bus)
        generate_recommendations_event_rule = events.Rule(
            self,
            "GenerateRecommendationsEventRule",
            rule_name=f"spendsense-generate-recommendations-event-{env_name}",
            description="Trigger generate-recommendations Lambda after persona is assigned",
            event_pattern=events.EventPattern(
                source=["spendsense"],
                detail_type=["Persona Assigned"],
                detail={
                    "event_type": ["persona.assigned"]
                }
            ),
            targets=[
                targets.LambdaFunction(
                    generate_recommendations_lambda,
                    event=events.RuleTargetInput.from_object({
                        "event_type": events.EventField.from_path("$.detail.event_type"),
                        "user_id": events.EventField.from_path("$.detail.user_id"),
                        "timestamp": events.EventField.from_path("$.time")
                    })
                )
            ]
        )

        # Outputs
        CfnOutput(
            self,
            "ApiGatewayUrl",
            value=api.url,
            description="API Gateway endpoint URL",
            export_name=f"{self.stack_name}-ApiGatewayUrl",
        )

        CfnOutput(
            self,
            "ApiGatewayId",
            value=api.rest_api_id,
            description="API Gateway REST API ID",
            export_name=f"{self.stack_name}-ApiGatewayId",
        )

        CfnOutput(
            self,
            "ApiLambdaFunctionArn",
            value=api_lambda.function_arn,
            description="API Lambda function ARN",
            export_name=f"{self.stack_name}-ApiLambdaFunctionArn",
        )

        CfnOutput(
            self,
            "ComputeFeaturesLambdaArn",
            value=compute_features_lambda.function_arn,
            description="Compute Features Lambda function ARN",
        )

        CfnOutput(
            self,
            "AssignPersonaLambdaArn",
            value=assign_persona_lambda.function_arn,
            description="Assign Persona Lambda function ARN",
        )

        CfnOutput(
            self,
            "GenerateRecommendationsLambdaArn",
            value=generate_recommendations_lambda.function_arn,
            description="Generate Recommendations Lambda function ARN",
        )

        # EventBridge Rule ARNs
        CfnOutput(
            self,
            "ComputeFeaturesScheduledRuleArn",
            value=compute_features_scheduled_rule.rule_arn,
            description="EventBridge scheduled rule ARN for compute-features Lambda",
        )

        CfnOutput(
            self,
            "ComputeFeaturesEventRuleArn",
            value=compute_features_event_rule.rule_arn,
            description="EventBridge event rule ARN for compute-features Lambda",
        )

        CfnOutput(
            self,
            "AssignPersonaScheduledRuleArn",
            value=assign_persona_scheduled_rule.rule_arn,
            description="EventBridge scheduled rule ARN for assign-persona Lambda",
        )

        CfnOutput(
            self,
            "AssignPersonaEventRuleArn",
            value=assign_persona_event_rule.rule_arn,
            description="EventBridge event rule ARN for assign-persona Lambda",
        )

        CfnOutput(
            self,
            "GenerateRecommendationsScheduledRuleArn",
            value=generate_recommendations_scheduled_rule.rule_arn,
            description="EventBridge scheduled rule ARN for generate-recommendations Lambda",
        )

        CfnOutput(
            self,
            "GenerateRecommendationsEventRuleArn",
            value=generate_recommendations_event_rule.rule_arn,
            description="EventBridge event rule ARN for generate-recommendations Lambda",
        )

        # Store references
        self.api = api
        self.api_lambda = api_lambda
        self.compute_features_lambda = compute_features_lambda
        self.assign_persona_lambda = assign_persona_lambda
        self.generate_recommendations_lambda = generate_recommendations_lambda

