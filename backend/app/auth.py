"""
Authentication Routers for SPHERE
"""
from app.crypto.mac import SHA256
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
    """Assign first user as admin, rest as their chosen role"""
    user_count = db.query(User).count()
    return "admin" if user_count == 0 else None

def hash_for_search(value: str) -> str:
    """Create hash for search indexing using custom SHA256"""
    sha256 = SHA256()
    return sha256.hash_hex(value)


@router.post("/register/doctor", response_model=UserResponse)
async def register_doctor(data: DoctorRegister, db: Session = Depends(get_db)):
    """Register a new doctor - all data encrypted"""
    
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check using hashed values
    email_hash = hash_for_search(data.email)
    username_hash = hash_for_search(data.username)
    
    print(f"\n📝 Registering Doctor:")
    print(f"   Email: {data.email}")
    print(f"   Email Hash: {email_hash}")
    print(f"   Username: {data.username}")
    print(f"   Username Hash: {username_hash}")
    
    if db.query(User).filter(User.email_hash == email_hash).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if db.query(User).filter(User.username_hash == username_hash).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    assigned_role = get_role_for_registration(db)
    if assigned_role is None:
        assigned_role = "doctor"
    
    hashed_password = password_manager.hash_password(data.password)
    print(f"   Password Hash: {hashed_password[:50]}...")
    
    # Create user with encrypted data (properties handle encryption)
    user = User(
        username=data.username,
        email=data.email,
        name=data.name,
        contact_no=data.contact_no,
        specialization=data.specialization,
        hashed_password=hashed_password,
        role=assigned_role,
        two_factor_enabled=True
    )
    
    print(f"   Encrypted Username: {user.username_encrypted[:50] if user.username_encrypted else 'FAILED'}...")
    print(f"   Encrypted Email: {user.email_encrypted[:50] if user.email_encrypted else 'FAILED'}...")
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"✓ Doctor registered successfully (ID: {user.id})\n")
    
    return UserResponse.from_orm(user)


@router.post("/register/patient", response_model=UserResponse)
async def register_patient(data: PatientRegister, db: Session = Depends(get_db)):
    """Register a new patient - all data encrypted"""
    
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check using hashed values
    email_hash = hash_for_search(data.email)
    username_hash = hash_for_search(data.username)
    
    print(f"\n📝 Registering Patient:")
    print(f"   Email: {data.email}")
    print(f"   Email Hash: {email_hash}")
    print(f"   Username: {data.username}")
    print(f"   Username Hash: {username_hash}")
    
    if db.query(User).filter(User.email_hash == email_hash).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if db.query(User).filter(User.username_hash == username_hash).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    assigned_role = get_role_for_registration(db)
    if assigned_role is None:
        assigned_role = "patient"
    
    hashed_password = password_manager.hash_password(data.password)
    print(f"   Password Hash: {hashed_password[:50]}...")
    
    # Create user with encrypted data (properties handle encryption)
    user = User(
        username=data.username,
        email=data.email,
        name=data.name,
        contact_no=data.contact_no,
        age=data.age,
        sex=data.sex,
        hashed_password=hashed_password,
        role=assigned_role,
        two_factor_enabled=True
    )
    
    print(f"   Encrypted Username: {user.username_encrypted[:50] if user.username_encrypted else 'FAILED'}...")
    print(f"   Encrypted Email: {user.email_encrypted[:50] if user.email_encrypted else 'FAILED'}...")
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"✓ Patient registered successfully (ID: {user.id})\n")
    
    return UserResponse.from_orm(user)


@router.post("/login", response_model=LoginResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login user - returns 2FA requirement if needed"""
    
    # Hash email for search using custom SHA256
    sha256 = SHA256()
    email_hash = sha256.hash_hex(data.email)
    user = db.query(User).filter(User.email_hash == email_hash).first()
    
    if not user or not password_manager.verify_password(data.password, user.hashed_password):
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
        
        # Send code via email (simulated for development)
        await email_service.send_2fa_code(user.email, code)
        
        return LoginResponse(
            requires_2fa=True,
            temp_token=temp_token
        )
    
    # Create access token
    access_token = jwt_manager.create_access_token(data={"sub": str(user.id)})
    
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