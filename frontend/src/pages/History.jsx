import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getSimulationsHistory } from '../services/api';

export default function History() {
  const navigate = useNavigate();
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getSimulationsHistory()
      .then((data) => {
        setSimulations(data);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load simulation history. Is the backend running?');
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Nav */}
      <div className="max-w-5xl mx-auto px-6 pt-6">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-indigo-400 text-sm hover:underline">
            &larr; Back to Home
          </Link>
          <Link to="/" className="text-xl font-bold">
            Census<span className="text-indigo-400">Minds</span>
          </Link>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-10">
        <h1 className="text-3xl font-bold mb-2">Simulation History</h1>
        <p className="text-gray-400 mb-8">View results from past policy simulations.</p>

        {loading && (
          <div className="text-center py-20">
            <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-400">Loading history...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-20">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {!loading && !error && simulations.length === 0 && (
          <div className="text-center py-20">
            <svg className="w-16 h-16 text-gray-700 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <p className="text-gray-500 text-lg mb-2">No past simulations yet</p>
            <p className="text-gray-600 text-sm mb-6">Run your first simulation to see results here.</p>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white font-medium transition-colors cursor-pointer"
            >
              Run a Simulation
            </button>
          </div>
        )}

        {!loading && simulations.length > 0 && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left text-xs font-medium text-gray-400 uppercase tracking-wider px-6 py-3">Date</th>
                  <th className="text-left text-xs font-medium text-gray-400 uppercase tracking-wider px-6 py-3">ZIP</th>
                  <th className="text-left text-xs font-medium text-gray-400 uppercase tracking-wider px-6 py-3">Policy</th>
                  <th className="text-right text-xs font-medium text-gray-400 uppercase tracking-wider px-6 py-3">Support</th>
                  <th className="text-right text-xs font-medium text-gray-400 uppercase tracking-wider px-6 py-3">Oppose</th>
                  <th className="text-right text-xs font-medium text-gray-400 uppercase tracking-wider px-6 py-3">Personas</th>
                </tr>
              </thead>
              <tbody>
                {simulations.map((sim) => {
                  const dateStr = sim.created_at
                    ? new Date(sim.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                    : 'N/A';
                  const policyPreview = sim.policy && sim.policy.length > 60
                    ? sim.policy.slice(0, 57) + '...'
                    : sim.policy || 'N/A';

                  return (
                    <tr
                      key={sim.id}
                      onClick={() => navigate(`/results/${sim.id}`)}
                      className="border-b border-gray-800/50 hover:bg-gray-800/50 cursor-pointer transition-colors"
                    >
                      <td className="px-6 py-4 text-sm text-gray-400 whitespace-nowrap">{dateStr}</td>
                      <td className="px-6 py-4 text-sm text-white font-mono">{sim.zip_code}</td>
                      <td className="px-6 py-4 text-sm text-gray-300">{policyPreview}</td>
                      <td className="px-6 py-4 text-sm text-indigo-400 text-right font-medium">{sim.support_pct}%</td>
                      <td className="px-6 py-4 text-sm text-red-400 text-right font-medium">{sim.oppose_pct}%</td>
                      <td className="px-6 py-4 text-sm text-gray-400 text-right">{sim.num_personas}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
