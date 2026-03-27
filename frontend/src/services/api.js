import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

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
