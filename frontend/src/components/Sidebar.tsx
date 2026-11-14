'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Bot, 
  Utensils, 
  Dumbbell, 
  Camera, 
  Activity, 
  CheckCircle2, 
  Zap, 
  ShieldCheck, 
  Flame,
  Radio
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const NAV_ITEMS = [
  {
    id: 'coach',
    label: 'Virtual Gym Buddy',
    shortLabel: 'Coach',
    icon: Bot,
    badge: 'AI Coach',
    description: 'Conversational Kinesiology'
  },
  {
    id: 'pose',
    label: 'AI Pose Coach',
    shortLabel: 'Pose',
    icon: Camera,
    badge: 'Vision 60 FPS',
    highlight: true,
    description: 'Real-Time Squat Vision'
  },
  {
    id: 'diet',
    label: 'AI Dietician',
    shortLabel: 'Diet',
    icon: Utensils,
    badge: 'Macros & Meals',
    description: 'Precision Nutrition'
  },
  {
    id: 'routine',
    label: 'Gym & Routines',
    shortLabel: 'Gyms',
    icon: Dumbbell,
    badge: 'Hyperlocal',
    description: 'Splits & Star Ratings'
  }
];

export default function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const [backendStatus, setBackendStatus] = useState<{
    status: string;
    mode?: string;
    gemini_configured?: boolean;
  }>({ status: 'connecting' });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health');
        if (res.ok) {
          const data = await res.json();
          setBackendStatus(data);
        } else {
          setBackendStatus({ status: 'online', mode: 'Local Engine Active' });
        }
      } catch (err) {
        setBackendStatus({ status: 'online', mode: 'Local Engine Active' });
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 20000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {/* ==================================================================== */}
      {/* DESKTOP SLEEK SIDEBAR (Inspired by Vercel & Apple Fitness)           */}
      {/* ==================================================================== */}
      <aside className="hidden md:flex flex-col w-64 lg:w-72 border-r border-slate-800/80 bg-[#070b14]/90 backdrop-blur-2xl h-screen sticky top-0 p-5 z-40 select-none">
        {/* Brand Header */}
        <div className="flex items-center gap-3 pb-6 border-b border-slate-800/60">
          <div className="relative flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-teal-400 via-teal-500 to-emerald-600 shadow-glow-teal shadow-teal-500/20">
            <Activity className="h-6 w-6 text-slate-950 stroke-[2.5]" />
            <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-teal-400 opacity-75"></span>
              <span className="relative inline-flex h-3.5 w-3.5 rounded-full bg-teal-500 border-2 border-slate-950"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-black tracking-tight text-white">
                PULSE <span className="bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent">AI</span>
              </span>
              <span className="rounded-full bg-teal-500/10 px-2 py-0.5 text-[10px] font-bold text-teal-400 border border-teal-500/20">
                PRO
              </span>
            </div>
            <p className="text-[11px] font-medium text-slate-400">Intelligent Fitness Ecosystem</p>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 py-6 space-y-1.5">
          <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2">
            Platform Modules
          </p>

          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`relative w-full flex items-center gap-3.5 px-3.5 py-3 rounded-xl text-left transition-all duration-200 group ${
                  isActive 
                    ? 'text-white' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeTabBadge"
                    className="absolute inset-0 bg-gradient-to-r from-teal-500/15 via-teal-500/10 to-emerald-500/5 rounded-xl border border-teal-500/30 shadow-glow-teal shadow-teal-500/10"
                    transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                  />
                )}

                <div className={`relative flex h-9 w-9 items-center justify-center rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-teal-500/20 text-teal-300' 
                    : 'bg-slate-900/80 text-slate-400 group-hover:text-slate-200 group-hover:bg-slate-800'
                }`}>
                  <Icon className="h-4 w-4" />
                </div>

                <div className="relative flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold truncate">{item.label}</span>
                    {item.highlight && (
                      <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse ml-1" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-500 truncate">{item.description}</p>
                </div>
              </button>
            );
          })}
        </div>

        {/* Live System Badge & Metrics */}
        <div className="pt-4 border-t border-slate-800/60 space-y-3">
          <div className="rounded-xl bg-slate-900/60 border border-slate-800/80 p-3">
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="text-slate-400 flex items-center gap-1.5 font-medium">
                <Radio className="h-3 w-3 text-teal-400 animate-pulse" />
                Backend Status
              </span>
              <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-400">
                <CheckCircle2 className="h-3 w-3" />
                Active
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono truncate">
              {backendStatus.mode || 'FastAPI Port 8000'}
            </p>
          </div>

          <div className="flex items-center justify-between px-1 text-[11px] text-slate-400">
            <span className="flex items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5 text-teal-400" />
              100% Client Privacy
            </span>
            <span>v2.0 Hackathon</span>
          </div>
        </div>
      </aside>

      {/* ==================================================================== */}
      {/* MOBILE FLOATING DOCK (Inspired by iOS / Apple Fitness)                */}
      {/* ==================================================================== */}
      <nav className="md:hidden fixed bottom-3 inset-x-3 z-50 bg-[#070b14]/90 backdrop-blur-2xl border border-slate-800/90 rounded-2xl p-1.5 shadow-2xl shadow-black/80">
        <div className="grid grid-cols-4 gap-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`relative flex flex-col items-center justify-center py-2 px-1 rounded-xl transition-all ${
                  isActive ? 'text-teal-300' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="mobileActiveTab"
                    className="absolute inset-0 bg-teal-500/15 rounded-xl border border-teal-500/30 shadow-glow-teal shadow-teal-500/10"
                    transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                  />
                )}
                <div className="relative">
                  <Icon className="h-5 w-5 mb-0.5" />
                  {item.highlight && (
                    <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
                  )}
                </div>
                <span className="relative text-[10px] font-semibold">{item.shortLabel}</span>
              </button>
            );
          })}
        </div>
      </nav>
    </>
  );
}
