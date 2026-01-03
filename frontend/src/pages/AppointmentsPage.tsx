import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import appointmentService from '../services/appointmentService';
import type { Appointment } from '../services/appointmentService';
import SphereLogo from '../components/SphereLogo';
import { getUserRole } from '../utils/auth';

const AppointmentsPage: React.FC = () => {
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const userRole = getUserRole();

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const data = await appointmentService.getAppointments();
      setAppointments(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load appointments');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (id: number) => {
    if (!confirm('Are you sure you want to cancel this appointment?')) return;
    
    setActionLoading(id);
    try {
      await appointmentService.cancelAppointment(id);
      fetchAppointments();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to cancel appointment');
    } finally {
      setActionLoading(null);
    }
  };

  const handleConfirm = async (id: number) => {
    setActionLoading(id);
    try {
      await appointmentService.confirmAppointment(id);
      fetchAppointments();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to confirm appointment');
    } finally {
      setActionLoading(null);
    }
  };

  const handleComplete = async (id: number) => {
    const notes = prompt('Add any notes for this appointment (optional):');
    setActionLoading(id);
    try {
      await appointmentService.completeAppointment(id, notes || undefined);
      fetchAppointments();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to complete appointment');
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
    };
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  const formatTime = (timeStr: string | null) => {
    if (!timeStr) return 'N/A';
    try {
      const [hours, minutes] = timeStr.split(':');
      const hour = parseInt(hours);
      const ampm = hour >= 12 ? 'PM' : 'AM';
      const hour12 = hour % 12 || 12;
      return `${hour12}:${minutes} ${ampm}`;
    } catch {
      return timeStr;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <SphereLogo className="w-16 h-16 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading appointments...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <SphereLogo className="w-10 h-10" />
            <h1 className="text-2xl font-bold text-gray-800">My Appointments</h1>
          </div>
          <div className="flex gap-3">
            {userRole === 'patient' && (
              <button
                onClick={() => navigate('/doctors')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
              >
                + Book New
              </button>
            )}
            <button
              onClick={() => navigate('/profile')}
              className="px-4 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
            >
              Profile
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {appointments.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl shadow-sm">
            <div className="text-gray-400 text-6xl mb-4">📅</div>
            <h2 className="text-xl font-semibold text-gray-700 mb-2">No Appointments</h2>
            <p className="text-gray-500 mb-6">
              {userRole === 'patient' 
                ? "You haven't booked any appointments yet."
                : "You don't have any appointments scheduled."}
            </p>
            {userRole === 'patient' && (
              <button
                onClick={() => navigate('/doctors')}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
              >
                Find a Doctor
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {appointments.map((appointment) => (
              <div
                key={appointment.id}
                className={`bg-white rounded-xl shadow-sm p-6 border-l-4 ${
                  appointment.status === 'confirmed' ? 'border-blue-500' :
                  appointment.status === 'completed' ? 'border-green-500' :
                  appointment.status === 'cancelled' ? 'border-red-500' :
                  'border-yellow-500'
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  {/* Appointment Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {getStatusBadge(appointment.status)}
                      {!appointment.integrity_verified && (
                        <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
                          ⚠️ Integrity Warning
                        </span>
                      )}
                    </div>
                    
                    <h3 className="text-lg font-semibold text-gray-800">
                      {userRole === 'doctor' 
                        ? `Patient: ${appointment.patient_name || 'Unknown'}`
                        : `Dr. ${appointment.doctor_name || 'Unknown'}`
                      }
                    </h3>
                    
                    {userRole !== 'doctor' && appointment.doctor_specialization && (
                      <p className="text-indigo-600 text-sm">{appointment.doctor_specialization}</p>
                    )}
                    
                    <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Date:</span>
                        <span className="ml-2 font-medium">{formatDate(appointment.appointment_date)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Time:</span>
                        <span className="ml-2 font-medium">{formatTime(appointment.appointment_time)}</span>
                      </div>
                    </div>
                    
                    {appointment.reason && (
                      <div className="mt-3">
                        <span className="text-gray-500 text-sm">Reason:</span>
                        <p className="text-gray-700 text-sm mt-1">{appointment.reason}</p>
                      </div>
                    )}
                    
                    {appointment.notes && (
                      <div className="mt-3 bg-blue-50 p-3 rounded-lg">
                        <span className="text-blue-800 text-sm font-medium">Doctor's Notes:</span>
                        <p className="text-blue-700 text-sm mt-1">{appointment.notes}</p>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col gap-2">
                    {/* Patient actions */}
                    {userRole === 'patient' && appointment.status === 'pending' && (
                      <button
                        onClick={() => handleCancel(appointment.id)}
                        disabled={actionLoading === appointment.id}
                        className="px-4 py-2 text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition disabled:opacity-50"
                      >
                        {actionLoading === appointment.id ? 'Canceling...' : 'Cancel'}
                      </button>
                    )}
                    
                    {/* Doctor actions */}
                    {userRole === 'doctor' && appointment.status === 'pending' && (
                      <>
                        <button
                          onClick={() => handleConfirm(appointment.id)}
                          disabled={actionLoading === appointment.id}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                        >
                          {actionLoading === appointment.id ? 'Processing...' : 'Confirm'}
                        </button>
                        <button
                          onClick={() => handleCancel(appointment.id)}
                          disabled={actionLoading === appointment.id}
                          className="px-4 py-2 text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition disabled:opacity-50"
                        >
                          Decline
                        </button>
                      </>
                    )}
                    
                    {userRole === 'doctor' && appointment.status === 'confirmed' && (
                      <button
                        onClick={() => handleComplete(appointment.id)}
                        disabled={actionLoading === appointment.id}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50"
                      >
                        {actionLoading === appointment.id ? 'Processing...' : 'Mark Complete'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default AppointmentsPage;
