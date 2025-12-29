
from enum import Enum
from typing import List, Set
from functools import wraps
from fastapi import HTTPException, status


class Role(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"


class Permission(str, Enum):
    # User management
    VIEW_ALL_USERS = "view_all_users"
    EDIT_ALL_USERS = "edit_all_users"
    DELETE_USERS = "delete_users"
    
    # Profile management
    VIEW_OWN_PROFILE = "view_own_profile"
    EDIT_OWN_PROFILE = "edit_own_profile"
    VIEW_OTHER_PROFILES = "view_other_profiles"
    
    # Health records
    CREATE_HEALTH_RECORD = "create_health_record"
    VIEW_OWN_RECORDS = "view_own_records"
    EDIT_OWN_RECORDS = "edit_own_records"
    VIEW_PATIENT_RECORDS = "view_patient_records"
    EDIT_PATIENT_RECORDS = "edit_patient_records"
    DELETE_RECORDS = "delete_records"
    
    # System settings
    MANAGE_SYSTEM_SETTINGS = "manage_system_settings"
    VIEW_SYSTEM_LOGS = "view_system_logs"
    MANAGE_KEYS = "manage_keys"
    
    # Doctor-specific
    PRESCRIBE_MEDICATION = "prescribe_medication"
    VIEW_APPOINTMENTS = "view_appointments"
    MANAGE_APPOINTMENTS = "manage_appointments"


class RolePermissions:
    """Maps roles to their permissions"""
    
    PERMISSIONS = {
        Role.ADMIN: {
            # Full system access
            Permission.VIEW_ALL_USERS,
            Permission.EDIT_ALL_USERS,
            Permission.DELETE_USERS,
            Permission.VIEW_OWN_PROFILE,
            Permission.EDIT_OWN_PROFILE,
            Permission.VIEW_OTHER_PROFILES,
            Permission.VIEW_OWN_RECORDS,
            Permission.VIEW_PATIENT_RECORDS,
            Permission.DELETE_RECORDS,
            Permission.MANAGE_SYSTEM_SETTINGS,
            Permission.VIEW_SYSTEM_LOGS,
            Permission.MANAGE_KEYS,
        },
        
        Role.DOCTOR: {
            # Doctor permissions
            Permission.VIEW_OWN_PROFILE,
            Permission.EDIT_OWN_PROFILE,
            Permission.VIEW_OTHER_PROFILES,  # Can view patient profiles
            Permission.VIEW_OWN_RECORDS,
            Permission.VIEW_PATIENT_RECORDS,
            Permission.EDIT_PATIENT_RECORDS,
            Permission.CREATE_HEALTH_RECORD,
            Permission.PRESCRIBE_MEDICATION,
            Permission.VIEW_APPOINTMENTS,
            Permission.MANAGE_APPOINTMENTS,
        },
        
        Role.PATIENT: {
            # Patient permissions (limited)
            Permission.VIEW_OWN_PROFILE,
            Permission.EDIT_OWN_PROFILE,
            Permission.VIEW_OWN_RECORDS,
            Permission.EDIT_OWN_RECORDS,
            Permission.VIEW_APPOINTMENTS,
        }
    }
    
    @classmethod
    def get_permissions(cls, role: Role) -> Set[Permission]:
        """Get all permissions for a role"""
        return cls.PERMISSIONS.get(role, set())
    
    @classmethod
    def has_permission(cls, role: Role, permission: Permission) -> bool:
        """Check if role has specific permission"""
        return permission in cls.get_permissions(role)
    
    @classmethod
    def has_any_permission(cls, role: Role, permissions: List[Permission]) -> bool:
        """Check if role has any of the specified permissions"""
        role_permissions = cls.get_permissions(role)
        return any(perm in role_permissions for perm in permissions)
    
    @classmethod
    def has_all_permissions(cls, role: Role, permissions: List[Permission]) -> bool:
        """Check if role has all of the specified permissions"""
        role_permissions = cls.get_permissions(role)
        return all(perm in role_permissions for perm in permissions)


class AccessControl:
    """Handles access control checks"""
    
    @staticmethod
    def check_permission(user_role: str, required_permission: Permission) -> bool:
        """
        Check if user has required permission
        
        Args:
            user_role: User's role
            required_permission: Required permission
        
        Returns:
            True if user has permission
        """
        try:
            role = Role(user_role)
            return RolePermissions.has_permission(role, required_permission)
        except ValueError:
            return False
    
    @staticmethod
    def check_any_permission(user_role: str, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions"""
        try:
            role = Role(user_role)
            return RolePermissions.has_any_permission(role, permissions)
        except ValueError:
            return False
    
    @staticmethod
    def check_all_permissions(user_role: str, permissions: List[Permission]) -> bool:
        """Check if user has all specified permissions"""
        try:
            role = Role(user_role)
            return RolePermissions.has_all_permissions(role, permissions)
        except ValueError:
            return False
    
    @staticmethod
    def is_admin(user_role: str) -> bool:
        """Check if user is admin"""
        return user_role == Role.ADMIN.value
    
    @staticmethod
    def is_doctor(user_role: str) -> bool:
        """Check if user is doctor"""
        return user_role == Role.DOCTOR.value
    
    @staticmethod
    def is_patient(user_role: str) -> bool:
        """Check if user is patient"""
        return user_role == Role.PATIENT.value
    
    @staticmethod
    def can_access_user_data(requester_role: str, requester_id: str, target_id: str) -> bool:
        """
        Check if requester can access target user's data
        
        Args:
            requester_role: Role of user making request
            requester_id: ID of user making request
            target_id: ID of target user
        
        Returns:
            True if access allowed
        """
        # Admin can access all data
        if AccessControl.is_admin(requester_role):
            return True
        
        # Users can always access their own data
        if requester_id == target_id:
            return True
        
        # Doctors can access patient data (with proper authorization)
        if AccessControl.is_doctor(requester_role):
            return AccessControl.check_permission(
                requester_role, 
                Permission.VIEW_PATIENT_RECORDS
            )
        
        # Patients cannot access other users' data
        return False


def require_permission(permission: Permission):
    """
    Decorator to require specific permission for endpoint
    
    Usage:
        @require_permission(Permission.VIEW_ALL_USERS)
        def get_all_users():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            user_role = current_user.get('role')
            
            if not AccessControl.check_permission(user_role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_role(role: Role):
    """
    Decorator to require specific role for endpoint
    
    Usage:
        @require_role(Role.ADMIN)
        def admin_only_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            user_role = current_user.get('role')
            
            if user_role != role.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires {role.value} role"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def test_rbac():
    """Test RBAC system"""
    print("Testing Role-Based Access Control...")
    
    # Test permissions for each role
    print("\n1. Testing Admin permissions...")
    admin_perms = RolePermissions.get_permissions(Role.ADMIN)
    print(f"Admin has {len(admin_perms)} permissions")
    assert Permission.VIEW_ALL_USERS in admin_perms
    assert Permission.DELETE_USERS in admin_perms
    assert Permission.MANAGE_SYSTEM_SETTINGS in admin_perms
    print("✓ Admin permissions verified")
    
    print("\n2. Testing Doctor permissions...")
    doctor_perms = RolePermissions.get_permissions(Role.DOCTOR)
    print(f"Doctor has {len(doctor_perms)} permissions")
    assert Permission.VIEW_PATIENT_RECORDS in doctor_perms
    assert Permission.PRESCRIBE_MEDICATION in doctor_perms
    assert Permission.DELETE_USERS not in doctor_perms
    print("✓ Doctor permissions verified")
    
    print("\n3. Testing Patient permissions...")
    patient_perms = RolePermissions.get_permissions(Role.PATIENT)
    print(f"Patient has {len(patient_perms)} permissions")
    assert Permission.VIEW_OWN_PROFILE in patient_perms
    assert Permission.VIEW_OWN_RECORDS in patient_perms
    assert Permission.VIEW_PATIENT_RECORDS not in patient_perms
    print("✓ Patient permissions verified")
    
    # Test permission checks
    print("\n4. Testing permission checks...")
    ac = AccessControl()
    
    # Admin should be able to delete users
    can_delete = ac.check_permission(Role.ADMIN.value, Permission.DELETE_USERS)
    print(f"Admin can delete users: {can_delete}")
    assert can_delete
    
    # Patient should NOT be able to delete users
    patient_cant_delete = ac.check_permission(Role.PATIENT.value, Permission.DELETE_USERS)
    print(f"Patient can delete users: {patient_cant_delete}")
    assert not patient_cant_delete
    
    # Test data access
    print("\n5. Testing data access control...")
    
    # Admin accessing any user's data
    admin_access = ac.can_access_user_data(Role.ADMIN.value, "admin1", "patient1")
    print(f"Admin can access patient data: {admin_access}")
    assert admin_access
    
    # Patient accessing own data
    own_access = ac.can_access_user_data(Role.PATIENT.value, "patient1", "patient1")
    print(f"Patient can access own data: {own_access}")
    assert own_access
    
    # Patient accessing other patient's data
    other_access = ac.can_access_user_data(Role.PATIENT.value, "patient1", "patient2")
    print(f"Patient can access other patient data: {other_access}")
    assert not other_access
    
    # Doctor accessing patient data
    doctor_access = ac.can_access_user_data(Role.DOCTOR.value, "doctor1", "patient1")
    print(f"Doctor can access patient data: {doctor_access}")
    assert doctor_access
    
    print("\n✓ All RBAC tests passed!")


if __name__ == "__main__":
    test_rbac()