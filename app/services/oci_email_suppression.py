"""
OCI Email Suppression Service
Handles checking and removing email addresses from OCI Email Delivery suppression list.
"""
import oci
from oci.auth.signers import InstancePrincipalsSecurityTokenSigner
from oci.exceptions import ServiceError
from typing import Dict, Optional
from app.config import settings


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
        try:
            response = self.client.list_suppressions(
                compartment_id=settings.oci_tenancy_ocid,
                email_address=email
            )

            if not response.data:
                return {
                    "email": email,
                    "is_suppressed": False,
                    "suppression": None
                }

            suppression = response.data[0]
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
        # First check if email is suppressed
        check_result = await self.check_suppression(email)

        if not check_result["is_suppressed"]:
            raise ValueError(f"Email '{email}' is not in the suppression list")

        # Remove the suppression
        suppression_id = check_result["suppression"]["id"]

        try:
            self.client.delete_suppression(suppression_id)

            return {
                "message": f"Email '{email}' has been successfully removed from the suppression list",
                "email": email,
                "removed": True,
                "suppression_id": suppression_id,
                "previous_reason": check_result["suppression"]["reason"],
                "previous_time_created": check_result["suppression"]["time_created"]
            }

        except ServiceError as e:
            raise ServiceError(
                status=e.status,
                code=e.code,
                headers=e.headers,
                message=f"Failed to remove suppression for {email}: {e.message}"
            )


# Create a singleton instance
email_suppression_service = EmailSuppressionService()
