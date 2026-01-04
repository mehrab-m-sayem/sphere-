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
  two_factor_enabled: boolean;
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
  const [twoFactorLoading, setTwoFactorLoading] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

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

  const handleToggle2FA = async () => {
    if (!profile) return;
    
    setTwoFactorLoading(true);
    try {
      const newValue = !profile.two_factor_enabled;
      const response = await api.put('/users/me/2fa', { enabled: newValue });
      setProfile(response.data);
      alert(`Two-factor authentication ${newValue ? 'enabled' : 'disabled'} successfully`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update 2FA settings');
    } finally {
      setTwoFactorLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      alert('New passwords do not match');
      return;
    }
    if (passwordData.new_password.length < 8) {
      alert('New password must be at least 8 characters long');
      return;
    }
    
    setPasswordLoading(true);
    try {
      await api.put('/users/me/password', passwordData);
      alert('Password changed successfully');
      setShowPasswordModal(false);
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to change password');
    } finally {
      setPasswordLoading(false);
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
              {/* View Doctors - available to patients only */}
              {profile.role === 'patient' && (
                <>
                  <button
                    onClick={() => navigate('/doctors')}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-medium"
                  >
                    View Doctors
                  </button>
                  <button
                    onClick={() => navigate('/appointments')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-medium"
                  >
                    My Appointments
                  </button>
                  <button
                    onClick={() => navigate('/diagnoses')}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm font-medium"
                  >
                    My Diagnoses
                  </button>
                </>
              )}
              {profile.role === 'doctor' && (
                <>
                  <button
                    onClick={() => navigate('/appointments')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-medium"
                  >
                    My Appointments
                  </button>
                  <button
                    onClick={() => navigate('/diagnoses')}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm font-medium"
                  >
                    Diagnoses
                  </button>
                </>
              )}
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

                {/* Security Settings - 2FA Toggle */}
                <div className="pt-6 border-t">
                  <h3 className="text-sm font-semibold text-gray-700 mb-4">Security Settings</h3>
                  <div className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                    <div>
                      <label className="block text-sm font-medium text-gray-800">Two-Factor Authentication (2FA)</label>
                      <p className="text-xs text-gray-500 mt-1">
                        {profile.two_factor_enabled 
                          ? 'Email OTP verification is required during login' 
                          : 'Login without email OTP verification'}
                      </p>
                    </div>
                    <button
                      onClick={handleToggle2FA}
                      disabled={twoFactorLoading}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
                        profile.two_factor_enabled ? 'bg-indigo-600' : 'bg-gray-300'
                      } ${twoFactorLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          profile.two_factor_enabled ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                  
                  {/* Change Password Button */}
                  <div className="mt-4">
                    <button
                      onClick={() => setShowPasswordModal(true)}
                      className="px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-900 transition text-sm font-medium"
                    >
                      Change Password
                    </button>
                  </div>
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

      {/* Change Password Modal */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Change Password</h3>
            <p className="text-sm text-gray-500 mb-4">
              Password is secured using SHA256 with salt hashing
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
                <input
                  type="password"
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Enter current password"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                <input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Enter new password (min 8 characters)"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                <input
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Confirm new password"
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setShowPasswordModal(false);
                  setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
                }}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleChangePassword}
                disabled={passwordLoading || !passwordData.current_password || !passwordData.new_password || !passwordData.confirm_password}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {passwordLoading ? 'Changing...' : 'Change Password'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;