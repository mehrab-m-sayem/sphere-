"""
Appointments Router for SPHERE
Handles appointment booking, viewing, and management
All data is encrypted using RSA/ECC and verified with HMAC
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Appointment
from app.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


def build_appointment_response(appointment: Appointment, db: Session) -> AppointmentResponse:
    """
    Build appointment response with decrypted data and integrity verification
    """
    # Get patient and doctor info
    patient = db.query(User).filter(User.id == appointment.patient_id).first()
    doctor = db.query(User).filter(User.id == appointment.doctor_id).first()
    
    return AppointmentResponse(
        id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        patient_name=patient.name if patient else None,
        doctor_name=doctor.name if doctor else None,
        doctor_specialization=doctor.specialization if doctor else None,
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        reason=appointment.reason,
        notes=appointment.notes,
        status=appointment.status,
        integrity_verified=appointment.verify_integrity(),
        created_at=appointment.created_at,
        updated_at=appointment.updated_at
    )


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new appointment (Patient only)
    - Encrypts reason with RSA
    - Encrypts date/time with ECC
    - Generates HMAC for integrity verification
    """
    # Only patients can book appointments
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can book appointments"
        )
    
    # Verify the doctor exists and is active
    doctor = db.query(User).filter(
        User.id == appointment_data.doctor_id,
        User.role == "doctor",
        User.is_active == True
    ).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Create appointment with encrypted fields
    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=appointment_data.doctor_id,
        status="pending"
    )
    
    # Set encrypted fields (encryption happens in setters)
    appointment.reason = appointment_data.reason
    appointment.appointment_date = appointment_data.appointment_date
    appointment.appointment_time = appointment_data.appointment_time
    
    # Compute HMAC for data integrity
    appointment.data_hmac = Appointment.compute_hmac(
        current_user.id,
        appointment_data.doctor_id,
        appointment_data.reason,
        appointment_data.appointment_date,
        appointment_data.appointment_time
    )
    
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    print(f"✅ Appointment created: Patient {current_user.id} -> Doctor {doctor.id}")
    
    return build_appointment_response(appointment, db)


@router.get("", response_model=List[AppointmentResponse])
async def get_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all appointments for current user
    - Patients see their own appointments
    - Doctors see appointments made with them
    - Admins see all appointments
    """
    if current_user.role == "admin":
        appointments = db.query(Appointment).all()
    elif current_user.role == "doctor":
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == current_user.id
        ).all()
    else:  # patient
        appointments = db.query(Appointment).filter(
            Appointment.patient_id == current_user.id
        ).all()
    
    return [build_appointment_response(apt, db) for apt in appointments]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific appointment by ID
    User must be the patient, doctor, or admin
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check access permissions (RBAC)
    if current_user.role != "admin":
        if current_user.id != appointment.patient_id and current_user.id != appointment.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this appointment"
            )
    
    return build_appointment_response(appointment, db)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    update_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an appointment
    - Patients can cancel or reschedule their appointments
    - Doctors can confirm, complete, or add notes
    - Admins can do everything
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check permissions based on role (RBAC)
    is_patient = current_user.id == appointment.patient_id
    is_doctor = current_user.id == appointment.doctor_id
    is_admin = current_user.role == "admin"
    
    if not (is_patient or is_doctor or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this appointment"
        )
    
    # Track if we need to recompute HMAC
    recompute_hmac = False
    new_reason = appointment.reason
    new_date = appointment.appointment_date
    new_time = appointment.appointment_time
    
    # Handle status updates
    if update_data.status:
        allowed_statuses = ["pending", "confirmed", "completed", "cancelled"]
        if update_data.status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {allowed_statuses}"
            )
        
        # Patients can only cancel
        if is_patient and not is_admin:
            if update_data.status != "cancelled":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Patients can only cancel appointments"
                )
        
        appointment.status = update_data.status
    
    # Handle notes (doctors and admins only)
    if update_data.notes is not None:
        if not (is_doctor or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only doctors can add notes"
            )
        appointment.notes = update_data.notes
    
    # Handle date/time updates (patient reschedule or admin)
    if update_data.appointment_date:
        if not (is_patient or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only patients can reschedule"
            )
        appointment.appointment_date = update_data.appointment_date
        new_date = update_data.appointment_date
        recompute_hmac = True
        # Reset status to pending when rescheduling
        appointment.status = "pending"
    
    if update_data.appointment_time:
        if not (is_patient or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only patients can reschedule"
            )
        appointment.appointment_time = update_data.appointment_time
        new_time = update_data.appointment_time
        recompute_hmac = True
        appointment.status = "pending"
    
    # Recompute HMAC if critical data changed
    if recompute_hmac:
        appointment.data_hmac = Appointment.compute_hmac(
            appointment.patient_id,
            appointment.doctor_id,
            new_reason,
            new_date,
            new_time
        )
    
    db.commit()
    db.refresh(appointment)
    
    print(f"✅ Appointment {appointment_id} updated by user {current_user.id}")
    
    return build_appointment_response(appointment, db)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an appointment (Admin only, or patient can cancel)
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Only admin can fully delete, patients should cancel instead
    if current_user.role != "admin":
        if current_user.id == appointment.patient_id:
            # Patients cancel instead of delete
            appointment.status = "cancelled"
            db.commit()
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete appointments"
        )
    
    db.delete(appointment)
    db.commit()
    
    print(f"🗑️ Appointment {appointment_id} deleted by admin {current_user.id}")
