"""
Diagnoses Router for SPHERE
Handles diagnosis creation, viewing, and management by doctors
All data is encrypted using RSA/ECC with multi-level encryption for sensitive data
HMAC ensures data integrity
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Diagnosis, Appointment
from app.schemas import DiagnosisCreate, DiagnosisUpdate, DiagnosisResponse, PatientListItem
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/diagnoses", tags=["diagnoses"])


def build_diagnosis_response(diagnosis: Diagnosis, db: Session) -> DiagnosisResponse:
    """
    Build diagnosis response with decrypted data and integrity verification
    """
    # Get doctor and patient info
    doctor = db.query(User).filter(User.id == diagnosis.doctor_id).first()
    patient = db.query(User).filter(User.id == diagnosis.patient_id).first()
    
    return DiagnosisResponse(
        id=diagnosis.id,
        doctor_id=diagnosis.doctor_id,
        patient_id=diagnosis.patient_id,
        appointment_id=diagnosis.appointment_id,
        doctor_name=doctor.name if doctor else None,
        patient_name=patient.name if patient else None,
        diagnosis=diagnosis.diagnosis,
        prescription=diagnosis.prescription,
        symptoms=diagnosis.symptoms,
        notes=diagnosis.notes,
        confidential_notes=diagnosis.confidential_notes,
        integrity_verified=diagnosis.verify_integrity(),
        created_at=diagnosis.created_at,
        updated_at=diagnosis.updated_at
    )


@router.get("/patients", response_model=List[PatientListItem])
async def get_patients_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get list of all patients (Doctor only)
    Used for selecting a patient when creating a diagnosis
    """
    if current_user.role != "doctor" and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view patient list"
        )
    
    patients = db.query(User).filter(
        User.role == "patient",
        User.is_active == True
    ).all()
    
    return [
        PatientListItem(
            id=patient.id,
            name=patient.name,
            age=patient.age,
            sex=patient.sex
        )
        for patient in patients
    ]


@router.post("", response_model=DiagnosisResponse, status_code=status.HTTP_201_CREATED)
async def create_diagnosis(
    diagnosis_data: DiagnosisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new diagnosis (Doctor only)
    - Encrypts diagnosis and prescription with RSA
    - Encrypts symptoms and notes with ECC
    - Encrypts confidential_notes with multi-level encryption (RSA + ECC)
    - Generates HMAC for integrity verification
    """
    # Only doctors can create diagnoses (RBAC)
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create diagnoses"
        )
    
    # Verify the patient exists
    patient = db.query(User).filter(
        User.id == diagnosis_data.patient_id,
        User.role == "patient",
        User.is_active == True
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Verify appointment if provided
    if diagnosis_data.appointment_id:
        appointment = db.query(Appointment).filter(
            Appointment.id == diagnosis_data.appointment_id,
            Appointment.doctor_id == current_user.id,
            Appointment.patient_id == diagnosis_data.patient_id
        ).first()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found or doesn't match doctor/patient"
            )
    
    # Create diagnosis with encrypted fields
    diagnosis = Diagnosis(
        doctor_id=current_user.id,
        patient_id=diagnosis_data.patient_id,
        appointment_id=diagnosis_data.appointment_id
    )
    
    # Set encrypted fields (encryption happens in setters)
    diagnosis.diagnosis = diagnosis_data.diagnosis
    
    if diagnosis_data.prescription:
        diagnosis.prescription = diagnosis_data.prescription
    
    if diagnosis_data.symptoms:
        diagnosis.symptoms = diagnosis_data.symptoms
    
    if diagnosis_data.notes:
        diagnosis.notes = diagnosis_data.notes
    
    # Multi-level encryption for confidential notes
    if diagnosis_data.confidential_notes:
        diagnosis.confidential_notes = diagnosis_data.confidential_notes
    
    # Compute HMAC for data integrity
    diagnosis.data_hmac = Diagnosis.compute_hmac(
        current_user.id,
        diagnosis_data.patient_id,
        diagnosis_data.diagnosis,
        diagnosis_data.prescription or ""
    )
    
    db.add(diagnosis)
    db.commit()
    db.refresh(diagnosis)
    
    print(f"✅ Diagnosis created by Dr. {current_user.id} for patient {patient.id}")
    
    return build_diagnosis_response(diagnosis, db)


@router.get("", response_model=List[DiagnosisResponse])
async def get_diagnoses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get diagnoses based on user role (RBAC)
    - Patients see their own diagnoses
    - Doctors see diagnoses they created
    - Admins see all diagnoses
    """
    if current_user.role == "admin":
        diagnoses = db.query(Diagnosis).all()
    elif current_user.role == "doctor":
        diagnoses = db.query(Diagnosis).filter(
            Diagnosis.doctor_id == current_user.id
        ).all()
    else:  # patient
        diagnoses = db.query(Diagnosis).filter(
            Diagnosis.patient_id == current_user.id
        ).all()
    
    return [build_diagnosis_response(d, db) for d in diagnoses]


@router.get("/patient/{patient_id}", response_model=List[DiagnosisResponse])
async def get_patient_diagnoses(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all diagnoses for a specific patient
    - Patients can only view their own
    - Doctors and admins can view any patient's diagnoses
    """
    # RBAC check
    if current_user.role == "patient" and current_user.id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own diagnoses"
        )
    
    diagnoses = db.query(Diagnosis).filter(
        Diagnosis.patient_id == patient_id
    ).all()
    
    return [build_diagnosis_response(d, db) for d in diagnoses]


@router.get("/{diagnosis_id}", response_model=DiagnosisResponse)
async def get_diagnosis(
    diagnosis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific diagnosis by ID
    User must be the patient, the doctor who created it, or admin
    """
    diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
    
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found"
        )
    
    # RBAC check
    if current_user.role != "admin":
        if current_user.id != diagnosis.patient_id and current_user.id != diagnosis.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this diagnosis"
            )
    
    return build_diagnosis_response(diagnosis, db)


