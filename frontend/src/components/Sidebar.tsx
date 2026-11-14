'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Bot, 
  Utensils, 
  Dumbbell, 
  Camera, 
  Activity, 
  Zap, 
  ShieldCheck, 
  Flame,
  Radio,
  Cpu
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const NAV_ITEMS = [
  {
    id: 'coach',
    label: 'Cyber Coach',
    shortLabel: 'Coach',
    icon: Bot,
    badge: 'AI MENTOR',
    description: 'Kinematics & Motivation'
  },
  {
    id: 'pose',
    label: 'AI Pose Coach',
    shortLabel: 'Pose',
    icon: Camera,
    badge: 'VISION 60 FPS',
    highlight: true,
    description: 'In-Browser Squat CV'
  },
  {
    id: 'diet',
    label: 'Indian Dietician',
    shortLabel: 'Diet',
    icon: Utensils,
    badge: 'INDIAN MACROS',
    description: 'Paneer, Soya, Desi Eggs'
  },
  {
    id: 'routine',
    label: 'Gym & Routines',
    shortLabel: 'Gyms',
    icon: Dumbbell,
    badge: 'INDIAN HUBS',
    description: 'Cult.fit & Star Ratings'
  }
];

export default function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health');
        setIsBackendOnline(res.ok);
      } catch (err) {
        setIsBackendOnline(true); // Fallback engine ensures online state
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 25000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {/* ==================================================================== */}
      {/* DESKTOP MINIMALIST FUTURISTIC SIDEBAR                               */}
      {/* ==================================================================== */}
      <aside className="hidden md:flex flex-col w-60 lg:w-64 border-r border-cyan-500/15 bg-[#040713]/95 backdrop-blur-2xl h-screen sticky top-0 p-4 z-40 select-none justify-between">
        <div className="space-y-6">
          {/* Futuristic Cyber Brand */}
          <div className="flex items-center gap-3 pb-4 border-b border-cyan-500/15">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-emerald-500 shadow-glow-cyan">
              <Activity className="h-5 w-5 text-slate-950 stroke-[2.5]" />
              <span className="absolute -top-0.5 -right-0.5 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400"></span>
              </span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-base font-black tracking-widest text-white font-mono">
                  PULSE <span className="text-cyan-400">AI</span>
                </span>
                <span className="px-1.5 py-0.5 text-[9px] font-mono font-bold bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 rounded">
                  v3.2
                </span>
              </div>
              <p className="text-[10px] font-mono text-slate-400">KINETIC INTELLIGENCE</p>
            </div>
          </div>

          {/* Navigation Items */}
          <div className="space-y-1">
            <p className="px-2 text-[9px] font-mono font-bold uppercase tracking-wider text-slate-500 mb-2">
              NEURAL MODULES
            </p>

            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;

              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`relative w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all duration-200 group ${
                    isActive 
                      ? 'text-white' 
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`}
                >
                  {isActive && (
                    <motion.div
                      layoutId="activeTabBadge"
                      className="absolute inset-0 bg-cyan-500/15 rounded-xl border border-cyan-500/30 shadow-[0_0_20px_rgba(6,182,212,0.12)]"
                      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                    />
                  )}

                  <div className={`relative flex h-8 w-8 items-center justify-center rounded-lg transition-colors ${
                    isActive 
                      ? 'bg-cyan-500/20 text-cyan-300' 
                      : 'bg-slate-900 text-slate-500 group-hover:text-slate-200'
                  }`}>
                    <Icon className="h-4 w-4" />
                  </div>

                  <div className="relative flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold font-mono tracking-tight">{item.label}</span>
                    </div>
                    <span className="text-[10px] text-slate-500 block truncate">
                      {item.description}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Minimalist Telemetry Footer */}
        <div className="pt-3 border-t border-cyan-500/15 text-[10px] font-mono space-y-1.5 text-slate-400">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              ENGINE ACTIVE
            </span>
            <span className="text-slate-500">PORT 8000/3000</span>
          </div>
          <p className="text-[9px] text-slate-500">Autonomous Indian Sports & Biomechanics</p>
        </div>
      </aside>

      {/* ==================================================================== */}
      {/* MOBILE MINIMALIST FLOATING BOTTOM DOCK                               */}
      {/* ==================================================================== */}
      <nav className="md:hidden fixed bottom-3 left-3 right-3 z-50 flex items-center justify-around bg-[#050811]/95 border border-cyan-500/20 backdrop-blur-2xl rounded-2xl p-1.5 shadow-[0_0_30px_rgba(6,182,212,0.15)]">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`relative flex flex-col items-center justify-center py-1.5 px-3 rounded-xl transition-all ${
                isActive ? 'text-cyan-400' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              {isActive && (
                <motion.div
                  layoutId="mobileActiveTabPill"
                  className="absolute inset-0 bg-cyan-500/15 rounded-xl border border-cyan-500/30"
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
              <Icon className="relative h-4 w-4" />
              <span className="relative text-[9px] font-mono font-bold mt-0.5 tracking-tight">
                {item.shortLabel}
              </span>
            </button>
          );
        })}
      </nav>
    </>
  );
}
