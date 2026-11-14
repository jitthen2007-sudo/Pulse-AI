'use client';

import React, { useEffect, useState } from 'react';
import { Activity, Bot, Utensils, Dumbbell, Camera, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export default function Navbar({ activeTab, setActiveTab }: NavbarProps) {
  const [healthStatus, setHealthStatus] = useState<{
    status: string;
    gemini_configured?: boolean;
    gemini_model?: string;
  } | null>(null);

  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => setHealthStatus(data))
      .catch(() => setHealthStatus({ status: 'offline' }));
  }, []);

  const navItems = [
    { id: 'coach', label: 'Virtual Coach', icon: Bot, badge: 'Gemini AI' },
    { id: 'pose', label: 'AI Pose Coach', icon: Camera, badge: 'Client-Side Vision', highlight: true },
    { id: 'diet', label: 'AI Dietician', icon: Utensils, badge: 'Nutrition' },
    { id: 'routine', label: 'Gym & Routines', icon: Dumbbell, badge: 'Hyperlocal' },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-[#0a0f1d]/85 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-teal-400 via-teal-500 to-emerald-600 shadow-glow-teal">
            <Activity className="h-6 w-6 text-slate-950 stroke-[2.5]" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-teal-400 opacity-75"></span>
              <span className="relative inline-flex h-3 w-3 rounded-full bg-teal-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-extrabold tracking-tight text-white">
                PULSE <span className="bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent">AI</span>
              </span>
              <span className="rounded-full bg-teal-500/10 px-2 py-0.5 text-[10px] font-semibold text-teal-400 border border-teal-500/20">
                v1.0 PRO
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Intelligent Form & Fitness Ecosystem</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 sm:gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`group relative flex items-center gap-2 rounded-xl px-3 py-2 text-xs sm:text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-teal-500/20 to-emerald-500/20 text-teal-300 border border-teal-500/40 shadow-glow-teal'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200 border border-transparent'
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? 'text-teal-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
                <span className="hidden md:inline">{item.label}</span>
                {item.highlight && (
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* System Status Pill */}
        <div className="hidden lg:flex items-center gap-2 rounded-full bg-slate-900/90 px-3 py-1.5 border border-slate-800 text-xs">
          {healthStatus?.status === 'online' ? (
            <>
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              <span className="text-slate-300 font-medium">
                {healthStatus.gemini_configured ? 'Gemini 2.5 Live' : 'Autonomous Mode (Offline Ready)'}
              </span>
            </>
          ) : (
            <>
              <AlertCircle className="h-3.5 w-3.5 text-amber-400 animate-pulse" />
              <span className="text-slate-400">Connecting...</span>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
