'use client';

import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  Send, 
  User, 
  Sparkles, 
  Zap, 
  Heart, 
  Dumbbell, 
  Copy, 
  Check, 
  Flame, 
  Activity, 
  RefreshCw,
  Terminal,
  Cpu
} from 'lucide-react';
import { generateClientChat } from '@/lib/sportsEngine';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sentiment?: string;
  tips?: string[];
  quote?: string;
  timestamp: string;
}

const FUTURISTIC_CHIPS = [
  { label: '⚡ Overcome Laziness & Train', prompt: 'I feel lazy and demotivated today, but I need to workout. Motivate me and tell me how to get started!' },
  { label: '🍛 High-Protein Indian Veg Diet', prompt: 'Give me a high-protein Indian vegetarian diet plan using paneer, soya chunks, and dal to hit 130g protein.' },
  { label: '🏋️ Squat Depth & Knee Caving', prompt: 'My knees cave in (valgus collapse) when squatting heavy. What biomechanical cues and prehab drills will fix this?' },
  { label: '🧘 Autoregulate Heavy Fatigue', prompt: 'I am totally exhausted from work today. Should I skip the gym or adapt my workout using RPE autoregulation?' },
  { label: '💊 Creatine & Supplement Truth', prompt: 'What are the scientific facts on Creatine Monohydrate, Whey Protein, and Ashwagandha for muscle growth?' },
  { label: '📊 Optimal Push-Pull-Legs Split', prompt: 'What is the scientifically optimal frequency and volume for a 6-day Push Pull Legs (PPL) hypertrophy split?' }
];

