"""
OCI Email Suppression Service
Handles checking and removing email addresses from OCI Email Delivery suppression list.
"""
import oci
from oci.auth.signers import InstancePrincipalsSecurityTokenSigner
from oci.exceptions import ServiceError
from typing import Dict, Optional
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class EmailSuppressionService:
    """Service for managing OCI Email Delivery suppressions."""

    def __init__(self):
        """Initialize the OCI Email client with Instance Principals authentication."""
        self.signer = InstancePrincipalsSecurityTokenSigner()
        self.client = oci.email.EmailClient(
            config={"region": settings.oci_region},
            signer=self.signer
        )

    async def check_suppression(self, email: str) -> Dict[str, any]:
        """
        Check if an email address is in the suppression list.

        Args:
            email: Email address to check

        Returns:
            Dict with suppression details if found, None if not found

        Raises:
            ServiceError: If OCI API call fails
        """
        logger.info("Checking suppression status", extra={"email": email})

        try:
            # Log OCI API call
            logger.info(
                "Calling OCI API: list_suppressions",
                extra={
                    "email": email,
                    "compartment_id": settings.oci_tenancy_ocid[:20] + "..."
                }
            )

            response = self.client.list_suppressions(
                compartment_id=settings.oci_tenancy_ocid,
                email_address=email
            )

            if not response.data:
                logger.info(
                    "Email not in suppression list",
                    extra={"email": email, "is_suppressed": False}
                )
                return {
                    "email": email,
                    "is_suppressed": False,
                    "suppression": None
                }

            suppression = response.data[0]
            logger.info(
                "Email found in suppression list",
                extra={
                    "email": email,
                    "is_suppressed": True,
                    "suppression_id": suppression.id,
                    "reason": suppression.reason
                }
            )
            return {
                "email": email,
                "is_suppressed": True,
                "suppression": {
                    "id": suppression.id,
                    "reason": suppression.reason,
                    "time_created": str(suppression.time_created)
                }
            }

        except ServiceError as e:
            logger.error(
                f"OCI API error while checking suppression",
                extra={
                    "email": email,
                    "error_code": e.code,
                    "error_status": e.status,
                    "error_message": e.message
                }
            )
            raise ServiceError(
                status=e.status,
                code=e.code,
                headers=e.headers,
                message=f"Failed to check suppression for {email}: {e.message}"
            )

    async def remove_suppression(self, email: str) -> Dict[str, any]:
        """
        Remove an email address from the suppression list.

        Args:
            email: Email address to remove

        Returns:
            Dict with operation result

        Raises:
            ServiceError: If OCI API call fails
            ValueError: If email is not in suppression list
        """
        logger.info("Removing suppression", extra={"email": email})

        # First check if email is suppressed
        check_result = await self.check_suppression(email)

        if not check_result["is_suppressed"]:
            logger.warning(
                "Cannot remove - email not in suppression list",
                extra={"email": email}
            )
            raise ValueError(f"Email '{email}' is not in the suppression list")

        # Remove the suppression
        suppression_id = check_result["suppression"]["id"]
        suppression_reason = check_result["suppression"]["reason"]

        logger.info(
            "Found suppression entry - proceeding with deletion",
            extra={
                "email": email,
                "suppression_id": suppression_id,
                "reason": suppression_reason
            }
        )

        try:
            logger.info(
                "Calling OCI API: delete_suppression",
                extra={"email": email, "suppression_id": suppression_id}
            )

            self.client.delete_suppression(suppression_id)

            logger.info(
                "Successfully removed suppression",
                extra={
                    "email": email,
                    "suppression_id": suppression_id,
                    "previous_reason": suppression_reason
                }
            )

            return {
                "message": f"Email '{email}' has been successfully removed from the suppression list",
                "email": email,
                "removed": True,
                "suppression_id": suppression_id,
                "previous_reason": check_result["suppression"]["reason"],
                "previous_time_created": check_result["suppression"]["time_created"]
            }

        except ServiceError as e:
            logger.error(
                "OCI API error while removing suppression",
                extra={
                    "email": email,
                    "suppression_id": suppression_id,
                    "error_code": e.code,
                    "error_status": e.status,
                    "error_message": e.message
                }
            )
            raise ServiceError(
                status=e.status,
                code=e.code,
                headers=e.headers,
                message=f"Failed to remove suppression for {email}: {e.message}"
            )


# Create a singleton instance
email_suppression_service = EmailSuppressionService()
