"""
Admin Management Routers for SPHERE
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserResponse
from app.dependencies import get_current_admin
from typing import List

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Get all users (admin only)"""
    
    users = db.query(User).all()
    return users


@router.put("/users/{user_id}/activate")
async def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Toggle user active/inactive status (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deactivating admin
    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate admin users"
        )
    
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    return {"message": "User status updated", "user": UserResponse.from_orm(user)}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Delete user (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting admin
    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete admin users"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}