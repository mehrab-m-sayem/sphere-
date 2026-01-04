import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import diagnosisService from '../services/diagnosisService';
import type { Patient } from '../services/diagnosisService';
import SphereLogo from '../components/SphereLogo';

const CreateDiagnosisPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preselectedPatientId = searchParams.get('patient');
  const appointmentId = searchParams.get('appointment');

  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState({
    patient_id: preselectedPatientId || '',
    diagnosis: '',
    prescription: '',
    symptoms: '',
    notes: '',
    confidential_notes: '',
  });

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const data = await diagnosisService.getPatients();
      setPatients(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load patients');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      await diagnosisService.createDiagnosis({
        patient_id: parseInt(formData.patient_id),
        appointment_id: appointmentId ? parseInt(appointmentId) : undefined,
        diagnosis: formData.diagnosis,
        prescription: formData.prescription || undefined,
        symptoms: formData.symptoms || undefined,
        notes: formData.notes || undefined,
        confidential_notes: formData.confidential_notes || undefined,
      });
      setSuccess(true);
      setTimeout(() => {
        navigate('/diagnoses');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create diagnosis');
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <SphereLogo className="w-16 h-16 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-xl shadow-lg max-w-md">
          <div className="text-green-500 text-6xl mb-4">✓</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Diagnosis Created!</h2>
          <p className="text-gray-600 mb-4">
            The diagnosis has been securely encrypted and saved.
          </p>
          <p className="text-sm text-gray-500">Redirecting to diagnoses list...</p>
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
            <h1 className="text-2xl font-bold text-gray-800">Create Diagnosis</h1>
          </div>
          <button
            onClick={() => navigate('/diagnoses')}
            className="px-4 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
          >
            ← Back to Diagnoses
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-md p-6 space-y-6">
          {/* Patient Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Patient *
            </label>
            <select
              name="patient_id"
              value={formData.patient_id}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">-- Select a patient --</option>
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.name} {patient.age ? `(${patient.age} yrs)` : ''} {patient.sex ? `- ${patient.sex}` : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Symptoms */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Symptoms
              <span className="text-xs text-gray-500 ml-2">(ECC Encrypted)</span>
            </label>
            <textarea
              name="symptoms"
              value={formData.symptoms}
              onChange={handleChange}
              rows={3}
              placeholder="Describe the patient's symptoms..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />
          </div>

          {/* Diagnosis */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Diagnosis *
              <span className="text-xs text-gray-500 ml-2">(RSA Encrypted)</span>
            </label>
            <textarea
              name="diagnosis"
              value={formData.diagnosis}
              onChange={handleChange}
              required
              rows={4}
              placeholder="Enter the diagnosis..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />
          </div>

          {/* Prescription */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Prescription
              <span className="text-xs text-gray-500 ml-2">(RSA Encrypted)</span>
            </label>
            <textarea
              name="prescription"
              value={formData.prescription}
              onChange={handleChange}
              rows={4}
              placeholder="Enter medications and treatment plan..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Notes
              <span className="text-xs text-gray-500 ml-2">(ECC Encrypted)</span>
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              placeholder="Any additional notes..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />
          </div>

          {/* Confidential Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confidential Notes
              <span className="text-xs text-purple-600 ml-2">(Multi-Level: RSA + ECC Encrypted)</span>
            </label>
            <textarea
              name="confidential_notes"
              value={formData.confidential_notes}
              onChange={handleChange}
              rows={3}
              placeholder="Highly sensitive information (double encrypted)..."
              className="w-full px-4 py-3 border border-purple-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none bg-purple-50"
            />
          </div>

          {/* Security Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <span className="text-blue-500 text-xl">🔒</span>
              <div>
                <p className="text-sm text-blue-800 font-medium">End-to-End Encryption</p>
                <p className="text-xs text-blue-600 mt-1">
                  All medical data is encrypted using RSA and ECC algorithms before storage.
                  Confidential notes use multi-level encryption (RSA + ECC).
                  Data integrity is verified using HMAC.
                </p>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Creating Diagnosis...' : 'Create Diagnosis'}
          </button>
        </form>
      </main>
    </div>
  );
};

export default CreateDiagnosisPage;
