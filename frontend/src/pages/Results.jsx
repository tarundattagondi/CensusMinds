import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getSimulationStatus, API_BASE } from '../services/api';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell,
} from 'recharts';

const COLORS = { support: '#6366f1', oppose: '#ef4444' };

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-center">
      <p className="text-3xl font-bold text-white">{value}</p>
      <p className="text-sm text-gray-400 mt-1">{label}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  );
}

function SupportGauge({ supportPct, opposePct }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex justify-between text-sm mb-2">
        <span className="text-indigo-400 font-medium">Support {supportPct}%</span>
        <span className="text-red-400 font-medium">Oppose {opposePct}%</span>
      </div>
      <div className="w-full h-6 bg-gray-800 rounded-full overflow-hidden flex">
        <div
          className="h-full bg-indigo-500 transition-all duration-700"
          style={{ width: `${supportPct}%` }}
        />
        <div
          className="h-full bg-red-500 transition-all duration-700"
          style={{ width: `${opposePct}%` }}
        />
      </div>
    </div>
  );
}

function BreakdownChart({ title, data }) {
  if (!data || Object.keys(data).length === 0) return null;

  const chartData = Object.entries(data).map(([name, vals]) => ({
    name: name.length > 18 ? name.slice(0, 16) + '...' : name,
    fullName: name,
    Support: vals.support_pct,
    Oppose: vals.oppose_pct,
    total: vals.total,
  }));

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={chartData.length * 50 + 60}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 10, right: 30 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis type="number" domain={[0, 100]} tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <YAxis dataKey="name" type="category" width={140} tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <Tooltip
            contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
            labelStyle={{ color: '#f3f4f6' }}
            formatter={(value, name) => [`${value}%`, name]}
            labelFormatter={(label, payload) => payload?.[0]?.payload?.fullName || label}
          />
          <Legend wrapperStyle={{ color: '#9ca3af' }} />
          <Bar dataKey="Support" fill={COLORS.support} radius={[0, 4, 4, 0]} />
          <Bar dataKey="Oppose" fill={COLORS.oppose} radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function HiddenImpacts({ impacts }) {
  if (!impacts || impacts.length === 0) return null;

  return (
    <div className="bg-orange-950/40 border border-orange-700 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-orange-400 mb-3 flex items-center gap-2">
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
        </svg>
        Hidden Impacts — Underrepresented Voices
      </h3>
      <p className="text-sm text-orange-300/70 mb-4">
        These groups are highly impacted but unlikely to attend public meetings.
      </p>
      <div className="space-y-3">
        {impacts.map((impact, i) => (
          <div key={i} className="bg-orange-950/30 border border-orange-800/50 rounded-lg p-4">
            <p className="text-orange-200 font-medium">{impact.group}</p>
            <p className="text-sm text-orange-300/70 mt-1">
              {impact.high_impact_count} highly impacted, {impact.would_not_attend_count} wouldn't attend
              (out of {impact.total_in_group} in group)
            </p>
            {impact.example_personas?.length > 0 && (
              <p className="text-xs text-orange-400/50 mt-1">
                e.g. {impact.example_personas.join(', ')}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function ThemeList({ title, items, color }) {
  if (!items || items.length === 0) return null;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-white mb-3">{title}</h3>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex gap-3 text-sm">
            <span className={`mt-0.5 shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${color === 'red' ? 'bg-red-900/50 text-red-400' : 'bg-indigo-900/50 text-indigo-400'}`}>
              {i + 1}
            </span>
            <span className="text-gray-300">{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function PersonaCard({ response }) {
  const stanceColor = response.stance === 'SUPPORT' ? 'text-indigo-400 bg-indigo-900/30 border-indigo-800' : 'text-red-400 bg-red-900/30 border-red-800';
  const impactColors = {
    NONE: 'text-gray-400', LOW: 'text-green-400', MEDIUM: 'text-yellow-400',
    HIGH: 'text-orange-400', CRITICAL: 'text-red-400',
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-white font-medium">{response.persona_name}</h4>
        <span className={`text-xs font-bold px-2 py-1 rounded border ${stanceColor}`}>
          {response.stance}
        </span>
      </div>
      <div className="text-xs text-gray-500 mb-3 flex flex-wrap gap-x-3 gap-y-1">
        <span>Age {response.age}</span>
        <span>{response.ethnicity}</span>
        <span>{response.income_range}</span>
        <span>{response.housing_type}</span>
        <span>{response.commute_mode}</span>
      </div>
      <p className="text-sm text-gray-300 mb-3">{response.reasoning}</p>
      <div className="flex items-center justify-between text-xs">
        <span className={impactColors[response.impact_level] || 'text-gray-400'}>
          Impact: {response.impact_level}
        </span>
        <span className="text-gray-500">
          Attend meeting: {response.would_attend}
        </span>
      </div>
      {response.suggested_modification && (
        <p className="text-xs text-gray-500 mt-2 pt-2 border-t border-gray-800">
          <span className="text-gray-400 font-medium">Suggestion:</span> {response.suggested_modification}
        </p>
      )}
    </div>
  );
}

export default function Results() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [sim, setSim] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let interval;
    async function poll() {
      try {
        const data = await getSimulationStatus(id);
        setSim(data);
        if (data.status === 'complete' || data.status === 'error') {
          clearInterval(interval);
        }
      } catch {
        setError('Failed to fetch simulation results.');
        clearInterval(interval);
      }
    }
    poll();
    interval = setInterval(poll, 2000);
    return () => clearInterval(interval);
  }, [id]);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 text-lg">{error}</p>
          <button onClick={() => navigate('/')} className="mt-4 text-indigo-400 underline">
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  if (!sim || sim.status !== 'complete') {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading results...</p>
        </div>
      </div>
    );
  }

  if (sim.status === 'error') {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 text-lg">Simulation failed: {sim.error}</p>
          <button onClick={() => navigate('/')} className="mt-4 text-indigo-400 underline">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const r = sim.results;
  const s = r.summary;

  // Compute average impact score
  const impactScores = { NONE: 0, LOW: 1, MEDIUM: 2, HIGH: 3, CRITICAL: 4 };
  const impactEntries = Object.entries(r.impact_distribution || {});
  const avgImpact = impactEntries.length > 0
    ? (impactEntries.reduce((sum, [level, pct]) => sum + (impactScores[level] || 0) * pct, 0) / 100).toFixed(1)
    : 'N/A';
  const impactLabels = ['None', 'Low', 'Medium', 'High', 'Critical'];
  const avgImpactLabel = avgImpact !== 'N/A' ? impactLabels[Math.round(parseFloat(avgImpact))] || avgImpact : 'N/A';

  // Get individual responses from suggested_modifications (which has persona info)
  const personaResponses = r.suggested_modifications?.map(m => {
    // Find full response data — the results store responses in breakdowns
    return null;
  }).filter(Boolean) || [];

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-6xl mx-auto px-6 py-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-4 mb-2">
              <button onClick={() => navigate('/')} className="text-indigo-400 text-sm hover:underline cursor-pointer">
                &larr; New Simulation
              </button>
              <button onClick={() => navigate('/history')} className="text-gray-400 text-sm hover:underline cursor-pointer">
                History
              </button>
            </div>
            <h1 className="text-3xl font-bold">Simulation Results</h1>
            {r.policy && (
              <p className="text-gray-400 mt-2 max-w-2xl">"{r.policy}"</p>
            )}
            {r.zip_code && (
              <p className="text-sm text-gray-500 mt-1">
                ZIP {r.zip_code}
                {r.census_snapshot && (
                  <> — Pop. {r.census_snapshot.total_population?.toLocaleString()}, Median Income ${r.census_snapshot.median_household_income?.toLocaleString()}</>
                )}
              </p>
            )}
          </div>
          <div className="flex gap-3 shrink-0">
            <a
              href={`${API_BASE}/api/export/${id}/pdf`}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm text-white transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m.75 12l3 3m0 0l3-3m-3 3v-6m-1.5-9H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
              Download PDF
            </a>
            <a
              href={`${API_BASE}/api/export/${id}/csv`}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm text-white transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0112 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M3.375 8.25c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m17.25-3.75h-7.5c-.621 0-1.125.504-1.125 1.125m8.625-1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M12 10.875v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125M10.875 12c-.621 0-1.125.504-1.125 1.125M12 12c.621 0 1.125.504 1.125 1.125m0 0v1.5c0 .621-.504 1.125-1.125 1.125m1.125-2.625c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125M10.875 18.75c-.621 0-1.125-.504-1.125-1.125v-1.5c0-.621.504-1.125 1.125-1.125m1.125 2.625c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125" />
              </svg>
              Download CSV
            </a>
          </div>
        </div>

        {/* Support/Oppose Gauge */}
        <SupportGauge supportPct={s.support_pct} opposePct={s.oppose_pct} />

        {/* Stat Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <StatCard label="Support" value={`${s.support_pct}%`} sub={`${s.support_count} personas`} />
          <StatCard label="Oppose" value={`${s.oppose_pct}%`} sub={`${s.oppose_count} personas`} />
          <StatCard label="Avg Impact" value={avgImpactLabel} />
          <StatCard label="Would Attend Meeting" value={`${r.attendance?.would_attend_pct}%`} />
        </div>

        {/* Charts */}
        <div className="grid md:grid-cols-2 gap-6 mt-8">
          <BreakdownChart title="Support/Oppose by Income" data={r.breakdown_by_income} />
          <BreakdownChart title="Support/Oppose by Age Group" data={r.breakdown_by_age_group} />
        </div>

        <div className="grid md:grid-cols-2 gap-6 mt-6">
          <BreakdownChart title="Support/Oppose by Commute Mode" data={r.breakdown_by_commute} />
          <BreakdownChart title="Support/Oppose by Housing" data={r.breakdown_by_housing} />
        </div>

        {/* Hidden Impacts */}
        <div className="mt-8">
          <HiddenImpacts impacts={r.hidden_impacts} />
        </div>

        {/* Concerns & Benefits */}
        <div className="grid md:grid-cols-2 gap-6 mt-8">
          <ThemeList title="Top Concerns" items={r.top_concerns} color="red" />
          <ThemeList title="Top Benefits" items={r.top_benefits} color="indigo" />
        </div>

        {/* Persona Cards */}
        {r.all_responses && r.all_responses.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold text-white mb-4">Individual Persona Responses</h3>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[800px] overflow-y-auto pr-2">
              {r.all_responses.map((resp, i) => (
                <PersonaCard key={i} response={resp} />
              ))}
            </div>
          </div>
        )}

        {/* Suggested Modifications (fallback if no all_responses) */}
        {(!r.all_responses || r.all_responses.length === 0) && r.suggested_modifications?.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold text-white mb-4">Suggested Modifications</h3>
            <div className="space-y-3">
              {r.suggested_modifications.map((m, i) => (
                <div key={i} className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                  <span className="text-indigo-400 font-medium text-sm">{m.persona}</span>
                  <p className="text-gray-300 text-sm mt-1">{m.suggestion}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
