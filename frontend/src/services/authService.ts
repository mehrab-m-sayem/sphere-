import api from './api';

interface LoginData {
  email: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  name: string;
  contact_no: string;
  password: string;
  confirm_password: string;
  specialization?: string;
  age?: number;
  sex?: string;
}

const authService = {
  async login(data: LoginData) {
    const response = await api.post('/login', data);
    
    // Store token and user data if login successful
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      if (response.data.user) {
        localStorage.setItem('role', response.data.user.role);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
    }
    
    return response.data;
  },

  async registerDoctor(data: RegisterData) {
    const response = await api.post('/register/doctor', data);
    return response.data;
  },

  async registerPatient(data: RegisterData) {
    const response = await api.post('/register/patient', data);
    return response.data;
  },

  async verify2FA(tempToken: string, code: string) {
    const response = await api.post('/2fa/verify', { temp_token: tempToken, code });
    
    // Store token and user data
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      if (response.data.user) {
        localStorage.setItem('role', response.data.user.role);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
    }
    
    return response.data;
  },

  async resend2FA(tempToken: string) {
    const response = await api.post('/2fa/resend', { temp_token: tempToken });
    return response.data;
  },
};

export default authService;