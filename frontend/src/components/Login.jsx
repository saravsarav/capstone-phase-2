import React, { useState } from 'react';
import { ShieldAlert, Lock, Mail, User, ArrowRight, Loader2 } from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const Login = ({ onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    full_name: ""
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (isLogin) {
        const res = await axios.post(`${API_BASE}/login`, {
          email: formData.email,
          password: formData.password
        });
        const token = res.data.access_token;
        localStorage.setItem("sentinel_token", token);
        onLoginSuccess(token);
      } else {
        await axios.post(`${API_BASE}/signup`, formData);
        setIsLogin(true);
        setError("Account created successfully! Please login.");
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-6 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-900 via-black to-black">
      <div className="w-full max-w-md animate-in fade-in slide-in-from-bottom-4 duration-700">
        {/* Logo Section */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-brand-cyan rounded-xl mb-4 shadow-[0_0_30px_rgba(0,229,255,0.3)]">
            <ShieldAlert className="text-black w-10 h-10" />
          </div>
          <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">SENTINEL</h1>
          <p className="text-slate-500 text-xs font-bold tracking-[0.3em] uppercase mt-2">Elite Threat Intelligence</p>
        </div>

        {/* Card */}
        <div className="bg-slate-950/50 backdrop-blur-xl border border-white/5 p-8 rounded-2xl shadow-2xl">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            {isLogin ? <Lock className="w-5 h-5 text-brand-cyan" /> : <User className="w-5 h-5 text-brand-cyan" />}
            {isLogin ? "System Access Required" : "Create Security Profile"}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest pl-1">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    required
                    placeholder="E.g. John Doe"
                    className="w-full bg-black/50 border border-white/10 rounded-lg py-2.5 pl-10 pr-4 text-sm focus:border-brand-cyan/50 focus:ring-1 focus:ring-brand-cyan/20 outline-none transition-all"
                    value={formData.full_name}
                    onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  />
                </div>
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest pl-1">Neural ID (Email)</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  required
                  placeholder="name@agency.gov"
                  className="w-full bg-black/50 border border-white/10 rounded-lg py-2.5 pl-10 pr-4 text-sm focus:border-brand-cyan/50 focus:ring-1 focus:ring-brand-cyan/20 outline-none transition-all"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest pl-1">Cyber Key (Password)</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  className="w-full bg-black/50 border border-white/10 rounded-lg py-2.5 pl-10 pr-4 text-sm focus:border-brand-cyan/50 focus:ring-1 focus:ring-brand-cyan/20 outline-none transition-all"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                />
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500 text-xs font-bold animate-shake">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-brand-cyan text-black font-black text-xs uppercase tracking-widest py-3 rounded-lg flex items-center justify-center gap-2 hover:bg-[#00B8CC] transition-all shadow-[0_10px_20px_rgba(0,229,255,0.1)] active:scale-95 disabled:opacity-50 disabled:active:scale-100"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : (
                <>
                  {isLogin ? "Initiate Access" : "Activate Profile"}
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 text-center">
            <button 
              onClick={() => { setIsLogin(!isLogin); setError(""); }}
              className="text-[10px] font-bold text-slate-500 hover:text-brand-cyan uppercase tracking-widest transition-colors"
            >
              {isLogin ? "Unauthorized? Register Identity" : "Already Identified? Secure Login"}
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 flex items-center justify-center gap-4 opacity-30">
          <div className="h-px w-10 bg-white"></div>
          <span className="text-[8px] font-bold uppercase tracking-[0.5em]">Sentinel Protocol V2</span>
          <div className="h-px w-10 bg-white"></div>
        </div>
      </div>
    </div>
  );
};

export default Login;
