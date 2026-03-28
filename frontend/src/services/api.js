import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach password header to every request
api.interceptors.request.use((config) => {
  const password = localStorage.getItem('censusminds_password');
  if (password) {
    config.headers['x-app-password'] = password;
  }
  return config;
});

export { API_BASE };

export async function verifyPassword(password) {
  const response = await api.post('/api/auth/verify', { password });
  return response.data;
}

export async function startSimulation(zipCode, policyDescription, numPersonas = 100, demo = false, anthropicApiKey = null) {
  const body = {
    zip_code: zipCode,
    policy_description: policyDescription,
    num_personas: numPersonas,
  };
  if (anthropicApiKey) {
    body.anthropic_api_key = anthropicApiKey;
  }
  const response = await api.post(`/api/simulate${demo ? '?demo=true' : ''}`, body);
  return response.data;
}

export async function getSimulationStatus(simId) {
  const response = await api.get(`/api/simulate/${simId}/status`);
  return response.data;
}

export async function getCensusData(zipCode) {
  const response = await api.get(`/api/census/${zipCode}`);
  return response.data;
}

export async function getRateLimit() {
  const response = await api.get('/api/rate-limit');
  return response.data;
}

export async function getSimulationsHistory() {
  const response = await api.get('/api/simulations');
  return response.data;
}

export async function getSavedSimulation(simId) {
  const response = await api.get(`/api/simulations/${simId}`);
  return response.data;
}

export default api;
