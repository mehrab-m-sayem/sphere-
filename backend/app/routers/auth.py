"""
Authentication Routers for SPHERE
"""
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas import (
    DoctorRegister,
    PatientRegister,
    UserLogin,
    TokenResponse,
    LoginResponse,
    UserResponse
)
from app.auth.password import PasswordManager
from app.auth.jwt_handler import JWTManager
from app.auth.two_factor import TwoFactorAuth
from app.services.email_service import EmailService

router = APIRouter(prefix="/api", tags=["auth"])
jwt_manager = JWTManager()
password_manager = PasswordManager()
two_fa = TwoFactorAuth()
email_service = EmailService()


def get_role_for_registration(db: Session):
    """Assign first user as admin, rest keep their chosen role"""
    user_count = db.query(User).count()
    return "admin" if user_count == 0 else None


@router.post("/register/doctor", response_model=UserResponse)
async def register_doctor(data: DoctorRegister, db: Session = Depends(get_db)):
    """Register a new doctor"""
    
    # Validate passwords match
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if user already exists
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Determine role - first user is admin, rest are doctors
    assigned_role = get_role_for_registration(db)
    if assigned_role is None:
        assigned_role = "doctor"
    
    # Create new user
    hashed_password = password_manager.hash_password(data.password)
    user = User(
        username=data.username,
        email=data.email,
        name=data.name,
        hashed_password=hashed_password,
        specialization=data.specialization,
        contact_no=data.contact_no,
        role=assigned_role,
        two_factor_enabled=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/register/patient", response_model=UserResponse)
async def register_patient(data: PatientRegister, db: Session = Depends(get_db)):
    """Register a new patient"""
    
    # Validate passwords match
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if user already exists
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Determine role - first user is admin, rest are patients
    assigned_role = get_role_for_registration(db)
    if assigned_role is None:
        assigned_role = "patient"
    
    # Create new user
    hashed_password = password_manager.hash_password(data.password)
    user = User(
        username=data.username,
        email=data.email,
        name=data.name,
        hashed_password=hashed_password,
        age=data.age,
        sex=data.sex,
        contact_no=data.contact_no,
        role=assigned_role,
        two_factor_enabled=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=LoginResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login user - returns 2FA requirement if needed"""
    
    # Hash email for search
    email_hash = hashlib.sha256(data.email.encode()).hexdigest()
    print(f"\n🔍 Login attempt for email: {data.email}")
    print(f"🔍 Email hash: {email_hash}")
    
    user = db.query(User).filter(User.email_hash == email_hash).first()
    
    if not user:
        print(f"❌ User not found with email hash: {email_hash}")
        # Try to find all users for debugging
        all_users = db.query(User).all()
        print(f"📊 Total users in DB: {len(all_users)}")
        for u in all_users:
            print(f"   - Email hash in DB: {u.email_hash}, Decrypted email: {u.email}")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    print(f"✓ User found: {user.email}")
    
    # Verify password
    password_match = password_manager.verify_password(data.password, user.hashed_password)
    print(f"🔐 Password match: {password_match}")
    print(f"🔐 Stored hash: {user.hashed_password[:50]}...")
    
    if not password_match:
        print(f"Password mismatch for user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Check if 2FA is enabled
    if user.two_factor_enabled:
        # Generate 2FA code
        code = two_fa.generate_code()
        temp_token = jwt_manager.create_temp_token({"user_id": user.id, "code": code})
        
        print(f"2FA enabled for user {user.email}, code: {code}")
        
        # Send code via email (simulated for development)
        await email_service.send_2fa_code(user.email, code)
        
        return LoginResponse(
            requires_2fa=True,
            temp_token=temp_token
        )
    
    # Create access token
    access_token = jwt_manager.create_access_token(data={"sub": str(user.id)})
    
    print(f"Login successful for user: {user.email}")
    
    return LoginResponse(
        access_token=access_token,
        requires_2fa=False,
        user=UserResponse.from_orm(user)
    )

@router.post("/2fa/verify", response_model=TokenResponse)
async def verify_2fa(data: dict, db: Session = Depends(get_db)):
    """Verify 2FA code"""
    
    temp_token = data.get("temp_token")
    code = data.get("code")
    
    payload = jwt_manager.verify_token(temp_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid temp token"
        )
    
    user_id = payload.get("user_id")
    stored_code = payload.get("code")
    
    if code != stored_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create access token
    access_token = jwt_manager.create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.post("/2fa/resend")
async def resend_2fa(data: dict, db: Session = Depends(get_db)):
    """Resend 2FA code"""
    
    temp_token = data.get("temp_token")
    
    payload = jwt_manager.verify_token(temp_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid temp token"
        )
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate new code
    code = two_fa.generate_code()
    new_temp_token = jwt_manager.create_temp_token({"user_id": user.id, "code": code})
    
    # Send code via email
    await email_service.send_2fa_code(user.email, code)
    
    return {"temp_token": new_temp_token}