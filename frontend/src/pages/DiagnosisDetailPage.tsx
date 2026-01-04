import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import diagnosisService from '../services/diagnosisService';
import type { Diagnosis } from '../services/diagnosisService';
import SphereLogo from '../components/SphereLogo';
import { getUserRole } from '../utils/auth';

const DiagnosisDetailPage: React.FC = () => {
  const navigate = useNavigate();
  const { diagnosisId } = useParams<{ diagnosisId: string }>();
  const userRole = getUserRole();

  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  const [editData, setEditData] = useState({
    diagnosis: '',
    prescription: '',
    symptoms: '',
    notes: '',
    confidential_notes: '',
  });

  useEffect(() => {
    fetchDiagnosis();
  }, [diagnosisId]);

  const fetchDiagnosis = async () => {
    try {
      const data = await diagnosisService.getDiagnosis(parseInt(diagnosisId || '0'));
      setDiagnosis(data);
      setEditData({
        diagnosis: data.diagnosis || '',
        prescription: data.prescription || '',
        symptoms: data.symptoms || '',
        notes: data.notes || '',
        confidential_notes: data.confidential_notes || '',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load diagnosis');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await diagnosisService.updateDiagnosis(parseInt(diagnosisId || '0'), {
        diagnosis: editData.diagnosis,
        prescription: editData.prescription || undefined,
        symptoms: editData.symptoms || undefined,
        notes: editData.notes || undefined,
        confidential_notes: editData.confidential_notes || undefined,
      });
      await fetchDiagnosis();
      setIsEditing(false);
      alert('Diagnosis updated successfully!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update diagnosis');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setEditData({
      ...editData,
      [e.target.name]: e.target.value,
    });
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <SphereLogo className="w-16 h-16 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading diagnosis...</p>
        </div>
      </div>
    );
  }

  if (error || !diagnosis) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Diagnosis not found'}</p>
          <button
            onClick={() => navigate('/diagnoses')}
            className="text-indigo-600 hover:text-indigo-800"
          >
            ← Back to Diagnoses
          </button>
        </div>
      </div>
    );
  }

  const canEdit = userRole === 'doctor' || userRole === 'admin';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <SphereLogo className="w-10 h-10" />
            <h1 className="text-2xl font-bold text-gray-800">Diagnosis Details</h1>
          </div>
          <div className="flex gap-3">
            {canEdit && !isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
              >
                Edit Diagnosis
              </button>
            )}
            <button
              onClick={() => navigate('/diagnoses')}
              className="px-4 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
            >
              ← Back
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Status Banner */}
        {!diagnosis.integrity_verified && (
          <div className="bg-red-50 border border-red-300 text-red-800 px-4 py-3 rounded-lg mb-6 flex items-center gap-2">
            <span className="text-xl">⚠️</span>
            <div>
              <p className="font-semibold">Data Integrity Warning</p>
              <p className="text-sm">
                The HMAC verification failed. This data may have been tampered with.
              </p>
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          {/* Header Info */}
          <div className="bg-gradient-to-r from-indigo-500 to-purple-500 p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-indigo-100 text-sm">
                  {userRole === 'patient' ? 'Diagnosed by' : 'Patient'}
                </p>
                <h2 className="text-2xl font-bold">
                  {userRole === 'patient'
                    ? `Dr. ${diagnosis.doctor_name || 'Unknown'}`
                    : diagnosis.patient_name || 'Unknown'}
                </h2>
              </div>
              <div className="text-right">
                <p className="text-indigo-100 text-sm">Date</p>
                <p className="font-medium">{formatDate(diagnosis.created_at)}</p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Symptoms */}
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-2">
                Symptoms
                <span className="text-xs text-blue-500 ml-2">(ECC Encrypted)</span>
              </label>
              {isEditing ? (
                <textarea
                  name="symptoms"
                  value={editData.symptoms}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                />
              ) : (
                <p className="text-gray-800 bg-gray-50 p-4 rounded-lg">
                  {diagnosis.symptoms || 'No symptoms recorded'}
                </p>
              )}
            </div>

            {/* Diagnosis */}
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-2">
                Diagnosis
                <span className="text-xs text-green-600 ml-2">(RSA Encrypted)</span>
              </label>
              {isEditing ? (
                <textarea
                  name="diagnosis"
                  value={editData.diagnosis}
                  onChange={handleChange}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                />
              ) : (
                <p className="text-gray-800 bg-green-50 p-4 rounded-lg font-medium">
                  {diagnosis.diagnosis || 'No diagnosis recorded'}
                </p>
              )}
            </div>

            {/* Prescription */}
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-2">
                Prescription
                <span className="text-xs text-green-600 ml-2">(RSA Encrypted)</span>
              </label>
              {isEditing ? (
                <textarea
                  name="prescription"
                  value={editData.prescription}
                  onChange={handleChange}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                />
              ) : (
                <div className="bg-blue-50 p-4 rounded-lg">
                  {diagnosis.prescription ? (
                    <p className="text-gray-800 whitespace-pre-wrap">{diagnosis.prescription}</p>
                  ) : (
                    <p className="text-gray-500 italic">No prescription provided</p>
                  )}
                </div>
              )}
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-2">
                Additional Notes
                <span className="text-xs text-blue-500 ml-2">(ECC Encrypted)</span>
              </label>
              {isEditing ? (
                <textarea
                  name="notes"
                  value={editData.notes}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                />
              ) : (
                <p className="text-gray-800 bg-gray-50 p-4 rounded-lg">
                  {diagnosis.notes || 'No additional notes'}
                </p>
              )}
            </div>

            {/* Confidential Notes (only visible to doctors) */}
            {(userRole === 'doctor' || userRole === 'admin') && (
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-2">
                  Confidential Notes
                  <span className="text-xs text-purple-600 ml-2">(Multi-Level: RSA + ECC)</span>
                </label>
                {isEditing ? (
                  <textarea
                    name="confidential_notes"
                    value={editData.confidential_notes}
                    onChange={handleChange}
                    rows={3}
                    className="w-full px-4 py-3 border border-purple-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none bg-purple-50"
                  />
                ) : (
                  <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg">
                    {diagnosis.confidential_notes ? (
                      <p className="text-gray-800 whitespace-pre-wrap">
                        {diagnosis.confidential_notes}
                      </p>
                    ) : (
                      <p className="text-gray-500 italic">No confidential notes</p>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Edit Buttons */}
            {isEditing && (
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex-1 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setEditData({
                      diagnosis: diagnosis.diagnosis || '',
                      prescription: diagnosis.prescription || '',
                      symptoms: diagnosis.symptoms || '',
                      notes: diagnosis.notes || '',
                      confidential_notes: diagnosis.confidential_notes || '',
                    });
                  }}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
                >
                  Cancel
                </button>
              </div>
            )}

            {/* Security Info */}
            <div className="bg-gray-50 border rounded-lg p-4 mt-6">
              <div className="flex items-center gap-2 text-gray-600">
                <span>🔐</span>
                <span className="text-sm">
                  This medical record is encrypted and integrity-verified using HMAC
                </span>
                {diagnosis.integrity_verified && (
                  <span className="text-green-600 text-sm ml-auto">✓ Verified</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DiagnosisDetailPage;
