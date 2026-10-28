import React from 'react';
import { Cpu, CheckCircle2, Zap, BarChart2, Shield } from 'lucide-react';

export default function ModelPerformanceView({ stats }) {
  const metrics = [
    { label: 'Overall Accuracy', value: '99.4%', change: '+0.4% from v0.9' },
    { label: 'Precision (Phishing)', value: '99.1%', change: 'Low False Positives' },
    { label: 'Recall (Phishing)', value: '98.8%', change: 'Minimal Missed Attacks' },
    { label: 'Average Latency', value: '18ms', change: 'Real-time inference' },
  ];

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Model Performance & Telemetry</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Machine Learning classifier evaluation, confusion matrix, and feature extraction metrics.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {metrics.map((m) => (
          <div key={m.label} className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-sm space-y-2">
            <span className="text-xs font-semibold text-slate-500 uppercase">{m.label}</span>
            <div className="text-3xl font-extrabold text-slate-900 tracking-tight">{m.value}</div>
            <div className="text-xs font-medium text-emerald-600 flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{m.change}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Confusion Matrix (6 cols) */}
        <div className="lg:col-span-6 bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="font-bold text-slate-900 text-base">Confusion Matrix</h3>
            <span className="text-xs font-mono text-slate-400">Test Evaluation (n=1,000)</span>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2 text-center text-xs">
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 space-y-1">
              <div className="font-extrabold text-2xl text-emerald-700">492</div>
              <div className="font-bold text-emerald-800">True Positive (TP)</div>
              <p className="text-[11px] text-emerald-600">Correctly blocked phishing</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
              <div className="font-extrabold text-2xl text-slate-700">4</div>
              <div className="font-bold text-slate-800">False Positive (FP)</div>
              <p className="text-[11px] text-slate-500">Safe email misclassified</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
              <div className="font-extrabold text-2xl text-slate-700">6</div>
              <div className="font-bold text-slate-800">False Negative (FN)</div>
              <p className="text-[11px] text-slate-500">Phishing bypass attempt</p>
            </div>

            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 space-y-1">
              <div className="font-extrabold text-2xl text-blue-700">498</div>
              <div className="font-bold text-blue-800">True Negative (TN)</div>
              <p className="text-[11px] text-blue-600">Correctly allowed safe email</p>
            </div>
          </div>
        </div>

        {/* Feature Extractor Pipeline (6 cols) */}
        <div className="lg:col-span-6 bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="font-bold text-slate-900 text-base">Feature Extraction Pipeline</h3>
            <span className="text-xs font-mono text-blue-600 font-semibold">Active Engine</span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start justify-between">
              <div>
                <div className="font-bold text-slate-900">TF-IDF N-Gram Vectorizer</div>
                <div className="text-slate-500 text-[11px]">Sublinear TF scaling, max 10,000 features, unigram & bigrams</div>
              </div>
              <span className="px-2 py-0.5 text-[11px] rounded bg-blue-100 text-blue-700 font-mono font-semibold">NLP</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start justify-between">
              <div>
                <div className="font-bold text-slate-900">Multi-Vector Heuristic Scorer</div>
                <div className="text-slate-500 text-[11px]">Brand spoofing dictionary, high-risk TLDs (.xyz, .top), raw IP links</div>
              </div>
              <span className="px-2 py-0.5 text-[11px] rounded bg-purple-100 text-purple-700 font-mono font-semibold">Heuristics</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start justify-between">
              <div>
                <div className="font-bold text-slate-900">URL Masking & Path Harvester</div>
                <div className="text-slate-500 text-[11px]">Unmasks bit.ly, tinyurl, and scans paths for /auth, /login, /wallet</div>
              </div>
              <span className="px-2 py-0.5 text-[11px] rounded bg-rose-100 text-rose-700 font-mono font-semibold">URL Threat</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