@router.put("/{diagnosis_id}", response_model=DiagnosisResponse)
async def update_diagnosis(
    diagnosis_id: int,
    update_data: DiagnosisUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a diagnosis (Doctor who created it or Admin only)
    """
    diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
    
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found"
        )
    
    # RBAC: Only the doctor who created it or admin can update
    if current_user.role != "admin" and current_user.id != diagnosis.doctor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the doctor who created this diagnosis can update it"
        )
    
    # Track changes for HMAC recomputation
    new_diagnosis = diagnosis.diagnosis
    new_prescription = diagnosis.prescription or ""
    recompute_hmac = False
    
    # Update fields
    if update_data.diagnosis is not None:
        diagnosis.diagnosis = update_data.diagnosis
        new_diagnosis = update_data.diagnosis
        recompute_hmac = True
    
    if update_data.prescription is not None:
        diagnosis.prescription = update_data.prescription
        new_prescription = update_data.prescription
        recompute_hmac = True
    
    if update_data.symptoms is not None:
        diagnosis.symptoms = update_data.symptoms
    
    if update_data.notes is not None:
        diagnosis.notes = update_data.notes
    
    if update_data.confidential_notes is not None:
        diagnosis.confidential_notes = update_data.confidential_notes
    
    # Recompute HMAC if critical data changed
    if recompute_hmac:
        diagnosis.data_hmac = Diagnosis.compute_hmac(
            diagnosis.doctor_id,
            diagnosis.patient_id,
            new_diagnosis,
            new_prescription
        )
    
    db.commit()
    db.refresh(diagnosis)
    
    print(f"✅ Diagnosis {diagnosis_id} updated by user {current_user.id}")
    
    return build_diagnosis_response(diagnosis, db)


@router.delete("/{diagnosis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diagnosis(
    diagnosis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a diagnosis (Admin only for audit purposes)
    Doctors can update but not delete diagnoses
    """
    diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
    
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found"
        )
    
    # Only admin can delete (RBAC - medical records should be preserved)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete diagnosis records"
        )
    
    db.delete(diagnosis)
    db.commit()
    
    print(f"🗑️ Diagnosis {diagnosis_id} deleted by admin {current_user.id}")
