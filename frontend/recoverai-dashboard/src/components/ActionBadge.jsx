import React from 'react';

export default function ActionBadge({ action }) {
  const norm = (action || '').toUpperCase();

  let styles = 'bg-slate-100 text-slate-700 border-slate-200';

  if (norm === 'RETRY') {
    styles = 'bg-blue-50 text-blue-700 border-blue-200';
  } else if (norm === 'ALTERNATE_PAYMENT') {
    styles = 'bg-indigo-50 text-indigo-700 border-indigo-200';
  } else if (norm === 'SEND_REMINDER') {
    styles = 'bg-purple-50 text-purple-700 border-purple-200';
  } else if (norm === 'ESCALATE') {
    styles = 'bg-amber-50 text-amber-800 border-amber-300';
  } else if (norm === 'STOP') {
    styles = 'bg-rose-50 text-rose-700 border-rose-200';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium tracking-wide border ${styles}`}>
      {norm || 'NONE'}
    </span>
  );
}
