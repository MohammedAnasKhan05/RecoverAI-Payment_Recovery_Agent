import React from 'react';

export default function StatusBadge({ status }) {
  const normalized = (status || '').toUpperCase();
  
  let styles = 'bg-slate-100 text-slate-700 border-slate-200';
  
  if (normalized === 'RECOVERED') {
    styles = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  } else if (normalized === 'AT_RISK') {
    styles = 'bg-sky-50 text-sky-700 border-sky-200';
  } else if (normalized === 'ESCALATED') {
    styles = 'bg-amber-50 text-amber-700 border-amber-200';
  } else if (normalized === 'STOPPED') {
    styles = 'bg-slate-100 text-slate-600 border-slate-300';
  } else if (normalized === 'FAILED') {
    styles = 'bg-rose-50 text-rose-700 border-rose-200';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles}`}>
      <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
        normalized === 'RECOVERED' ? 'bg-emerald-500' :
        normalized === 'AT_RISK' ? 'bg-sky-500 animate-pulse' :
        normalized === 'ESCALATED' ? 'bg-amber-500' :
        normalized === 'FAILED' ? 'bg-rose-500' : 'bg-slate-400'
      }`} />
      {normalized || 'UNKNOWN'}
    </span>
  );
}
