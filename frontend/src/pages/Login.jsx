import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { verifyPassword, startSimulation } from '../services/api';

export default function Login() {
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!password.trim()) return;
    setError('');
    setLoading(true);
    try {
      await verifyPassword(password.trim());
      localStorage.setItem('censusminds_password', password.trim());
      navigate('/');
    } catch {
      setError('Invalid access code');
      setLoading(false);
    }
  }

  async function handleDemo() {
    setLoading(true);
    setError('');
    try {
      // Demo doesn't need auth — set a temporary password to pass middleware
      // The demo endpoint is public-accessible, but we need the header for the simulate call
      // So we call verify first to check if we even need auth
      const data = await startSimulation('22030', 'demo', 20, true);
      navigate(`/results/${data.sim_id}`);
    } catch {
      setError('Demo unavailable. Please enter access code.');
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
      <div className="max-w-sm w-full px-6">
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold tracking-tight mb-3">
            Census<span className="text-indigo-400">Minds</span>
          </h1>
          <p className="text-gray-500 text-sm">Census-grounded policy impact simulator</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-gray-900 rounded-2xl p-8 border border-gray-800 shadow-2xl">
          <div className="mb-6">
            <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
              Access Code
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter access code"
              autoFocus
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-lg"
            />
          </div>

          {error && (
            <p className="text-red-400 text-sm mb-4">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed rounded-lg text-white font-semibold text-lg transition-colors cursor-pointer"
          >
            {loading ? 'Verifying...' : 'Enter'}
          </button>

          <div className="mt-5 text-center">
            <button
              type="button"
              disabled={loading}
              onClick={handleDemo}
              className="text-sm text-gray-500 hover:text-indigo-400 transition-colors cursor-pointer"
            >
              Try demo without access code
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
