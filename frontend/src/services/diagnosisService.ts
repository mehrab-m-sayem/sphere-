import api from './api';

export interface Patient {
  id: number;
  name: string;
  age: number | null;
  sex: string | null;
}

export interface Diagnosis {
  id: number;
  doctor_id: number;
  patient_id: number;
  appointment_id: number | null;
  doctor_name: string | null;
  patient_name: string | null;
  diagnosis: string | null;
  prescription: string | null;
  symptoms: string | null;
  notes: string | null;
  confidential_notes: string | null;
  integrity_verified: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface CreateDiagnosisData {
  patient_id: number;
  appointment_id?: number;
  diagnosis: string;
  prescription?: string;
  symptoms?: string;
  notes?: string;
  confidential_notes?: string;
}

export interface UpdateDiagnosisData {
  diagnosis?: string;
  prescription?: string;
  symptoms?: string;
  notes?: string;
  confidential_notes?: string;
}

const diagnosisService = {
  // Get list of all patients (for doctors)
  async getPatients(): Promise<Patient[]> {
    const response = await api.get('/diagnoses/patients');
    return response.data;
  },

  // Create a new diagnosis
  async createDiagnosis(data: CreateDiagnosisData): Promise<Diagnosis> {
    const response = await api.post('/diagnoses', data);
    return response.data;
  },

  // Get all diagnoses for current user
  async getDiagnoses(): Promise<Diagnosis[]> {
    const response = await api.get('/diagnoses');
    return response.data;
  },

  // Get diagnoses for a specific patient
  async getPatientDiagnoses(patientId: number): Promise<Diagnosis[]> {
    const response = await api.get(`/diagnoses/patient/${patientId}`);
    return response.data;
  },

  // Get a specific diagnosis
  async getDiagnosis(id: number): Promise<Diagnosis> {
    const response = await api.get(`/diagnoses/${id}`);
    return response.data;
  },

  // Update a diagnosis
  async updateDiagnosis(id: number, data: UpdateDiagnosisData): Promise<Diagnosis> {
    const response = await api.put(`/diagnoses/${id}`, data);
    return response.data;
  },

  // Delete a diagnosis (admin only)
  async deleteDiagnosis(id: number): Promise<void> {
    await api.delete(`/diagnoses/${id}`);
  },
};

export default diagnosisService;
