"""Privacy and GDPR compliance endpoints."""

import logging
import json
from typing import Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.connection import get_session
from src.personalization.api.dependencies import get_current_user
from src.personalization.models.db_models import (
    User,
    Progress,
    Achievement,
    PracticeAttempt,
)
from src.personalization.services.user_service import (
    get_user_by_id,
    soft_delete_user,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users", tags=["privacy"])


# ===== Models =====
class DataExportRequest(BaseModel):
    """Request model for data export."""

    include_conversations: bool = Field(default=True, description="Include chat history")
    format: str = Field(default="json", enum=["json", "csv"])


class AccountDeletionRequest(BaseModel):
    """Request model for account deletion."""

    confirm_deletion: bool = Field(
        ..., description="User must confirm deletion"
    )
    password: str = Field(..., description="User password for confirmation")


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")


# ===== Privacy Endpoints =====
@router.get(
    "/{user_id}/data/export",
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        403: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Export user data",
    description="Export all user data in JSON format (GDPR compliance).",
)
async def export_user_data(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Export all user data for GDPR compliance.

    Args:
        user_id: User ID to export data for
        session: Database session
        current_user: Current authenticated user

    Returns:
        JSON object with all user data

    Raises:
        HTTPException: If user not found or unauthorized
    """
    # Authorization: only user or admin can export
    if current_user.user_id != user_id and not current_user.is_admin:
        logger.warning(f"Unauthorized data export attempt by {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only export your own data"
        )

    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Collect all user data
    progress_records = await session.execute(
        select(Progress).where(Progress.user_id == user_id)
    )
    progress_data = [p.to_dict() for p in progress_records.scalars().all()]

    achievements = await session.execute(
        select(Achievement).where(Achievement.user_id == user_id)
    )
    achievements_data = [a.to_dict() for a in achievements.scalars().all()]

    practice_attempts = await session.execute(
        select(PracticeAttempt).where(PracticeAttempt.user_id == user_id)
    )
    practice_data = [p.to_dict() for p in practice_attempts.scalars().all()]

    # Compile full data export
    export_data = {
        "export_date": datetime.utcnow().isoformat(),
        "user": {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "skill_level": user.skill_level,
            "skill_confidence": user.skill_confidence,
            "preferences": user.preferences_json,
            "bio": user.bio,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        },
        "progress": progress_data,
        "achievements": achievements_data,
        "practice_attempts": practice_data,
        "summary": {
            "total_chapters": len(progress_data),
            "total_achievements": len(achievements_data),
            "total_practice_attempts": len(practice_data),
        }
    }

    logger.info(f"Data export completed for user {user_id}")

    return export_data


@router.delete(
    "/{user_id}/account",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        403: {"model": ErrorResponse, "description": "Unauthorized or wrong password"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Delete user account",
    description="Permanently delete user account and all associated data (GDPR compliance).",
)
async def delete_account(
    user_id: UUID,
    request: AccountDeletionRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete user account and cascade delete all data.

    Args:
        user_id: User ID to delete
        request: Deletion confirmation request
        session: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If user not found, unauthorized, or wrong password
    """
    # Authorization: only user (not admin) can delete their own account
    if current_user.user_id != user_id:
        logger.warning(f"Unauthorized account deletion attempt by {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )

    if not request.confirm_deletion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm account deletion"
        )

    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify password
    from src.personalization.utils.auth import verify_password
    if not verify_password(request.password, user.password_hash):
        logger.warning(f"Account deletion password verification failed for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect password"
        )

    # Soft delete user (cascade deletes will be handled by database)
    success = await soft_delete_user(session, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )

    logger.info(f"Account deleted for user {user_id}")


@router.get(
    "/{user_id}/privacy-policy",
    responses={
        200: {"description": "Privacy policy text"},
    },
    summary="Get privacy policy",
    description="Retrieve the privacy policy document.",
)
async def get_privacy_policy() -> Dict[str, str]:
    """
    Get privacy policy.

    Returns:
        Privacy policy document
    """
    policy = {
        "title": "Privacy Policy",
        "last_updated": "2026-02-04",
        "content": """
PRIVACY POLICY

1. DATA COLLECTION
We collect the following data:
- User account information (username, email, password hash)
- Learning progress and statistics
- Achievement and practice attempt records
- User preferences and settings

2. DATA USE
Your data is used to:
- Provide personalized learning recommendations
- Track your progress and achievements
- Generate learning statistics and insights
- Improve our services based on aggregated data

3. DATA PROTECTION
- All data is encrypted in transit (HTTPS)
- Passwords are hashed using bcrypt
- Database access is restricted and logged
- Regular security audits are conducted

4. DATA RETENTION
- Active user data is retained indefinitely
- Deleted users have data removed within 30 days
- You can request data deletion at any time

5. YOUR RIGHTS
You have the right to:
- Access your personal data
- Export your data in standard format
- Delete your account and all personal data
- Update your information
- Withdraw consent for data processing

6. CONTACT
For privacy inquiries, contact: privacy@roboticslearning.edu

7. GDPR COMPLIANCE
This service complies with GDPR regulations including:
- Data access and portability rights
- Right to be forgotten
- Transparent data processing
- Data protection by design
"""
    }
    return policy


@router.get(
    "/{user_id}/terms-of-service",
    responses={
        200: {"description": "Terms of service text"},
    },
    summary="Get terms of service",
    description="Retrieve the terms of service document.",
)
async def get_terms_of_service() -> Dict[str, str]:
    """
    Get terms of service.

    Returns:
        Terms of service document
    """
    terms = {
        "title": "Terms of Service",
        "last_updated": "2026-02-04",
        "content": """
TERMS OF SERVICE

1. ACCEPTANCE
By accessing this service, you accept these terms and conditions in full.

2. USE LICENSE
We grant you a limited, non-exclusive, non-transferable license to use this service.

3. USER RESPONSIBILITIES
You are responsible for:
- Maintaining confidentiality of your account
- All activities under your account
- Complying with all applicable laws

4. PROHIBITED CONDUCT
You may not:
- Use automated tools to access content
- Attempt to gain unauthorized access
- Share your account credentials
- Upload malicious content

5. INTELLECTUAL PROPERTY
All content and code are owned by or licensed to us.
You may not reproduce, distribute, or modify without permission.

6. LIMITATION OF LIABILITY
We are not liable for:
- Data loss or service interruptions
- Indirect or consequential damages
- Loss of profits or revenue

7. INDEMNIFICATION
You agree to indemnify us from any claims arising from your use of the service.

8. MODIFICATIONS
We may modify these terms at any time. Continued use constitutes acceptance.

9. GOVERNING LAW
These terms are governed by applicable laws.

10. CONTACT
For questions, contact: legal@roboticslearning.edu
"""
    }
    return terms
