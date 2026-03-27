import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { startSimulation, getRateLimit } from '../services/api';

const features = [
  {
    title: 'Census-Grounded',
    description: 'Real demographic data from the US Census Bureau ACS 5-Year profiles. Every persona reflects actual population distributions.',
    icon: (
      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21" />
      </svg>
    ),
  },
  {
    title: '100 AI Personas',
    description: 'Statistically accurate residents generated with weighted sampling — each with a name, job, income, housing, and personality.',
    icon: (
      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
      </svg>
    ),
  },
  {
    title: 'Demographic Breakdowns',
    description: 'See support/opposition split by income, age, commute mode, and housing — plus hidden impacts on underrepresented groups.',
    icon: (
      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
      </svg>
    ),
  },
];

export default function Landing() {
  const navigate = useNavigate();
  const [zipCode, setZipCode] = useState('');
  const [policy, setPolicy] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [userApiKey, setUserApiKey] = useState('');
  const [rateLimit, setRateLimit] = useState(null);

  useEffect(() => {
    getRateLimit()
      .then(setRateLimit)
      .catch(() => {});
  }, []);

  const rateLimitReached = rateLimit && rateLimit.remaining <= 0 && !userApiKey.trim();

  async function handleDemo() {
    setLoading(true);
    setError('');
    try {
      const data = await startSimulation('22030', 'demo', 20, true);
      navigate(`/results/${data.sim_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load demo. Is the backend running?');
      setLoading(false);
    }
  }

  async function handleSimulate(e) {
    e.preventDefault();
    if (!zipCode.trim() || !policy.trim()) {
      setError('Please enter both a ZIP code and a policy description.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const key = userApiKey.trim() || null;
      const data = await startSimulation(zipCode.trim(), policy.trim(), 100, false, key);
      if (data.remaining !== undefined) {
        setRateLimit(prev => prev ? { ...prev, remaining: data.remaining } : prev);
      }
      navigate(`/loading`, { state: { simId: data.sim_id, zipCode, policy } });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start simulation. Is the backend running?');
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Nav */}
      <div className="max-w-5xl mx-auto px-6 pt-6 flex justify-end">
        <Link to="/history" className="text-sm text-gray-400 hover:text-indigo-400 transition-colors">
          View Past Simulations &rarr;
        </Link>
      </div>

      {/* Hero */}
      <div className="max-w-4xl mx-auto px-6 pt-12 pb-16 text-center">
        <h1 className="text-6xl font-bold tracking-tight mb-4">
          Census<span className="text-indigo-400">Minds</span>
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
          What does your community <span className="text-white font-medium">actually</span> think?
          Simulate policy reactions using real census demographics and AI personas.
        </p>
      </div>

      {/* Input Form */}
      <div className="max-w-2xl mx-auto px-6 pb-16">
        <form onSubmit={handleSimulate} className="bg-gray-900 rounded-2xl p-8 border border-gray-800 shadow-2xl">
          <div className="mb-6">
            <label htmlFor="zip" className="block text-sm font-medium text-gray-300 mb-2">
              ZIP Code
            </label>
            <input
              id="zip"
              type="text"
              value={zipCode}
              onChange={(e) => setZipCode(e.target.value)}
              placeholder="e.g. 22030"
              maxLength={5}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-lg"
            />
          </div>

          <div className="mb-6">
            <label htmlFor="policy" className="block text-sm font-medium text-gray-300 mb-2">
              Policy Description
            </label>
            <textarea
              id="policy"
              value={policy}
              onChange={(e) => setPolicy(e.target.value)}
              placeholder="e.g. The city is proposing to remove 200 street parking spots downtown to add protected bike lanes on Main Street"
              rows={4}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-lg resize-none"
            />
          </div>

          {error && (
            <p className="text-red-400 text-sm mb-4">{error}</p>
          )}

          {rateLimitReached && (
            <div className="mb-4 p-3 bg-red-950/40 border border-red-800 rounded-lg">
              <p className="text-red-400 text-sm">
                Daily simulation limit reached. Use demo mode or{' '}
                <button type="button" onClick={() => setShowAdvanced(true)} className="underline cursor-pointer">
                  provide your own API key
                </button>{' '}
                for unlimited simulations.
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || rateLimitReached}
            className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed rounded-lg text-white font-semibold text-lg transition-colors cursor-pointer"
          >
            {loading ? 'Starting Simulation...' : 'Simulate'}
          </button>

          {/* Rate limit counter */}
          {rateLimit && !userApiKey.trim() && (
            <p className="text-xs text-gray-500 text-center mt-2">
              {rateLimit.remaining}/{rateLimit.limit} free simulations remaining today
            </p>
          )}
          {userApiKey.trim() && (
            <p className="text-xs text-green-500 text-center mt-2">
              Using your API key — unlimited simulations
            </p>
          )}

          {/* Advanced section */}
          <div className="mt-4">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-sm text-gray-500 hover:text-gray-300 transition-colors cursor-pointer flex items-center gap-1 mx-auto"
            >
              <svg
                className={`w-3 h-3 transition-transform ${showAdvanced ? 'rotate-90' : ''}`}
                fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
              Advanced
            </button>

            {showAdvanced && (
              <div className="mt-3 p-4 bg-gray-800/50 border border-gray-700 rounded-lg">
                <label htmlFor="apikey" className="block text-xs font-medium text-gray-400 mb-1.5">
                  Your Anthropic API Key (optional)
                </label>
                <input
                  id="apikey"
                  type="password"
                  value={userApiKey}
                  onChange={(e) => setUserApiKey(e.target.value)}
                  placeholder="sk-ant-..."
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
                />
                <p className="text-xs text-gray-500 mt-1.5">
                  Provide your own key for unlimited simulations.{' '}
                  <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline">
                    Get one free at console.anthropic.com
                  </a>
                </p>
              </div>
            )}
          </div>

          <div className="mt-4 text-center">
            <button
              type="button"
              disabled={loading}
              onClick={handleDemo}
              className="text-sm text-gray-400 hover:text-indigo-400 transition-colors cursor-pointer"
            >
              or try a demo with pre-loaded results &rarr;
            </button>
          </div>
        </form>
      </div>

      {/* Feature Cards */}
      <div className="max-w-5xl mx-auto px-6 pb-20">
        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-left"
            >
              <div className="text-indigo-400 mb-4">{feature.icon}</div>
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
