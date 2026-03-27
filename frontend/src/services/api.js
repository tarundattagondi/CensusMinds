import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function startSimulation(zipCode, policyDescription, numPersonas = 100) {
  const response = await api.post('/api/simulate', {
    zip_code: zipCode,
    policy_description: policyDescription,
    num_personas: numPersonas,
  });
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

export default api;
