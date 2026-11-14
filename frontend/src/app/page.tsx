'use client';

import React, { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import Sidebar from '@/components/Sidebar';
import VirtualCoach from '@/components/VirtualCoach';
import DieticianModule from '@/components/DieticianModule';
import RoutineModule from '@/components/RoutineModule';
import PoseCoachModule from '@/components/PoseCoachModule';
import { Activity, ShieldCheck, Zap, Sparkles } from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>('pose');

  return (
    <div className="min-h-screen flex bg-[#060913] text-slate-100 font-sans antialiased selection:bg-teal-500/30 selection:text-teal-200">
      {/* Sleek Sidebar (Desktop Left / Mobile Bottom Dock) */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 pb-20 md:pb-6 overflow-x-hidden">
        {/* Sleek Top Banner */}
        <header className="border-b border-slate-800/60 bg-[#0a0f1d]/80 backdrop-blur-xl px-4 sm:px-8 py-3.5 sticky top-0 z-30">
          <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2.5">
              <span className="flex h-2.5 w-2.5 rounded-full bg-teal-400 animate-pulse shadow-glow-teal" />
              <span className="font-bold text-white tracking-wide">Pulse AI Platform</span>
              <span className="hidden sm:inline-block text-slate-500">•</span>
              <span className="text-slate-400 hidden sm:inline">
                FastAPI Python Engine + MediaPipe Pose Kinematics
              </span>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 rounded-full bg-teal-500/10 px-3 py-1 text-teal-300 border border-teal-500/20 text-[11px] font-semibold">
                <ShieldCheck className="h-3.5 w-3.5 text-teal-400" />
                <span>100% Client-Side Video (Zero Upload)</span>
              </div>
              <div className="hidden lg:flex items-center gap-1.5 text-slate-400 text-[11px]">
                <Zap className="h-3.5 w-3.5 text-emerald-400" />
                <span>FastAPI Port 8000</span>
              </div>
            </div>
          </div>
        </header>

        {/* Dynamic Animated Content Viewport */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -14 }}
              transition={{ duration: 0.22, ease: 'easeOut' }}
              className="h-full"
            >
              {activeTab === 'coach' && <VirtualCoach />}
              {activeTab === 'diet' && <DieticianModule />}
              {activeTab === 'routine' && (
                <RoutineModule onGoToPoseCoach={() => setActiveTab('pose')} />
              )}
              {activeTab === 'pose' && <PoseCoachModule />}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
