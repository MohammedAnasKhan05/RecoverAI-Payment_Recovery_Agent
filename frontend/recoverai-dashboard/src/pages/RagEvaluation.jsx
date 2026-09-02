import React, { useState, useEffect } from 'react';
import { 
  Database, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Award, 
  BookOpen, 
  Target, 
  Compass,
  FileCheck2,
  Sparkles
} from 'lucide-react';
import { fetchRagEvaluation } from '../services/api';

export default function RagEvaluation() {
  const [evalData, setEvalData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadEvaluation = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRagEvaluation();
      setEvalData(data);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to fetch RAG evaluation data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvaluation();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center space-y-3">
          <RefreshCw className="w-8 h-8 text-[#0C6BF5] animate-spin" />
          <p className="text-sm font-medium text-slate-500">Running dynamic RAG benchmark suite...</p>
        </div>
      </div>
    );
  }

  if (error || !evalData) {
    return (
      <div className="p-8 bg-white rounded-xl border border-slate-200 card-shadow text-center space-y-4">
        <p className="text-sm text-rose-600">{error || 'Failed to load evaluation metrics.'}</p>
        <button onClick={loadEvaluation} className="px-4 py-2 bg-[#0C6BF5] text-white text-xs font-semibold rounded-lg">
          Retry Benchmark
        </button>
      </div>
    );
  }

  const metrics = [
    {
      title: 'Retrieval Accuracy',
      value: `${(evalData.retrieval_accuracy * 100).toFixed(1)}%`,
      desc: 'Correct policy matched',
      icon: Target,
      color: 'text-blue-600',
      bg: 'bg-blue-50'
    },
    {
      title: 'Context Relevance',
      value: `${(evalData.context_relevance * 100).toFixed(1)}%`,
      desc: 'Cosine semantic similarity',
      icon: Compass,
      color: 'text-indigo-600',
      bg: 'bg-indigo-50'
    },
    {
      title: 'Answer Grounding',
      value: `${(evalData.answer_grounding * 100).toFixed(1)}%`,
      desc: 'Factual token grounding',
      icon: FileCheck2,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50'
    },
    {
      title: 'Faithfulness',
      value: `${(evalData.faithfulness * 100).toFixed(1)}%`,
      desc: 'Policy constraint fidelity',
      icon: BookOpen,
      color: 'text-purple-600',
      bg: 'bg-purple-50'
    },
    {
      title: 'Overall RAG Score',
      value: `${(evalData.overall_score * 100).toFixed(1)}%`,
      desc: 'Composite benchmark index',
      icon: Award,
      color: 'text-amber-600',
      bg: 'bg-amber-50'
    },
  ];

  return (
    <div className="space-y-8 pb-16 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold text-[#0C2340]">RAG Policy Evaluation</h1>
            <span className="bg-emerald-50 text-emerald-700 text-xs font-bold px-2.5 py-0.5 rounded-full border border-emerald-200">
              Live Benchmark
            </span>
          </div>
          <p className="text-sm text-slate-500">
            Real-time evaluation across {evalData.total_queries} benchmark queries against indexed domain recovery policies
          </p>
        </div>

        <button
          onClick={loadEvaluation}
          className="inline-flex items-center space-x-2 px-4 py-2 border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg shadow-sm transition"
        >
          <RefreshCw className="w-3.5 h-3.5 text-[#0C6BF5]" />
          <span>Re-run Benchmark</span>
        </button>
      </div>

      {/* 5 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div key={idx} className="bg-white p-5 rounded-xl border border-slate-200 card-shadow">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500">{m.title}</span>
                <div className={`w-8 h-8 rounded-lg ${m.bg} ${m.color} flex items-center justify-center`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3">
                <div className={`text-2xl font-extrabold ${m.color}`}>
                  {m.value}
                </div>
                <p className="text-[11px] text-slate-500 mt-0.5">{m.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Benchmark Results Table */}
      <div className="bg-white rounded-2xl border border-slate-200 card-shadow overflow-hidden">
        <div className="p-6 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-[#0C2340]">Benchmark Evaluation Queries</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Testing retrieval accuracy and semantic grounding against UPI, Card, Abandonment, and Escalation policies
            </p>
          </div>
          <span className="text-xs font-mono font-semibold text-slate-500">
            {evalData.results?.filter(r => r.correct).length} / {evalData.total_queries} Correct
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3.5 font-semibold text-slate-500 uppercase">Query</th>
                <th className="px-6 py-3.5 font-semibold text-slate-500 uppercase">Expected Policy</th>
                <th className="px-6 py-3.5 font-semibold text-slate-500 uppercase">Retrieved Policy</th>
                <th className="px-6 py-3.5 text-center font-semibold text-slate-500 uppercase">Correct</th>
                <th className="px-6 py-3.5 text-center font-semibold text-slate-500 uppercase">Grounded</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-100">
              {evalData.results?.map((res, idx) => (
                <tr key={idx} className="hover:bg-slate-50/70 transition">
                  <td className="px-6 py-3.5 font-medium text-slate-800 max-w-sm">
                    "{res.query}"
                  </td>
                  <td className="px-6 py-3.5 font-mono text-slate-600">
                    {res.expected_policy}
                  </td>
                  <td className="px-6 py-3.5 font-mono font-bold text-[#0C6BF5]">
                    {res.retrieved_policy}
                  </td>
                  <td className="px-6 py-3.5 text-center">
                    {res.correct ? (
                      <span className="inline-flex items-center text-emerald-600 font-bold space-x-1">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Pass</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center text-rose-600 font-bold space-x-1">
                        <XCircle className="w-4 h-4" />
                        <span>Fail</span>
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-3.5 text-center">
                    {res.grounded ? (
                      <span className="inline-flex items-center text-emerald-600 font-bold space-x-1">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Yes</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center text-slate-400 font-bold space-x-1">
                        <XCircle className="w-4 h-4" />
                        <span>No</span>
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
