"""
Email Suppression Router
API endpoints for checking and removing email addresses from OCI suppression list.
"""
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from oci.exceptions import ServiceError

from app.services.oci_email_suppression import email_suppression_service


# Create router instance
router = APIRouter(
    prefix="/api/v1/email-suppression",
    tags=["Email Suppression"]
)


# Response Models (for API documentation and validation)
class SuppressionDetail(BaseModel):
    """Details about a suppression entry"""
    id: str
    reason: str
    time_created: str


class CheckSuppressionResponse(BaseModel):
    """Response model for checking suppression status"""
    email: str
    is_suppressed: bool
    suppression: Optional[SuppressionDetail] = None


class RemoveSuppressionResponse(BaseModel):
    """Response model for removing suppression"""
    message: str
    email: str
    removed: bool
    suppression_id: str
    previous_reason: str
    previous_time_created: str


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    email: Optional[str] = None


# API Endpoints

@router.get(
    "/{email}",
    response_model=CheckSuppressionResponse,
    summary="Check if email is suppressed",
    description="Check if an email address is in the OCI Email Delivery suppression list"
)
async def check_suppression(
    email: str = Path(
        ...,
        description="Email address to check",
        example="user@example.com"
    )
) -> CheckSuppressionResponse:
    """
    Check if an email address is in the suppression list.

    **Args:**
    - **email**: Email address to check (from URL path)

    **Returns:**
    - Email suppression status with details if suppressed

    **Example:**
    ```
    GET /api/v1/email-suppression/user@example.com
    ```
    """
    try:
        result = await email_suppression_service.check_suppression(email)
        return CheckSuppressionResponse(**result)

    except ServiceError as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCI API Error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete(
    "/{email}",
    response_model=RemoveSuppressionResponse,
    summary="Remove email from suppression list",
    description="Remove an email address from the OCI Email Delivery suppression list",
    responses={
        200: {"description": "Email successfully removed from suppression list"},
        404: {"description": "Email not found in suppression list"},
        500: {"description": "Internal server error or OCI API error"}
    }
)
async def remove_suppression(
    email: str = Path(
        ...,
        description="Email address to remove from suppression list",
        example="user@example.com"
    )
) -> RemoveSuppressionResponse:
    """
    Remove an email address from the suppression list.

    **Args:**
    - **email**: Email address to remove (from URL path)

    **Returns:**
    - Removal confirmation with details about the removed suppression

    **Raises:**
    - **404**: If email is not in the suppression list
    - **500**: If OCI API call fails

    **Example:**
    ```
    DELETE /api/v1/email-suppression/user@example.com
    ```
    """
    try:
        result = await email_suppression_service.remove_suppression(email)
        return RemoveSuppressionResponse(**result)

    except ValueError as e:
        # Email not in suppression list
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except ServiceError as e:
        # OCI API error
        raise HTTPException(
            status_code=500,
            detail=f"OCI API Error: {e.message}"
        )

    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
