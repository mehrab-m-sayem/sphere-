import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { logout } from '../utils/auth';
import SphereLogo from '../components/SphereLogo';

interface User {
  id: number;
  username: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/admin/users');
      setUsers(response.data);
    } catch (err) {
      console.error('Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const toggleUserStatus = async (userId: number) => {
    try {
      await api.put(`/admin/users/${userId}/activate`);
      fetchUsers();
    } catch (err) {
      alert('Failed to update user status');
    }
  };

  const deleteUser = async (userId: number) => {
    if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      await api.delete(`/admin/users/${userId}`);
      fetchUsers();
    } catch (err) {
      alert('Failed to delete user');
    }
  };

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'doctor': return 'bg-blue-100 text-blue-800';
      case 'patient': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <SphereLogo className="w-10 h-10" />
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Admin Dashboard</h1>
                <p className="text-xs text-gray-500">User Management</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/profile')}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition text-sm font-medium"
              >
                My Profile
              </button>
              <button
                onClick={() => {
                  logout();
                  navigate('/');
                }}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-xl shadow-sm">
          {/* Search and Stats */}
          <div className="p-6 border-b">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search users by username, email, or name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div className="flex gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-800">{users.length}</p>
                  <p className="text-xs text-gray-500">Total Users</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">
                    {users.filter(u => u.is_active).length}
                  </p>
                  <p className="text-xs text-gray-500">Active</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">
                    {users.filter(u => !u.is_active).length}
                  </p>
                  <p className="text-xs text-gray-500">Inactive</p>
                </div>
              </div>
            </div>
          </div>

          {/* Users Table */}
          <div className="overflow-x-auto">
            {loading ? (
              <div className="text-center py-12">
                <SphereLogo className="w-12 h-12 mx-auto mb-4 animate-pulse" />
                <p className="text-gray-600">Loading users...</p>
              </div>
            ) : filteredUsers.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-600">No users found</p>
              </div>
            ) : (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Joined
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{user.name}</p>
                          <p className="text-xs text-gray-500">@{user.username}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <p className="text-sm text-gray-900">{user.email}</p>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleBadgeColor(user.role)}`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() => toggleUserStatus(user.id)}
                            className="px-3 py-1 bg-yellow-500 text-white text-xs rounded hover:bg-yellow-600 transition"
                          >
                            {user.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                          {user.role !== 'admin' && (
                            <button
                              onClick={() => deleteUser(user.id)}
                              className="px-3 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600 transition"
                            >
                              Delete
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;