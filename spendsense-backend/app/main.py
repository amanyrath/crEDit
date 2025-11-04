"""FastAPI application entry point"""

from fastapi import FastAPI
from app.api.v1 import consumer, operator

app = FastAPI(
    title="SpendSense API",
    description="Financial education platform API",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SpendSense API"}


# Register API routers
app.include_router(consumer.router, prefix="/api/v1")
app.include_router(operator.router, prefix="/api/v1")
