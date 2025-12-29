import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { logout, getUserRole } from '../utils/auth';
import SphereLogo from '../components/SphereLogo';

interface UserProfile {
  id: number;
  username: string;
  email: string;
  name: string;
  contact_no: string;
  role: string;
  specialization?: string;
  age?: number;
  sex?: string;
  created_at: string;
  last_login?: string;
}

const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saveLoading, setSaveLoading] = useState(false);

  const [editData, setEditData] = useState({
    name: '',
    contact_no: ''
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/users/me');
      setProfile(response.data);
      setEditData({
        name: response.data.name,
        contact_no: response.data.contact_no
      });
    } catch (err) {
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    setSaveLoading(true);
    try {
      await api.put('/users/me', editData);
      setIsEditing(false);
      fetchProfile();
      alert('Profile updated successfully');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaveLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <SphereLogo className="w-16 h-16 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Profile not found'}</p>
          <button
            onClick={() => navigate('/')}
            className="text-indigo-600 hover:text-indigo-800"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  const isDoctor = profile.role === 'doctor';
  const isPatient = profile.role === 'patient';
  const roleLabel = profile.role.charAt(0).toUpperCase() + profile.role.slice(1);

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
              {profile.role === 'admin' && (
                <button
                  onClick={() => navigate('/admin')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-medium"
                >
                  View Registered Users
                </button>
              )}
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Profile Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-xl shadow-sm p-8">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-800">My Profile</h2>
                <p className="text-sm text-gray-500 mt-1">
                  {roleLabel} Account
                </p>
              </div>
              {!isEditing ? (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-medium"
                >
                  Edit Profile
                </button>
              ) : (
                <div className="flex gap-2">
                  <button
                    onClick={() => setIsEditing(false)}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition text-sm font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleUpdate}
                    disabled={saveLoading}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-medium disabled:opacity-50"
                  >
                    {saveLoading ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              )}
            </div>

            {!isEditing ? (
              // View Mode - Show only relevant fields based on role
              <div className="space-y-6">
                {/* Common Fields for All Users */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Username</label>
                    <p className="text-gray-800 font-medium">{profile.username}</p>
                  </div>
                  
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Email</label>
                    <p className="text-gray-800 font-medium">{profile.email}</p>
                  </div>
                  
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Full Name</label>
                    <p className="text-gray-800 font-medium">{profile.name}</p>
                  </div>
                  
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Contact Number</label>
                    <p className="text-gray-800 font-medium">{profile.contact_no}</p>
                  </div>
                </div>

                {/* Doctor-Specific Fields */}
                {isDoctor && profile.specialization && (
                  <div className="pt-6 border-t">
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">Specialization</label>
                      <p className="text-gray-800 font-medium">{profile.specialization}</p>
                    </div>
                  </div>
                )}

                {/* Patient-Specific Fields */}
                {isPatient && (
                  <div className="pt-6 border-t">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {profile.age !== undefined && (
                        <div>
                          <label className="block text-xs font-medium text-gray-500 mb-1">Age</label>
                          <p className="text-gray-800 font-medium">{profile.age} years</p>
                        </div>
                      )}

                      {profile.sex && (
                        <div>
                          <label className="block text-xs font-medium text-gray-500 mb-1">Sex</label>
                          <p className="text-gray-800 font-medium">{profile.sex}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Membership Info */}
                <div className="pt-6 border-t">
                  <label className="block text-xs font-medium text-gray-500 mb-1">Member Since</label>
                  <p className="text-gray-800">
                    {new Date(profile.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                </div>
              </div>
            ) : (
              // Edit Mode - Only allow editing name and contact_no
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  <input
                    type="text"
                    value={editData.name}
                    onChange={(e) => setEditData({...editData, name: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Contact Number</label>
                  <input
                    type="tel"
                    value={editData.contact_no}
                    onChange={(e) => setEditData({...editData, contact_no: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;