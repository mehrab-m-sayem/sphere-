import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import authService from '../services/authService';
import SphereLogo from '../components/SphereLogo';

const TwoFactorPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [tempToken, setTempToken] = useState('');
  const [resendLoading, setResendLoading] = useState(false);

  useEffect(() => {
    const token = location.state?.tempToken;
    if (!token) {
      navigate('/login');
    } else {
      setTempToken(token);
    }
  }, [location, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authService.verify2FA(tempToken, code);
      navigate('/profile');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid verification code');
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResendLoading(true);
    try {
      await authService.resend2FA(tempToken);
      setError('');
      alert('New verification code sent to your email');
    } catch (err) {
      setError('Failed to resend code. Please try again.');
    } finally {
      setResendLoading(false);
    }
  };

  const handleCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
    setCode(value);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-2xl p-8">
        <div className="flex justify-center mb-6">
          <SphereLogo className="w-20 h-20" />
        </div>
        
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">
            Verification Code
          </h2>
          <p className="text-gray-600 text-sm">
            Enter the 6-digit code sent to your email
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <input
              type="text"
              value={code}
              onChange={handleCodeChange}
              placeholder="000000"
              required
              maxLength={6}
              className="w-full px-4 py-4 text-center text-3xl font-bold border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent tracking-widest"
              autoFocus
            />
            <p className="text-xs text-gray-500 text-center mt-2">
              Code expires in 5 minutes
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || code.length !== 6}
            className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
          >
            {loading ? 'Verifying...' : 'Verify & Login'}
          </button>
        </form>

        <div className="mt-6 text-center space-y-3">
          <button
            onClick={handleResend}
            disabled={resendLoading}
            className="text-indigo-600 hover:text-indigo-800 text-sm font-medium disabled:opacity-50"
          >
            {resendLoading ? 'Sending...' : "Didn't receive code? Resend"}
          </button>
          <div>
            <button
              onClick={() => navigate('/login')}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              ← Back to Login
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TwoFactorPage;