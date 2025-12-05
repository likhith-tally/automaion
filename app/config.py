"""
Configuration management for the application.
Uses environment variables with fallback defaults.
"""
import os
from pydantic_settings import BaseSettings
from typing import Dict, Any


# Environment-specific configurations
ENVIRONMENT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "development": {
        "parent_tenancy_ocid": "ocid1.tenancy.oc1..aaaaaaaabyypi3rfbeajp3lix4wwkrmsewwvz2rezuneuxnpmnl76eufa3oa",
        "oci_region": "ap-mumbai-1",
        "log_level": "DEBUG",
        "log_format": "text"
    },
    "staging": {
        "parent_tenancy_ocid": "ocid1.tenancy.oc1..aaaaaaaabyypi3rfbeajp3lix4wwkrmsewwvz2rezuneuxnpmnl76eufa3oa",
        "oci_region": "ap-mumbai-1",
        "log_level": "INFO",
        "log_format": "json"
    },
    "production": {
        "parent_tenancy_ocid": "ocid1.tenancy.oc1..aaaaaaaa2elmflewdp5zcljlbvbdxxnpkrrnajlsjgcf4jx73tnh47ln2sya",
        "oci_region": "ap-mumbai-1",
        "log_level": "INFO",
        "log_format": "json"
    }
}


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment selector (only this needs to be set via env var)
    environment: str = "production"  # Options: development, staging, production

    # OCI Configuration (will be set based on environment)
    parent_tenancy_ocid: str = ""
    oci_region: str = ""

    # API Configuration
    api_title: str = "OCI Business Logic Service"
    api_version: str = "1.0.0"
    api_description: str = "FastAPI service for OCI business logic operations"

    # Logging Configuration (will be set based on environment)
    log_level: str = ""
    log_format: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        """Initialize settings and load environment-specific config."""
        super().__init__(**kwargs)

        # Load environment-specific configuration
        env_config = ENVIRONMENT_CONFIGS.get(self.environment)

        if not env_config:
            raise ValueError(
                f"Invalid environment '{self.environment}'. "
                f"Valid options: {', '.join(ENVIRONMENT_CONFIGS.keys())}"
            )

        # Apply environment-specific settings (only if not overridden by env vars)
        if not self.parent_tenancy_ocid:
            self.parent_tenancy_ocid = env_config["parent_tenancy_ocid"]
        if not self.oci_region:
            self.oci_region = env_config["oci_region"]
        if not self.log_level:
            self.log_level = env_config["log_level"]
        if not self.log_format:
            self.log_format = env_config["log_format"]


# Global settings instance
settings = Settings()
