import api from './api';

export interface Doctor {
  id: number;
  name: string;
  specialization: string | null;
}

export interface Appointment {
  id: number;
  patient_id: number;
  doctor_id: number;
  patient_name: string | null;
  doctor_name: string | null;
  doctor_specialization: string | null;
  appointment_date: string | null;
  appointment_time: string | null;
  reason: string | null;
  notes: string | null;
  status: string;
  integrity_verified: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface CreateAppointmentData {
  doctor_id: number;
  appointment_date: string;
  appointment_time: string;
  reason: string;
}

export interface UpdateAppointmentData {
  status?: string;
  notes?: string;
  appointment_date?: string;
  appointment_time?: string;
}

const appointmentService = {
  // Get list of all doctors
  async getDoctors(): Promise<Doctor[]> {
    const response = await api.get('/users/doctors');
    return response.data;
  },

  // Create a new appointment
  async createAppointment(data: CreateAppointmentData): Promise<Appointment> {
    const response = await api.post('/appointments', data);
    return response.data;
  },

  // Get all appointments for current user
  async getAppointments(): Promise<Appointment[]> {
    const response = await api.get('/appointments');
    return response.data;
  },

  // Get a specific appointment
  async getAppointment(id: number): Promise<Appointment> {
    const response = await api.get(`/appointments/${id}`);
    return response.data;
  },

  // Update an appointment
  async updateAppointment(id: number, data: UpdateAppointmentData): Promise<Appointment> {
    const response = await api.put(`/appointments/${id}`, data);
    return response.data;
  },

  // Cancel an appointment (patient)
  async cancelAppointment(id: number): Promise<Appointment> {
    const response = await api.put(`/appointments/${id}`, { status: 'cancelled' });
    return response.data;
  },

  // Confirm an appointment (doctor)
  async confirmAppointment(id: number): Promise<Appointment> {
    const response = await api.put(`/appointments/${id}`, { status: 'confirmed' });
    return response.data;
  },

  // Complete an appointment (doctor)
  async completeAppointment(id: number, notes?: string): Promise<Appointment> {
    const response = await api.put(`/appointments/${id}`, { 
      status: 'completed',
      notes: notes 
    });
    return response.data;
  },

  // Delete an appointment (admin only)
  async deleteAppointment(id: number): Promise<void> {
    await api.delete(`/appointments/${id}`);
  },
};

export default appointmentService;