export default function VirtualCoach() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `### ⚡ PULSE AI // CYBER COACH INITIALIZED

Welcome to **Pulse AI**, your **Futuristic Biomechanics & Motivational Mentor**.

I am engineered to eliminate mental hesitation, optimize lifting kinematics, and engineer your nutrition:
* **🔥 Relentless Mindset & Motivation:** Break past procrastination and forge automated discipline.
* **🔬 Biomechanics & Joint Integrity:** Moment arms, knee tracking, bar paths, and injury prehab.
* **🍛 Indian Fitness Nutrition:** Complete high-protein strategies with paneer, soya, dal, and desi eggs.
* **📊 Hypertrophy Architecture:** PPL splits, RPE autoregulation, and CNS recovery.

Tap a quick-trigger protocol below or ask any question to initiate analysis.`,
      sentiment: 'SYS.STATUS // READY',
      quote: '“Discipline is choosing between what you want now and what you want most.”',
      tips: [
        'Ask about form cues, feeling tired, or Indian high-protein meal combos.',
        'Use the AI Pose Coach tab for live camera squat kinematics.'
      ],
      timestamp: 'ONLINE'
    }
  ]);

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: textToSend.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!messageText) setInput('');
    setIsLoading(true);

    try {
      // First attempt: Call FastAPI Backend
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textToSend.trim(),
          history: messages.slice(-5).map((m) => ({
            role: m.role,
            content: m.content
          }))
        })
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.reply,
          sentiment: data.sentiment_detected || 'HIGH PERFORMANCE',
          tips: data.actionable_tips || [],
          quote: data.motivational_quote,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages((prev) => [...prev, assistantMsg]);
        return;
      }
      throw new Error('Backend offline');
    } catch (err) {
      // Seamless Zero-Downtime Fallback: Client-Side Cyber Engine (No error displayed!)
      const clientResult = generateClientChat(textToSend.trim());
      const fallbackMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: clientResult.reply,
        sentiment: clientResult.sentiment,
        tips: clientResult.tips,
        quote: clientResult.quote,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, fallbackMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const renderMarkdown = (content: string) => {
    return content.split('\n\n').map((paragraph, idx) => {
      if (paragraph.startsWith('### ')) {
        return (
          <h3 key={idx} className="text-sm sm:text-base font-black text-cyan-400 mt-2 mb-1.5 flex items-center gap-2 tracking-wide font-mono uppercase">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 shadow-glow-cyan" />
            {paragraph.replace('### ', '')}
          </h3>
        );
      }
      if (paragraph.startsWith('* **') || paragraph.startsWith('- **')) {
        return (
          <div key={idx} className="space-y-1.5 my-2">
            {paragraph.split('\n').map((line, lIdx) => {
              const cleaned = line.replace(/^[\*\-]\s*/, '');
              const parts = cleaned.split('**');
              return (
                <div key={lIdx} className="flex items-start gap-2 text-xs sm:text-sm text-slate-300 leading-relaxed">
                  <span className="text-cyan-400 mt-1 text-[10px]">▸</span>
                  <span>
                    {parts.map((p, pIdx) =>
                      pIdx % 2 === 1 ? (
                        <strong key={pIdx} className="text-white font-semibold">{p}</strong>
                      ) : (
                        <span key={pIdx}>{p}</span>
                      )
                    )}
                  </span>
                </div>
              );
            })}
          </div>
        );
      }
      return (
        <p key={idx} className="text-xs sm:text-sm text-slate-300 leading-relaxed my-1.5">
          {paragraph}
        </p>
      );
    });
  };

  return (
    <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-140px)] min-h-[580px] bg-[#050811]/90 rounded-2xl border border-cyan-500/20 backdrop-blur-2xl overflow-hidden shadow-[0_0_35px_rgba(6,182,212,0.06)]">
      {/* Sleek Cyber HUD Header */}
      <div className="flex items-center justify-between px-4 sm:px-6 py-3 border-b border-cyan-500/20 bg-slate-950/60">
        <div className="flex items-center gap-3">
          <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Cpu className="h-4 w-4 animate-pulse" />
            <span className="absolute -top-0.5 -right-0.5 h-2 w-2 rounded-full bg-emerald-400 shadow-glow-emerald" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-black tracking-widest text-white font-mono uppercase">
                PULSE // CYBER COACH
              </h2>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                v3.2 NEURAL
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono">Autonomous Biomechanics & Indian Fitness Intelligence</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[10px] font-mono text-emerald-400">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>CORE ACTIVE</span>
          </div>
          <button
            onClick={() => setMessages([messages[0]])}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
            title="Reset Terminal"
          >
            <RefreshCw className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Cyber Quick-Trigger Chips */}
      <div className="px-4 py-2 border-b border-slate-800/60 bg-slate-950/30 overflow-x-auto no-scrollbar">
        <div className="flex items-center gap-2 min-w-max">
          <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider flex items-center gap-1">
            <Terminal className="h-3 w-3 text-cyan-400" /> DIRECTIVES:
          </span>
          {FUTURISTIC_CHIPS.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(chip.prompt)}
              className="text-[11px] font-medium px-2.5 py-1 rounded-md bg-slate-900/80 hover:bg-cyan-500/15 text-slate-300 hover:text-cyan-300 border border-slate-800 hover:border-cyan-500/30 transition-all cursor-pointer whitespace-nowrap"
            >
              {chip.label}
            </button>
          ))}
        </div>
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.role === 'user';
          return (
            <div
              key={msg.id}
              className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* Avatar */}
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border text-xs font-mono ${
                  isUser
                    ? 'bg-slate-800 border-slate-700 text-slate-200'
                    : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
                }`}
              >
                {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
              </div>

              {/* Bubble */}
              <div
                className={`group relative max-w-[85%] sm:max-w-[78%] rounded-xl p-3.5 sm:p-4 text-xs sm:text-sm border transition-all ${
                  isUser
                    ? 'bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700 text-white rounded-tr-none'
                    : 'bg-[#090e1c]/90 border-cyan-500/20 text-slate-200 rounded-tl-none shadow-[0_0_20px_rgba(6,182,212,0.03)]'
                }`}
              >
                {!isUser && msg.sentiment && (
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-cyan-500/15 text-[10px] font-mono">
                    <span className="flex items-center gap-1.5 text-cyan-400">
                      <Zap className="h-3 w-3" />
                      {msg.sentiment}
                    </span>
                    <button
                      onClick={() => copyToClipboard(msg.content, msg.id)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-white"
                      title="Copy Response"
                    >
                      {copiedId === msg.id ? (
                        <Check className="h-3 w-3 text-emerald-400" />
                      ) : (
                        <Copy className="h-3 w-3" />
                      )}
                    </button>
                  </div>
                )}

                <div className="prose-sm">{renderMarkdown(msg.content)}</div>

                {/* Motivational Quote Callout */}
                {msg.quote && (
                  <div className="mt-3 p-2.5 rounded-lg bg-cyan-950/30 border border-cyan-500/20 text-cyan-300 font-mono text-[11px] italic flex items-start gap-2">
                    <Flame className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
                    <span>{msg.quote}</span>
                  </div>
                )}

                {/* Actionable Tips */}
                {msg.tips && msg.tips.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-slate-800/80 space-y-1">
                    <p className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 flex items-center gap-1">
                      <Sparkles className="h-3 w-3" /> TACTICAL CUES:
                    </p>
                    {msg.tips.map((tip, i) => (
                      <div key={i} className="flex items-start gap-1.5 text-[11px] text-slate-300">
                        <span className="text-emerald-400 font-mono">[{i + 1}]</span>
                        <span>{tip}</span>
                      </div>
                    ))}
                  </div>
                )}

                <span className="block text-right text-[9px] font-mono text-slate-500 mt-2">
                  {msg.timestamp}
                </span>
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-start gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 animate-pulse">
              <Bot className="h-4 w-4" />
            </div>
            <div className="rounded-xl rounded-tl-none bg-[#090e1c] border border-cyan-500/20 p-3 flex items-center gap-2 text-xs font-mono text-cyan-400">
              <span className="h-2 w-2 rounded-full bg-cyan-400 animate-ping" />
              <span>SYNTHESIZING KINEMATIC & MOTIVATIONAL DIRECTIVE...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Cyber Input Terminal */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-3 sm:p-4 border-t border-cyan-500/20 bg-slate-950/80 flex items-center gap-2"
      >
        <div className="relative flex-1">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about squat depth, fatigue, high-protein Indian diet, splits..."
            className="w-full rounded-xl bg-slate-900/90 border border-slate-700/80 px-4 py-2.5 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all font-sans"
            disabled={isLoading}
          />
        </div>
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-emerald-500 text-slate-950 font-bold transition-all hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed shadow-glow-cyan"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
