import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import SphereLogo from '../components/SphereLogo';
import { getUserRole } from '../utils/auth';

interface Doctor {
  id: number;
  name: string;
  specialization: string | null;
}

const DoctorsListPage: React.FC = () => {
  const navigate = useNavigate();
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const userRole = getUserRole();

  useEffect(() => {
    fetchDoctors();
  }, []);

  const fetchDoctors = async () => {
    try {
      const response = await api.get('/users/doctors');
      setDoctors(response.data);
    } catch (err: any) {
      console.error('Error fetching doctors:', err);
      console.error('Response:', err.response);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load doctors list';
      setError(`${errorMsg} (Status: ${err.response?.status || 'unknown'})`);
    } finally {
      setLoading(false);
    }
  };

  const filteredDoctors = doctors.filter(doctor => {
    const searchLower = searchTerm.toLowerCase();
    return (
      doctor.name?.toLowerCase().includes(searchLower) ||
      doctor.specialization?.toLowerCase().includes(searchLower)
    );
  });

  // Group doctors by specialization
  const doctorsBySpecialization = filteredDoctors.reduce((acc, doctor) => {
    const spec = doctor.specialization || 'General';
    if (!acc[spec]) {
      acc[spec] = [];
    }
    acc[spec].push(doctor);
    return acc;
  }, {} as Record<string, Doctor[]>);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <SphereLogo className="w-16 h-16 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading doctors...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <SphereLogo className="w-10 h-10" />
              <div>
                <h1 className="text-2xl font-bold text-gray-800">SPHERE</h1>
                <p className="text-xs text-gray-500">Health Record System</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/appointments')}
                className="px-4 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition text-sm font-medium"
              >
                My Appointments
              </button>
              <button
                onClick={() => navigate('/profile')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-medium"
              >
                My Profile
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Title and Search */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-2">Our Doctors</h2>
            <p className="text-gray-600 mb-6">
              Find the right specialist for your healthcare needs
            </p>
            
            {/* Search Bar */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search by name or specialization..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
              <svg
                className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Doctors List */}
          {filteredDoctors.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-8 text-center">
              <div className="text-gray-400 mb-4">
                <svg
                  className="w-16 h-16 mx-auto"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">
                {searchTerm ? 'No doctors found' : 'No doctors registered yet'}
              </h3>
              <p className="text-gray-500">
                {searchTerm
                  ? 'Try adjusting your search terms'
                  : 'Check back later for available doctors'}
              </p>
            </div>
          ) : (
            <div className="space-y-8">
              {Object.entries(doctorsBySpecialization)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([specialization, specDoctors]) => (
                  <div key={specialization}>
                    <h3 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
                      <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                      {specialization}
                      <span className="text-sm font-normal text-gray-400">
                        ({specDoctors.length} {specDoctors.length === 1 ? 'doctor' : 'doctors'})
                      </span>
                    </h3>
                    <div className="grid gap-4 md:grid-cols-2">
                      {specDoctors.map((doctor) => (
                        <div
                          key={doctor.id}
                          className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow border border-gray-100"
                        >
                          <div className="flex items-start gap-4">
                            <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0">
                              <svg
                                className="w-6 h-6 text-indigo-600"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                                />
                              </svg>
                            </div>
                            <div className="flex-1 min-w-0">
                              <h4 className="text-lg font-semibold text-gray-800 truncate">
                                Dr. {doctor.name}
                              </h4>
                              <p className="text-indigo-600 text-sm font-medium">
                                {doctor.specialization || 'General Practitioner'}
                              </p>
                              {userRole === 'patient' && (
                                <button
                                  onClick={() => navigate(`/book-appointment/${doctor.id}`)}
                                  className="mt-3 px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition"
                                >
                                  Book Appointment
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
            </div>
          )}

          {/* Summary */}
          {filteredDoctors.length > 0 && (
            <div className="mt-8 text-center text-gray-500 text-sm">
              Showing {filteredDoctors.length} of {doctors.length} doctors
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DoctorsListPage;
