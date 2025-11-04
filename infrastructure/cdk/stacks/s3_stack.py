"""
S3 Stack - S3 Buckets and CloudFront Distribution
"""
from aws_cdk import (
    Stack,
    Duration,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_iam as iam,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct


class S3Stack(Stack):
    """
    Creates S3 buckets and CloudFront distribution with:
    - S3 bucket for frontend hosting
    - S3 bucket for static assets
    - CloudFront distribution with Origin Access Control (OAC)
    - CORS configuration
    - Bucket policies for CloudFront access
    - Error pages configured for SPA routing
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env_name = self.node.try_get_context("environment") or "dev"
        account_id = self.account
        region = self.region

        # Create S3 bucket for frontend hosting
        # Note: We do NOT enable static website hosting because CloudFront will serve the content
        # Static website hosting would make CloudFront use the website endpoint which doesn't support OAI
        frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            bucket_name=f"spendsense-frontend-{env_name}",
            # website_index_document and website_error_document removed - CloudFront handles this
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,  # Enable versioning for rollback capability
            removal_policy=RemovalPolicy.DESTROY,  # Set to RETAIN for production
            auto_delete_objects=True,  # Automatically delete objects when stack is deleted
        )

        # Create S3 bucket for static assets
        assets_bucket = s3.Bucket(
            self,
            "AssetsBucket",
            bucket_name=f"spendsense-assets-{env_name}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,  # Enable versioning for rollback capability
            removal_policy=RemovalPolicy.DESTROY,  # Set to RETAIN for production
            auto_delete_objects=True,  # Automatically delete objects when stack is deleted
        )

        # Configure CORS for frontend bucket
        frontend_bucket.add_cors_rule(
            allowed_origins=["*"],  # Allow all origins for dev, restrict for prod
            allowed_methods=[
                s3.HttpMethods.GET,
                s3.HttpMethods.HEAD,
            ],
            allowed_headers=["*"],
            exposed_headers=["ETag", "Last-Modified"],
            max_age=3000,
        )

        # Configure CORS for assets bucket
        assets_bucket.add_cors_rule(
            allowed_origins=["*"],  # Allow all origins for dev, restrict for prod
            allowed_methods=[
                s3.HttpMethods.GET,
                s3.HttpMethods.HEAD,
            ],
            allowed_headers=["*"],
            exposed_headers=["ETag", "Last-Modified"],
            max_age=3000,
        )

        # Create custom cache policy for SPA routing (forward query strings)
        # This allows React Router to work properly with query parameters
        cache_policy = cloudfront.CachePolicy(
            self,
            "FrontendCachePolicy",
            cache_policy_name=f"spendsense-frontend-cache-{env_name}",
            default_ttl=Duration.hours(1),
            min_ttl=Duration.seconds(0),
            max_ttl=Duration.days(1),
            enable_accept_encoding_brotli=True,
            enable_accept_encoding_gzip=True,
            query_string_behavior=cloudfront.CacheQueryStringBehavior.all(),
            header_behavior=cloudfront.CacheHeaderBehavior.allow_list("Accept", "Accept-Language"),
            cookie_behavior=cloudfront.CacheCookieBehavior.none(),
        )

        # Create CloudFront Origin Access Identity (OAI) for S3 bucket access
        # Note: OAI is being used instead of OAC because S3Origin uses OAI by default
        # OAC is preferred but requires using L1 constructs which is more complex
        oai = cloudfront.OriginAccessIdentity(
            self,
            "OriginAccessIdentity",
            comment=f"OAI for SpendSense frontend bucket ({env_name})",
        )
        
        # Grant the OAI read access to the bucket
        frontend_bucket.grant_read(oai)
        
        # Create CloudFront distribution for frontend bucket
        distribution = cloudfront.Distribution(
            self,
            "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    frontend_bucket,
                    origin_access_identity=oai,
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD,
                cache_policy=cache_policy,
                compress=True,
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(300),
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(300),
                ),
            ],
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,  # Use North America and Europe for cost optimization
            comment=f"CloudFront distribution for SpendSense frontend ({env_name})",
        )

        # Outputs
        CfnOutput(
            self,
            "FrontendBucketName",
            value=frontend_bucket.bucket_name,
            description="S3 bucket name for frontend hosting",
            export_name=f"{self.stack_name}-FrontendBucketName",
        )

        CfnOutput(
            self,
            "FrontendBucketArn",
            value=frontend_bucket.bucket_arn,
            description="S3 bucket ARN for frontend hosting",
            export_name=f"{self.stack_name}-FrontendBucketArn",
        )

        CfnOutput(
            self,
            "AssetsBucketName",
            value=assets_bucket.bucket_name,
            description="S3 bucket name for static assets",
            export_name=f"{self.stack_name}-AssetsBucketName",
        )

        CfnOutput(
            self,
            "AssetsBucketArn",
            value=assets_bucket.bucket_arn,
            description="S3 bucket ARN for static assets",
            export_name=f"{self.stack_name}-AssetsBucketArn",
        )

        CfnOutput(
            self,
            "CloudFrontDistributionId",
            value=distribution.distribution_id,
            description="CloudFront distribution ID",
            export_name=f"{self.stack_name}-CloudFrontDistributionId",
        )

        CfnOutput(
            self,
            "CloudFrontDistributionUrl",
            value=f"https://{distribution.distribution_domain_name}",
            description="CloudFront distribution URL",
            export_name=f"{self.stack_name}-CloudFrontDistributionUrl",
        )

        CfnOutput(
            self,
            "CloudFrontDistributionDomainName",
            value=distribution.distribution_domain_name,
            description="CloudFront distribution domain name",
            export_name=f"{self.stack_name}-CloudFrontDistributionDomainName",
        )

        # Store for reference
        self.frontend_bucket = frontend_bucket
        self.assets_bucket = assets_bucket
        self.distribution = distribution

