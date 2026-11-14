'use client';

import React, { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import Sidebar from '@/components/Sidebar';
import VirtualCoach from '@/components/VirtualCoach';
import DieticianModule from '@/components/DieticianModule';
import RoutineModule from '@/components/RoutineModule';
import PoseCoachModule from '@/components/PoseCoachModule';
import { ShieldCheck, Cpu, Activity } from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>('pose');

  return (
    <div className="min-h-screen flex bg-[#03060f] text-slate-100 font-sans antialiased selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Sleek Minimalist Futuristic Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 pb-20 md:pb-6 overflow-x-hidden">
        {/* Minimalist Futuristic HUD Top Banner */}
        <header className="border-b border-cyan-500/15 bg-[#050811]/90 backdrop-blur-2xl px-4 sm:px-8 py-2.5 sticky top-0 z-30">
          <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
            <div className="flex items-center gap-2.5">
              <span className="flex h-2 w-2 rounded-full bg-cyan-400 animate-ping" />
              <span className="font-bold text-white tracking-widest uppercase">
                PULSE // KINEMATIC HUD
              </span>
              <span className="text-slate-600 hidden sm:inline">|</span>
              <span className="text-cyan-400/80 hidden sm:inline text-[11px]">
                INDIAN BIOMECHANICS & NUTRITION ENGINE
              </span>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 rounded-full bg-cyan-500/10 px-3 py-0.5 text-cyan-300 border border-cyan-500/20 text-[10px]">
                <ShieldCheck className="h-3 w-3 text-cyan-400" />
                <span>100% IN-BROWSER CV (ZERO CLOUD VIDEO)</span>
              </div>
              <div className="hidden sm:flex items-center gap-1.5 text-emerald-400 text-[10px]">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span>STATUS: NOMINAL</span>
              </div>
            </div>
          </div>
        </header>

        {/* Dynamic Viewport */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-3 sm:p-5 lg:p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.18, ease: 'easeOut' }}
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
