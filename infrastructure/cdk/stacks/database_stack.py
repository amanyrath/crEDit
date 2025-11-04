"""
Database Stack - RDS PostgreSQL and Secrets Manager
"""
from aws_cdk import (
    Stack,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_secretsmanager as secretsmanager,
    aws_kms as kms,
    RemovalPolicy,
    Duration,
    CfnOutput,
)
from constructs import Construct


class DatabaseStack(Stack):
    """
    Creates RDS PostgreSQL database with:
    - PostgreSQL 15.x on db.t3.micro
    - Encryption at rest
    - Automated backups
    - Security groups for Lambda access
    - Secrets Manager for connection string
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get VPC - use default VPC for MVP, can be parameterized later
        vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)

        # Create KMS key for RDS encryption
        kms_key = kms.Key(
            self,
            "DatabaseEncryptionKey",
            description="KMS key for RDS PostgreSQL encryption",
            enable_key_rotation=True,
        )

        # Create security group for RDS database
        db_security_group = ec2.SecurityGroup(
            self,
            "DatabaseSecurityGroup",
            vpc=vpc,
            description="Security group for RDS PostgreSQL database",
            allow_all_outbound=True,
        )

        # Create security group for Lambda functions (will be referenced by Lambda stack)
        lambda_security_group = ec2.SecurityGroup(
            self,
            "LambdaSecurityGroup",
            vpc=vpc,
            description="Security group for Lambda functions accessing RDS",
            allow_all_outbound=True,
        )

        # Allow Lambda security group to connect to RDS on port 5432
        db_security_group.add_ingress_rule(
            peer=lambda_security_group,
            connection=ec2.Port.tcp(5432),
            description="Allow Lambda functions to connect to PostgreSQL",
        )

        # Create database subnet group
        # For default VPC, use public subnets (default VPC typically only has public subnets)
        # For production with custom VPC, use private subnets
        subnet_group = rds.SubnetGroup(
            self,
            "DatabaseSubnetGroup",
            vpc=vpc,
            description="Subnet group for RDS PostgreSQL database",
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
        )

        # Generate database credentials in Secrets Manager
        db_credentials = rds.DatabaseSecret(
            self,
            "DatabaseCredentials",
            username="spendsense_admin",
            secret_name="spendsense/database/credentials",
        )

        # Create RDS PostgreSQL instance
        # Use PostgreSQL 15.14 (latest available version in us-east-1)
        database = rds.DatabaseInstance(
            self,
            "PostgreSQLDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15_14
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            subnet_group=subnet_group,
            security_groups=[db_security_group],
            database_name="spendsense",
            credentials=rds.Credentials.from_secret(db_credentials),
            backup_retention=Duration.days(7),
            delete_automated_backups=True,
            deletion_protection=False,  # Set to True for production
            removal_policy=RemovalPolicy.DESTROY,  # Set to RETAIN for production
            storage_encrypted=True,
            storage_encryption_key=kms_key,
            multi_az=False,  # Enable for production
            auto_minor_version_upgrade=True,
        )

        # Create connection string secret
        # Format: postgresql://username:password@host:5432/database_name
        connection_string_secret = secretsmanager.Secret(
            self,
            "DatabaseConnectionString",
            secret_name="spendsense/database/connection",
            description="Database connection string for SpendSense PostgreSQL",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"host":"PLACEHOLDER","port":"5432","database":"spendsense","username":"PLACEHOLDER"}',
                generate_string_key="password",
                exclude_characters='"@/\\',
            ),
            # This will be updated after database is created
        )

        # After database is created, we need to update the connection string
        # This is typically done via a custom resource or Lambda function
        # For now, we'll create a manual instruction in the README

        # Outputs
        CfnOutput(
            self,
            "DatabaseEndpoint",
            value=database.instance_endpoint.hostname,
            description="RDS PostgreSQL endpoint",
            export_name=f"{self.stack_name}-DatabaseEndpoint",
        )

        CfnOutput(
            self,
            "DatabasePort",
            value=str(database.instance_endpoint.port),
            description="RDS PostgreSQL port",
            export_name=f"{self.stack_name}-DatabasePort",
        )

        CfnOutput(
            self,
            "DatabaseName",
            value="spendsense",
            description="RDS PostgreSQL database name",
            export_name=f"{self.stack_name}-DatabaseName",
        )

        CfnOutput(
            self,
            "CredentialsSecretArn",
            value=db_credentials.secret_arn,
            description="ARN of the database credentials secret",
            export_name=f"{self.stack_name}-CredentialsSecretArn",
        )

        CfnOutput(
            self,
            "ConnectionStringSecretArn",
            value=connection_string_secret.secret_arn,
            description="ARN of the connection string secret",
            export_name=f"{self.stack_name}-ConnectionStringSecretArn",
        )

        CfnOutput(
            self,
            "LambdaSecurityGroupId",
            value=lambda_security_group.security_group_id,
            description="Security group ID for Lambda functions",
            export_name=f"{self.stack_name}-LambdaSecurityGroupId",
        )

        # Store outputs for reference
        self.database = database
        self.db_credentials = db_credentials
        self.connection_string_secret = connection_string_secret
        self.lambda_security_group = lambda_security_group

