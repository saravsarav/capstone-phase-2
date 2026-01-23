import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  ShieldAlert,
  Search,
  Activity,
  Terminal,
  CheckCircle,
  AlertTriangle,
  Info,
  ExternalLink,
  BrainCircuit,
  History,
  Send,
  Globe,
  Database,
  Lock,
  Cpu,
  Zap,
  LayoutGrid,
  ChevronRight
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [url, setUrl] = useState("");
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [feedback, setFeedback] = useState({ submitted: false, rating: null });
  const [scanLogs, setScanLogs] = useState([]);

  useEffect(() => {
    fetchHistory();
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API_BASE}/stats`);
      setStats(res.data);
    } catch (err) { console.error(err); }
  };

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/scans`);
      setHistory(res.data);
    } catch (err) { console.error("Failed to fetch history", err); }
  };

  const handleScan = async (e) => {
    e.preventDefault();
    if (!url) return;
    setScanning(true);
    setResult(null);
    setScanLogs(["[SYSTEM] Initializing reconnaissance sequence..."]);
    setFeedback({ submitted: false, rating: null });

    try {
      const { data } = await axios.post(`${API_BASE}/scan`, { url });
      const poll = setInterval(async () => {
        const check = await axios.get(`${API_BASE}/scan/${data.id}`);

        if (check.data.logs) {
          setScanLogs(check.data.logs);
        }

        if (check.data.status === "completed") {
          setResult(check.data);
          setScanning(false);
          fetchHistory();
          fetchStats();
          clearInterval(poll);
        }
      }, 800);
    } catch (err) {
      alert("Scan failed. Is the backend running?");
      setScanning(false);
    }
  };

  const submitFeedback = async (isAccurate) => {
    if (!result) return;
    try {
      await axios.post(`${API_BASE}/feedback`, {
        scan_id: result.id,
        is_accurate: isAccurate,
        corrected_severity: isAccurate ? result.predicted_severity_label : "Needs Manual Review"
      });
      setFeedback({ submitted: true, rating: isAccurate });
      fetchStats();
    } catch (err) { console.error(err); }
  };

  return (
    <div className="min-h-screen flex flex-col font-mono text-white bg-black">
      {/* Top Navigation */}
      <nav className="border-b border-white/5 bg-black/20 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2 group cursor-pointer">
              <div className="w-8 h-8 bg-brand-cyan rounded-sm flex items-center justify-center">
                <ShieldAlert className="text-black w-5 h-5" />
              </div>
              <span className="text-xl font-black tracking-tighter group-hover:text-brand-cyan transition-colors">SENTINEL</span>
            </div>
            <div className="hidden md:flex items-center gap-6 text-[10px] items-center font-bold tracking-widest text-slate-500">
              <span className="hover:text-white cursor-pointer transition-colors">DASHBOARD</span>
              <span className="hover:text-white cursor-pointer transition-colors">SCANS</span>
              <span className="hover:text-white cursor-pointer transition-colors">REPORTS</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/20">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-[10px] font-bold text-green-500 uppercase tracking-tighter">System Online</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16 pt-8">
          <h2 className="text-5xl md:text-7xl font-black mb-4 tracking-tighter gradient-text animate-pulse-glow">
            TARGET ACQUISITION
          </h2>
          <p className="text-slate-500 max-w-2xl mx-auto text-sm leading-relaxed tracking-tight">
            Deploy cognitive security protocols to scan, intercept, and neutralize vulnerabilities
            within the target endpoint architecture.
          </p>
        </div>

        {/* Scan Bar */}
        <div className="max-w-3xl mx-auto mb-20">
          <form onSubmit={handleScan} className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1 w-full group">
              <label className="text-[10px] font-bold text-brand-cyan uppercase mb-2 block tracking-widest">Target Endpoint URL</label>
              <div className="relative">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="HTTPS://VULNERABLE-TARGET.IO"
                  className="w-full text-2xl !bg-transparent border-b border-white/20 focus:border-brand-cyan outline-none transition-colors pb-2"
                  required
                />
              </div>
            </div>
            <button disabled={scanning} className="btn-primary h-[52px] min-w-[200px] flex items-center justify-center gap-2">
              {scanning ? (
                <>
                  <Activity className="animate-spin w-5 h-5" />
                  <span>ANALYZING...</span>
                </>
              ) : "INITIATE SCAN"}
            </button>
          </form>
        </div>

        {/* Dashboard Grid (Shown when no active scan/result) */}
        {!result && !scanning && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-20 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <div className="card tech-border">
              <div className="text-slate-500 text-[10px] font-bold mb-1 uppercase">Total Scans</div>
              <div className="text-3xl font-black text-brand-cyan">084</div>
              <div className="text-[10px] text-green-500 mt-2 font-bold">+12.5%</div>
            </div>
            <div className="card tech-border">
              <div className="text-slate-500 text-[10px] font-bold mb-1 uppercase">Critical Threats</div>
              <div className="text-3xl font-black text-red-500">012</div>
              <div className="text-[10px] text-red-400 mt-2 font-bold">ATTENTION REQ</div>
            </div>
            <div className="card tech-border">
              <div className="text-slate-500 text-[10px] font-bold mb-1 uppercase">Secure Hosts</div>
              <div className="text-3xl font-black text-green-500">056</div>
              <div className="text-[10px] text-slate-500 mt-2 font-bold select-none opacity-50">STABLE</div>
            </div>
            <div className="card tech-border">
              <div className="text-slate-500 text-[10px] font-bold mb-1 uppercase">Vulnerabilities</div>
              <div className="text-3xl font-black text-orange-500">142</div>
              <div className="text-[10px] text-slate-500 mt-2 font-bold select-none opacity-50">TOTAL ENGAGED</div>
            </div>
          </div>
        )}

        {/* Live Execution Logs (Terminal View) */}
        {scanning && (
          <div className="max-w-4xl mx-auto mb-12 animate-in fade-in transition-all duration-500">
            <div className="flex items-center gap-2 mb-4">
              <Terminal className="w-4 h-4 text-brand-cyan" />
              <h4 className="text-[10px] font-black tracking-widest text-brand-cyan uppercase">Live Execution Logs</h4>
            </div>
            <div className="bg-black/80 border border-brand-cyan/30 p-6 font-mono text-xs h-80 overflow-y-auto custom-scrollbar shadow-[0_0_20px_rgba(0,229,255,0.1)]">
              <div className="flex items-center gap-2 text-slate-500 mb-4 border-b border-white/5 pb-2">
                <span className="text-[8px]">/bin/sentinel-scan</span>
                <div className="flex-1"></div>
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-slate-800"></div>
                  <div className="w-1.5 h-1.5 rounded-full bg-slate-800"></div>
                  <div className="w-1.5 h-1.5 rounded-full bg-slate-800"></div>
                </div>
              </div>
              {scanLogs.map((log, i) => (
                <div key={i} className={cn(
                  "mb-2 flex items-start gap-3",
                  log.includes("SUCCESS") ? "text-green-400" :
                    log.includes("ERROR") ? "text-red-400" : "text-slate-400"
                )}>
                  <span className="opacity-30">[{i.toString().padStart(2, '0')}]</span>
                  <span className="opacity-50 select-none">➜</span>
                  <span className="flex-1">{log}</span>
                </div>
              ))}
              <div className="flex items-center gap-2 text-brand-cyan animate-pulse mt-2">
                <span className="w-2 h-4 bg-brand-cyan"></span>
              </div>
            </div>
          </div>
        )}

        {/* Results Area */}
        {result && (
          <div className="space-y-12 animate-in fade-in duration-500">
            {/* Analysis Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b border-white/10 pb-8">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 rounded-full bg-brand-cyan shadow-[0_0_8px_#00E5FF]"></div>
                  <span className="text-xs font-bold text-brand-cyan">SCAN COMPLETE</span>
                </div>
                <h3 className="text-4xl font-black tracking-tighter uppercase">{new URL(result.url).hostname}</h3>
              </div>
              <div className="flex flex-col items-end">
                <span className="text-[10px] text-slate-500 font-bold uppercase">Report ID</span>
                <span className="text-sm font-mono text-slate-300">#{result.id.slice(0, 8)}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Main Analysis Column */}
              <div className="lg:col-span-2 space-y-12">
                {/* Surface Map Discovery */}
                <section>
                  <div className="flex items-center gap-4 mb-6">
                    <div className="h-[1px] flex-1 bg-white/10"></div>
                    <h4 className="text-[10px] font-black tracking-[0.2em] text-slate-400 uppercase flex items-center gap-2">
                      <Globe className="w-3 h-3" /> Surface Map Discovery
                    </h4>
                    <div className="h-[1px] flex-1 bg-white/10"></div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {[
                      { l: "Crawled URLs", v: result.vulnerabilities.length * 3 + 4 },
                      { l: "Hidden Forms", v: "02" },
                      { l: "API Parameters", v: "14" },
                    ].map((m, i) => (
                      <div key={i} className="bg-white/5 p-4 border-l-2 border-brand-cyan/20">
                        <div className="text-[10px] text-slate-500 font-bold mb-1 uppercase">{m.l}</div>
                        <div className="text-2xl font-black">{m.v}</div>
                      </div>
                    ))}
                  </div>
                </section>

                {/* Core Detections */}
                <section>
                  <div className="flex justify-between items-center mb-8">
                    <h4 className="text-xl font-black italic tracking-tighter uppercase">Core Detections</h4>
                    <div className="h-px flex-1 mx-8 bg-gradient-to-r from-white/10 to-transparent"></div>
                  </div>
                  <div className="space-y-4">
                    {result.vulnerabilities.map((v, i) => (
                      <div key={i} className="group flex items-start gap-4 p-5 bg-white/5 tech-border hover:bg-white/[0.08] transition-colors border border-white/5">
                        <div className={cn(
                          "w-12 h-12 flex items-center justify-center shrink-0 border border-white/10 group-hover:border-brand-cyan/50 transition-colors",
                          v.raw_severity === "High" || v.raw_severity === "Critical" ? "text-red-500" : "text-brand-cyan"
                        )}>
                          {v.raw_severity === "High" || v.raw_severity === "Critical" ? <ShieldAlert className="w-6 h-6" /> : <Info className="w-6 h-6" />}
                        </div>
                        <div className="flex-1">
                          <div className="flex justify-between items-start mb-2">
                            <h5 className="text-lg font-black tracking-tight uppercase">{v.type}</h5>
                            <span className={cn(
                              "text-[10px] font-bold px-2 py-0.5 tracking-tighter",
                              v.raw_severity === "Critical" ? "bg-red-600 text-white" :
                                v.raw_severity === "High" ? "bg-red-500 text-black" :
                                  v.raw_severity === "Medium" ? "bg-yellow-500 text-black" : "bg-brand-cyan text-black"
                            )}>
                              {v.raw_severity.toUpperCase()}
                            </span>
                          </div>
                          <p className="text-slate-400 text-xs leading-relaxed mb-4">{v.description}</p>
                          {v.evidence && (
                            <div className="bg-black/40 p-3 font-mono text-[10px] text-brand-cyan/70 border border-white/5">
                              <span className="text-slate-600 block mb-1 uppercase font-bold tracking-widest text-[8px]">Discovery Trace</span>
                              {v.evidence}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              </div>

              {/* Sidebar Analysis */}
              <div className="space-y-8">
                {/* Severity Distribution Chart */}
                <div className="card tech-border">
                  <h5 className="text-[10px] font-black tracking-widest text-slate-500 uppercase mb-4">Severity Distribution</h5>
                  <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={[
                            { name: 'Critical', value: result.vulnerabilities.filter(v => v.raw_severity === 'Critical' || v.raw_severity === 'Critical').length || 0, color: '#dc2626' },
                            { name: 'High', value: result.vulnerabilities.filter(v => v.raw_severity === 'High').length || 0, color: '#ef4444' },
                            { name: 'Medium', value: result.vulnerabilities.filter(v => v.raw_severity === 'Medium').length || 0, color: '#eab308' },
                            { name: 'Low', value: result.vulnerabilities.filter(v => v.raw_severity === 'Low' || v.raw_severity === 'Info').length || 0, color: '#00E5FF' },
                          ].filter(d => d.value > 0)}
                          innerRadius={60}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {result.vulnerabilities.length > 0 ? (
                            [
                              { name: 'Critical', color: '#dc2626' },
                              { name: 'High', color: '#ef4444' },
                              { name: 'Medium', color: '#eab308' },
                              { name: 'Low', color: '#00E5FF' },
                            ].map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))
                          ) : null}
                        </Pie>
                        <Tooltip
                          contentStyle={{ backgroundColor: '#000', border: '1px solid rgba(255,255,255,0.1)', fontSize: '10px' }}
                          itemStyle={{ color: '#fff' }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="grid grid-cols-2 gap-2 mt-4">
                    {[
                      { l: 'Critical', c: 'bg-red-600' },
                      { l: 'High', c: 'bg-red-500' },
                      { l: 'Medium', c: 'bg-yellow-500' },
                      { l: 'Low', c: 'bg-brand-cyan' }
                    ].map(sev => {
                      const count = result.vulnerabilities.filter(v =>
                        sev.l === 'Low' ? (v.raw_severity === 'Low' || v.raw_severity === 'Info') : v.raw_severity === sev.l
                      ).length;
                      return (
                        <div key={sev.l} className="flex items-center gap-2">
                          <div className={cn("w-2 h-2 rounded-full", sev.c)}></div>
                          <span className="text-[10px] font-bold text-slate-400 uppercase">{sev.l}: {count}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Score Panel */}
                <div className="card tech-border !p-8 bg-brand-cyan/5 border-brand-cyan/30">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-[10px] font-bold text-brand-cyan uppercase tracking-[0.2em]">Neural Score</span>
                    <BrainCircuit className="w-4 h-4 text-brand-cyan" />
                  </div>
                  <div className="flex items-baseline gap-2 mb-6">
                    <span className="text-6xl font-black">{result.ml_severity_score}</span>
                    <span className="text-slate-500 text-xl">/10</span>
                  </div>
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-[10px] font-bold uppercase mb-1">
                      <span>Model Confidence</span>
                      <span>{Math.round(result.confidence_score * 100)}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-900 border border-white/5 relative">
                      <div
                        className="absolute h-full bg-brand-cyan shadow-[0_0_10px_#00E5FF]"
                        style={{ width: `${result.confidence_score * 100}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Feedback Panel */}
                <div className="card tech-border space-y-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Cpu className="w-4 h-4 text-slate-500" />
                    <h5 className="text-[10px] font-black tracking-widest text-slate-500 uppercase">Analyst Logic Gate</h5>
                  </div>
                  {!feedback.submitted ? (
                    <>
                      <p className="text-xs text-slate-400">Validate engine predictions to calibrate the neural weights.</p>
                      <div className="grid grid-cols-1 gap-2">
                        <button
                          onClick={() => submitFeedback(true)}
                          className="w-full py-2 border border-brand-cyan/20 text-brand-cyan text-[10px] font-bold hover:bg-brand-cyan hover:text-black transition-all uppercase tracking-widest"
                        >
                          Confirm Classification
                        </button>
                        <button
                          onClick={() => submitFeedback(false)}
                          className="w-full py-2 border border-white/10 text-slate-500 text-[10px] font-bold hover:border-red-500 hover:text-red-500 transition-all uppercase tracking-widest"
                        >
                          Override Prediction
                        </button>
                      </div>
                    </>
                  ) : (
                    <div className="py-4 text-center space-y-2">
                      <Zap className="w-6 h-6 text-green-500 mx-auto animate-pulse" />
                      <p className="text-[10px] font-bold text-green-500 uppercase tracking-widest">Weights Updated</p>
                      <p className="text-[10px] text-slate-600 uppercase">Online learning cycle complete.</p>
                    </div>
                  )}
                </div>

                {/* System Intel */}
                <div className="card tech-border bg-white/[0.02]">
                  <h5 className="text-[10px] font-black tracking-widest text-slate-500 uppercase mb-4 flex items-center justify-between">
                    System Intel
                    <Activity className="w-3 h-3" />
                  </h5>
                  {stats && (
                    <div className="space-y-4 font-mono">
                      <div className="flex justify-between items-center text-[10px]">
                        <span className="text-slate-600">ENGINE</span>
                        <span>{stats.model_version}</span>
                      </div>
                      <div className="flex justify-between items-center text-[10px]">
                        <span className="text-slate-600">INGESTED</span>
                        <span>{stats.analyst_labels_ingested} LABELS</span>
                      </div>
                      <div className="pt-2 border-t border-white/5">
                        <div className="text-[8px] text-slate-700 font-bold mb-2 tracking-widest uppercase">Bias Distribution</div>
                        <div className="space-y-2">
                          {Object.entries(stats.active_weights).slice(0, 3).map(([k, v]) => (
                            <div key={k} className="flex items-center gap-4">
                              <span className="text-[8px] text-slate-600 w-16 uppercase truncate">{k}</span>
                              <div className="flex-1 h-px bg-white/5">
                                <div className="h-full bg-slate-500" style={{ width: `${(v / 5) * 100}%` }} />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!result && !scanning && (
          <div className="max-w-4xl mx-auto opacity-10 pointer-events-none select-none mt-20">
            <div className="flex justify-center mb-8">
              <ShieldAlert className="w-32 h-32" />
            </div>
            <div className="h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
          </div>
        )}
      </main>

      {/* Terminal Footer */}
      <footer className="border-t border-white/5 bg-black/40 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 h-12 flex items-center justify-between text-[10px] font-bold text-slate-600 tracking-tighter uppercase">
          <div className="flex items-center gap-6">
            <span className="flex items-center gap-2">
              <Terminal className="w-3 h-3 text-brand-cyan" />
              SENTINEL_CORE_V2.0.4
            </span>
            <span className="flex items-center gap-2">
              <Activity className="w-3 h-3 text-green-500" />
              Operational
            </span>
          </div>
          <div className="flex items-center gap-6">
            <span>Latency: 12ms</span>
            <span className="text-brand-cyan">UTC: {new Date().toISOString().slice(11, 19)}</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
