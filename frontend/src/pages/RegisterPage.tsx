import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import SphereLogo from '../components/SphereLogo';

type RegistrationType = 'doctor' | 'patient' | null;

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [registrationType, setRegistrationType] = useState<RegistrationType>(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    name: '',
    specialization: '',
    age: '',
    sex: '',
    contact_no: '',
    password: '',
    confirm_password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      setLoading(false);
      return;
    }

    try {
      if (registrationType === 'doctor') {
        await authService.registerDoctor({
          username: formData.username,
          email: formData.email,
          name: formData.name,
          specialization: formData.specialization,
          contact_no: formData.contact_no,
          password: formData.password,
          confirm_password: formData.confirm_password
        });
      } else if (registrationType === 'patient') {
        await authService.registerPatient({
          username: formData.username,
          email: formData.email,
          name: formData.name,
          age: parseInt(formData.age),
          sex: formData.sex,
          contact_no: formData.contact_no,
          password: formData.password,
          confirm_password: formData.confirm_password
        });
      }

      alert('Registration successful! Please login.');
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  // Type Selection Screen
  if (!registrationType) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-2xl p-8">
          <div className="flex justify-center mb-6">
            <SphereLogo className="w-20 h-20" />
          </div>
          
          <h2 className="text-3xl font-bold text-center text-gray-800 mb-2">
            Register
          </h2>
          <p className="text-center text-gray-600 mb-8">Choose your account type</p>
          
          <div className="space-y-4">
            <button
              onClick={() => setRegistrationType('doctor')}
              className="w-full py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold text-lg hover:from-indigo-700 hover:to-purple-700 transition shadow-md"
            >
              Register as Doctor
            </button>
            
            <button
              onClick={() => setRegistrationType('patient')}
              className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold text-lg hover:from-purple-700 hover:to-pink-700 transition shadow-md"
            >
              Register as Patient
            </button>
          </div>

          <button
            onClick={() => navigate('/')}
            className="mt-6 w-full text-gray-600 hover:text-gray-800 transition"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    );
  }

  // Registration Form
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-2xl p-8">
        <div className="flex justify-center mb-6">
          <SphereLogo className="w-16 h-16" />
        </div>
        
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-2">
          {registrationType === 'doctor' ? 'Doctor' : 'Patient'} Registration
        </h2>
        <p className="text-center text-gray-600 mb-6">Create your account</p>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter username"
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter email"
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">Full Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter full name"
            />
          </div>

          {registrationType === 'doctor' && (
            <div>
              <label className="block text-gray-700 text-sm font-medium mb-1">Specialization</label>
              <input
                type="text"
                name="specialization"
                value={formData.specialization}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="e.g., Cardiology"
              />
            </div>
          )}

          {registrationType === 'patient' && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 text-sm font-medium mb-1">Age</label>
                <input
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                  required
                  min="0"
                  max="150"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="Age"
                />
              </div>
              
              <div>
                <label className="block text-gray-700 text-sm font-medium mb-1">Sex</label>
                <select
                  name="sex"
                  value={formData.sex}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="">Select</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
          )}

          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">Contact Number</label>
            <input
              type="tel"
              name="contact_no"
              value={formData.contact_no}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter contact number"
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Minimum 8 characters"
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">Confirm Password</label>
            <input
              type="password"
              name="confirm_password"
              value={formData.confirm_password}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Re-enter password"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
          >
            {loading ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <div className="mt-6 text-center space-y-2">
          <button
            onClick={() => setRegistrationType(null)}
            className="text-indigo-600 hover:text-indigo-800 text-sm"
          >
            ← Change Account Type
          </button>
          <div className="text-gray-600 text-sm">
            Already have an account?{' '}
            <button
              onClick={() => navigate('/login')}
              className="text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Login
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;