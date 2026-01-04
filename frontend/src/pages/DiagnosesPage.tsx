import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import diagnosisService from '../services/diagnosisService';
import type { Diagnosis } from '../services/diagnosisService';
import SphereLogo from '../components/SphereLogo';
import { getUserRole } from '../utils/auth';

const DiagnosesPage: React.FC = () => {
  const navigate = useNavigate();
  const [diagnoses, setDiagnoses] = useState<Diagnosis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const userRole = getUserRole();

  useEffect(() => {
    fetchDiagnoses();
  }, []);

  const fetchDiagnoses = async () => {
    try {
      const data = await diagnosisService.getDiagnoses();
      setDiagnoses(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load diagnoses');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <SphereLogo className="w-16 h-16 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading diagnoses...</p>
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
            <h1 className="text-2xl font-bold text-gray-800">
              {userRole === 'patient' ? 'My Medical Records' : 'Patient Diagnoses'}
            </h1>
          </div>
          <div className="flex gap-3">
            {userRole === 'doctor' && (
              <button
                onClick={() => navigate('/create-diagnosis')}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
              >
                + New Diagnosis
              </button>
            )}
            <button
              onClick={() => navigate('/appointments')}
              className="px-4 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
            >
              Appointments
            </button>
            <button
              onClick={() => navigate('/profile')}
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
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

        {diagnoses.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl shadow-sm">
            <div className="text-gray-400 text-6xl mb-4">📋</div>
            <h2 className="text-xl font-semibold text-gray-700 mb-2">No Diagnoses Found</h2>
            <p className="text-gray-500 mb-6">
              {userRole === 'doctor'
                ? "You haven't created any diagnoses yet."
                : "You don't have any medical records yet."}
            </p>
            {userRole === 'doctor' && (
              <button
                onClick={() => navigate('/create-diagnosis')}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
              >
                Create First Diagnosis
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {diagnoses.map((diagnosis) => (
              <div
                key={diagnosis.id}
                className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition cursor-pointer"
                onClick={() => navigate(`/diagnosis/${diagnosis.id}`)}
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs font-medium">
                        {formatDate(diagnosis.created_at)}
                      </span>
                      {!diagnosis.integrity_verified && (
                        <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
                          ⚠️ Integrity Warning
                        </span>
                      )}
                    </div>

                    <h3 className="text-lg font-semibold text-gray-800 mb-1">
                      {userRole === 'patient'
                        ? `By Dr. ${diagnosis.doctor_name || 'Unknown'}`
                        : `Patient: ${diagnosis.patient_name || 'Unknown'}`}
                    </h3>

                    <div className="mt-3">
                      <span className="text-gray-500 text-sm">Diagnosis:</span>
                      <p className="text-gray-800 font-medium mt-1 line-clamp-2">
                        {diagnosis.diagnosis || 'N/A'}
                      </p>
                    </div>

                    {diagnosis.prescription && (
                      <div className="mt-3">
                        <span className="text-gray-500 text-sm">Prescription:</span>
                        <p className="text-gray-700 text-sm mt-1 line-clamp-2">
                          {diagnosis.prescription}
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="flex-shrink-0">
                    <span className="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
                      View Details →
                    </span>
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

export default DiagnosesPage;
