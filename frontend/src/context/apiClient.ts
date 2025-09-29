const API_BASE_URL = import.meta.env.VITE_API_URL;

export const apiClient = async (url: string, options: RequestInit = {}) => {
  const makeRequest = async (requestOptions: RequestInit) => {
    return fetch(`${API_BASE_URL}${url}`, {
      ...requestOptions,
      credentials: 'include',
    });
  };

  let response = await makeRequest(options);

  if (response.status === 401) {
    const refreshResponse = await fetch(`${API_BASE_URL}/users/refresh/`, {
      method: 'POST',
      credentials: 'include',
    });

    if (refreshResponse.ok) {
      response = await makeRequest(options);
    } else {
      window.location.href = '/login';
      throw new Error('Authentication failed');
    }
  }

  return response;
};