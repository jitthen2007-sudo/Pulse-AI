'use client';

import React, { useState } from 'react';
import Navbar from '@/components/Navbar';
import VirtualCoach from '@/components/VirtualCoach';
import DieticianModule from '@/components/DieticianModule';
import RoutineModule from '@/components/RoutineModule';
import PoseCoachModule from '@/components/PoseCoachModule';
import { 
  Bot, 
  Utensils, 
  Dumbbell, 
  Camera, 
  Activity, 
  ShieldCheck, 
  Zap, 
  Sparkles,
  ArrowRight
} from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>('pose');

  return (
    <div className="min-h-screen flex flex-col bg-[#0a0f1d] text-slate-100">
      {/* Top Navbar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Hero Quick Banner for Hackathon Presentation */}
      <section className="border-b border-slate-800/60 bg-gradient-to-b from-[#0d1527] to-[#0a0f1d] px-4 py-3">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 text-slate-300">
            <span className="flex h-2 w-2 rounded-full bg-teal-400 animate-pulse" />
            <span className="font-semibold text-white">Pulse AI Hackathon Edition:</span>
            <span className="text-slate-400 hidden sm:inline">
              Client-Side Vision + FastAPI Backend + Google Gemini 2.5
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-slate-400">
              <ShieldCheck className="h-3.5 w-3.5 text-teal-400" />
              <span>Zero Video Upload (100% Private)</span>
            </div>
            <div className="flex items-center gap-1.5 text-slate-400 hidden md:flex">
              <Zap className="h-3.5 w-3.5 text-emerald-400" />
              <span>Next.js Rewrites to FastAPI</span>
            </div>
          </div>
        </div>
      </section>

      {/* Main Tab Viewport */}
      <main className="flex-1 py-4 sm:py-6">
        {activeTab === 'coach' && <VirtualCoach />}
        {activeTab === 'diet' && <DieticianModule />}
        {activeTab === 'routine' && (
          <RoutineModule onGoToPoseCoach={() => setActiveTab('pose')} />
        )}
        {activeTab === 'pose' && <PoseCoachModule />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 py-4 px-4 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-center sm:text-left">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-teal-400" />
            <span className="font-bold text-white">Pulse AI</span>
            <span>— Autonomous Fitness & Form Correction Platform</span>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <span>FastAPI Secure Backend</span>
            <span>•</span>
            <span>MediaPipe Pose Kinematics</span>
            <span>•</span>
            <span>Gemini Intelligence</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
