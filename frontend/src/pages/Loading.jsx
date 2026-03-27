import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { getSimulationStatus } from '../services/api';

const STATUS_LABELS = {
  pending: 'Initializing simulation...',
  fetching_census: 'Fetching census data...',
  generating_personas: 'Generating AI personas...',
  running_simulation: 'Simulating community reactions...',
  aggregating: 'Aggregating results...',
  complete: 'Simulation complete!',
  error: 'Simulation failed.',
};

const PERSONA_NAMES = [
  'Maria Garcia', 'James Wilson', 'Priya Patel', 'DeShawn Robinson', 'Sarah Johnson',
  'Carlos Martinez', 'Emily Chen', 'Marcus Hall', 'Yuki Tanaka', 'Jessica Williams',
  'Robert Smith', 'Aaliyah Washington', 'Wei Zhang', 'Linda Brown', 'Fernando Lopez',
  'Keisha Mitchell', 'Andrew Davis', 'Sakura Kim', 'Tyler Moore', 'Sofia Rodriguez',
  'Jordan Taylor', 'Mei Li', 'Brandon Scott', 'Valentina Cruz', 'Ryan Anderson',
];

export default function Loading() {
  const location = useLocation();
  const navigate = useNavigate();
  const { simId, zipCode, policy } = location.state || {};

  const [status, setStatus] = useState('pending');
  const [progress, setProgress] = useState(0);
  const [visibleNames, setVisibleNames] = useState([]);
  const [error, setError] = useState('');

  // Poll for simulation status
  useEffect(() => {
    if (!simId) {
      navigate('/');
      return;
    }

    const interval = setInterval(async () => {
      try {
        const data = await getSimulationStatus(simId);
        setStatus(data.status);
        setProgress(data.progress || 0);

        if (data.status === 'complete') {
          clearInterval(interval);
          setTimeout(() => navigate(`/results/${simId}`), 800);
        } else if (data.status === 'error') {
          clearInterval(interval);
          setError(data.error || 'An unknown error occurred.');
        }
      } catch {
        clearInterval(interval);
        setError('Lost connection to the server.');
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [simId, navigate]);

  // Animate persona names appearing
  useEffect(() => {
    if (status !== 'running_simulation') return;

    let nameIndex = 0;
    const interval = setInterval(() => {
      if (nameIndex < PERSONA_NAMES.length) {
        setVisibleNames(prev => [...prev, PERSONA_NAMES[nameIndex]]);
        nameIndex++;
      } else {
        clearInterval(interval);
      }
    }, 600);

    return () => clearInterval(interval);
  }, [status]);

  if (!simId) return null;

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
      <div className="max-w-lg w-full px-6">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-2">
            Census<span className="text-indigo-400">Minds</span>
          </h1>
          {zipCode && (
            <p className="text-gray-500 text-sm">ZIP {zipCode}</p>
          )}
        </div>

        {/* Status Text */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3">
            {status !== 'complete' && status !== 'error' && (
              <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            )}
            {status === 'complete' && (
              <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
            )}
            <p className="text-lg text-gray-300">
              {STATUS_LABELS[status] || 'Processing...'}
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-xs text-gray-500 mb-2">
            <span>Progress</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-600 to-indigo-400 rounded-full transition-all duration-700 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Persona Names */}
        {visibleNames.length > 0 && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 max-h-64 overflow-y-auto">
            <p className="text-xs text-gray-500 mb-3 uppercase tracking-wider">Personas simulated</p>
            <div className="flex flex-wrap gap-2">
              {visibleNames.map((name, i) => (
                <span
                  key={i}
                  className="text-sm px-3 py-1 bg-gray-800 border border-gray-700 rounded-full text-gray-300 animate-fade-in"
                  style={{ animation: 'fadeIn 0.4s ease-out' }}
                >
                  {name}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Policy reminder */}
        {policy && (
          <p className="text-xs text-gray-600 text-center mt-6 max-w-sm mx-auto">
            "{policy.length > 100 ? policy.slice(0, 100) + '...' : policy}"
          </p>
        )}

        {/* Error state */}
        {error && (
          <div className="mt-6 text-center">
            <p className="text-red-400 mb-4">{error}</p>
            <button
              onClick={() => navigate('/')}
              className="text-indigo-400 hover:underline cursor-pointer"
            >
              Back to Home
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
