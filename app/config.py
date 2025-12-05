"""
Configuration management for the application.
Uses environment variables with fallback defaults.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OCI Configuration
    oci_tenancy_ocid: str = "ocid1.tenancy.oc1..aaaaaaaabyypi3rfbeajp3lix4wwkrmsewwvz2rezuneuxnpmnl76eufa3oa"
    oci_region: str = "ap-mumbai-1"

    # API Configuration
    api_title: str = "OCI Business Logic Service"
    api_version: str = "1.0.0"
    api_description: str = "FastAPI service for OCI business logic operations"

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"  # Options: "json" or "text"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
