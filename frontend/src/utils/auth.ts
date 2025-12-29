// Authentication utility functions

// Check if user is authenticated by verifying if a token exists in localStorage
export function isAuthenticated(): boolean {
	const token = localStorage.getItem('token');
	return !!token;
}

// Get the user's role from localStorage (assuming it's stored as 'role')
export function getUserRole(): string | null {
	return localStorage.getItem('role');
}

// Logout the user by clearing relevant localStorage items
export function logout(): void {
	localStorage.removeItem('token');
	localStorage.removeItem('role');
	// Optionally clear other user-related data
	localStorage.removeItem('user');
}
