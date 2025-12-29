import React from 'react';
import { useNavigate } from 'react-router-dom';
import { isAuthenticated } from '../utils/auth';
import SphereLogo from '../components/SphereLogo';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  React.useEffect(() => {
    if (isAuthenticated()) {
      navigate('/profile');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          {/* Logo and Header */}
          <div className="flex justify-center mb-8">
            <SphereLogo className="w-32 h-32" />
          </div>
          
          <h1 className="text-6xl font-bold text-white mb-4">
            SPHERE
          </h1>
          <p className="text-2xl text-white/90 mb-8">
            Secure Patient Health Record System
          </p>

          {/* Action Buttons */}
          <div className="flex gap-4 justify-center mb-12">
            <button
              onClick={() => navigate('/login')}
              className="px-8 py-4 bg-white text-indigo-600 rounded-lg font-semibold text-lg hover:bg-gray-100 transition shadow-lg"
            >
              Login
            </button>
            <button
              onClick={() => navigate('/register')}
              className="px-8 py-4 bg-indigo-600 text-white rounded-lg font-semibold text-lg hover:bg-indigo-700 transition shadow-lg border-2 border-white"
            >
              Register
            </button>
          </div>

          {/* Simple Info Card */}
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 text-white max-w-md mx-auto">
            <p className="text-sm">
              A secure platform to record your health data and share it with trusted medical professionals.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;