"""Lambda handler for AWS Lambda deployment"""

from mangum import Mangum
from app.main import app

# Create ASGI adapter for Lambda
handler = Mangum(app)

