"""
Cognito Stack - User Pool, Groups, and Secrets Manager
"""
from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    aws_secretsmanager as secretsmanager,
    RemovalPolicy,
    Duration,
    CfnOutput,
)
from constructs import Construct


class CognitoStack(Stack):
    """
    Creates Cognito User Pool with:
    - Email/password authentication
    - User groups (consumers, operators)
    - JWT token configuration
    - Custom attributes (email, role)
    - Secrets Manager for configuration
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Cognito User Pool
        user_pool = cognito.UserPool(
            self,
            "UserPool",
            user_pool_name=f"spendsense-{self.node.try_get_context('environment') or 'dev'}",
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=False),  # Disable email verification for demo
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=True)
            ),
            custom_attributes={
                "role": cognito.StringAttribute(
                    min_len=1,
                    max_len=50,
                    mutable=True
                )
            },
            # Note: Custom attributes are prefixed with "custom:" in Cognito
            # This defines "custom:role" attribute
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.DESTROY,  # Set to RETAIN for production
            mfa=cognito.Mfa.OFF,  # Disabled for MVP, can be enabled later
            mfa_second_factor=cognito.MfaSecondFactor(
                sms=False,
                otp=True,
            ),
        )

        # Create User Pool Client with token expiration configuration
        user_pool_client = user_pool.add_client(
            "UserPoolClient",
            user_pool_client_name="spendsense-app-client",
            generate_secret=False,  # Public client for web/mobile apps
            auth_flows=cognito.AuthFlow(
                user_password=True,
                refresh_token=True,
                user_srp=False,  # Can be enabled later if needed
            ),
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30),
            prevent_user_existence_errors=True,
        )

        # Create user groups
        consumers_group = cognito.CfnUserPoolGroup(
            self,
            "ConsumersGroup",
            user_pool_id=user_pool.user_pool_id,
            group_name="consumers",
            description="Regular users who use the application",
        )

        operators_group = cognito.CfnUserPoolGroup(
            self,
            "OperatorsGroup",
            user_pool_id=user_pool.user_pool_id,
            group_name="operators",
            description="Admin/operator users who can perform administrative actions",
        )

        # Create Secrets Manager secret for Cognito configuration
        cognito_config_secret = secretsmanager.Secret(
            self,
            "CognitoConfiguration",
            secret_name="spendsense/cognito/configuration",
            description="Cognito User Pool configuration for SpendSense",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"user_pool_id":"PLACEHOLDER","user_pool_arn":"PLACEHOLDER","client_id":"PLACEHOLDER","region":"PLACEHOLDER"}',
                generate_string_key="placeholder",
            ),
        )

        # Update the secret with actual values after stack creation
        # Note: This will be updated via a script or custom resource after deployment
        # For now, we'll document the manual update process

        # Outputs
        CfnOutput(
            self,
            "UserPoolId",
            value=user_pool.user_pool_id,
            description="Cognito User Pool ID",
            export_name=f"{self.stack_name}-UserPoolId",
        )

        CfnOutput(
            self,
            "UserPoolArn",
            value=user_pool.user_pool_arn,
            description="Cognito User Pool ARN",
            export_name=f"{self.stack_name}-UserPoolArn",
        )

        CfnOutput(
            self,
            "UserPoolClientId",
            value=user_pool_client.user_pool_client_id,
            description="Cognito User Pool Client ID",
            export_name=f"{self.stack_name}-UserPoolClientId",
        )

        CfnOutput(
            self,
            "CognitoConfigSecretArn",
            value=cognito_config_secret.secret_arn,
            description="ARN of the Cognito configuration secret",
            export_name=f"{self.stack_name}-CognitoConfigSecretArn",
        )

        # Store references for potential cross-stack access
        self.user_pool = user_pool
        self.user_pool_client = user_pool_client
        self.consumers_group = consumers_group
        self.operators_group = operators_group
        self.cognito_config_secret = cognito_config_secret

