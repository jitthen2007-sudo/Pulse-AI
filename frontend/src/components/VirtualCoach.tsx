'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, User, Sparkles, Zap, Heart, ShieldAlert, Dumbbell, Compass, RefreshCw, Copy, Check } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sentiment?: string;
  tips?: string[];
  timestamp: string;
}

const STARTER_PROMPTS = [
  {
    title: "Squat Biomechanics & Knee Caving",
    prompt: "My knees tend to cave inward (valgus collapse) at the bottom of heavy squats. What muscle imbalances cause this, and what prehab drills should I do?",
    category: "Anatomy & Biomechanics"
  },
  {
    title: "Mood & Autoregulation",
    prompt: "I am feeling totally exhausted and drained from work, but I was supposed to hit a heavy leg session. How do I adapt my workout and mindset?",
    category: "Mood & Recovery"
  },
  {
    title: "Optimal Rest Times",
    prompt: "What is the scientifically optimal rest time between sets for compound strength lifts versus hypertrophy isolation movements?",
    category: "Exercise Physiology"
  },
  {
    title: "Lean Bulk Macro Setup",
    prompt: "How should I structure my protein, carb, and fat grams for a 300 kcal lean bulk without gaining excess visceral fat?",
    category: "Nutrition & Macros"
  }
];

export default function VirtualCoach() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `### 👋 Welcome to Pulse AI Virtual Coaching!

I am your **Master Fitness Coach, Biomechanics Specialist, and Psychological Performance Mentor**. 

Ask me anything about:
* **🔬 Muscle Anatomy & Joint Kinematics** (moment arms, prime movers, form breakdown)
* **⚡ Recovery Windows & CNS Fatigue** (supercompensation, sleep protocols, HRV)
* **🏋️ Workout Split Architectures** (PPL, Upper/Lower, Arnold Split, 5/3/1)
* **🥗 Macro Science & Metabolic Calibration** (protein synthesis, leucine thresholds, surpluses)
* **🛡️ Injury Prevention & Prehabilitation** (rotator cuff, patellar tracking, pelvic tilt)
* **🧠 Mood & Mental Autoregulation** (let me know how you feel today—tired, fired up, or stressed!)

How can I elevate your training today?`,
      sentiment: 'Ready to Coach',
      tips: [
        'Tell me your current mood or fatigue level for tailored motivation.',
        'Be specific about joint sensations or lift targets.'
      ],
      timestamp: 'Just now'
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

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.reply,
        sentiment: data.sentiment_detected || 'Motivated',
        tips: data.actionable_tips || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `### ⚠️ Connection Notice\n\nI was unable to reach the AI backend endpoint. Please ensure the FastAPI server is running on port 8000.\n\n*Error details: ${err instanceof Error ? err.message : 'Unknown connection error'}*`,
        sentiment: 'System Alert',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Simple Markdown Renderer
  const renderMarkdown = (content: string) => {
    return content.split('\n\n').map((paragraph, idx) => {
      if (paragraph.startsWith('### ')) {
        return (
          <h3 key={idx} className="text-base sm:text-lg font-bold text-teal-300 mt-2 mb-1 flex items-center gap-2">
            {paragraph.replace('### ', '')}
          </h3>
        );
      }
      if (paragraph.startsWith('## ')) {
        return (
          <h2 key={idx} className="text-lg sm:text-xl font-extrabold text-white mt-3 mb-2">
            {paragraph.replace('## ', '')}
          </h2>
        );
      }
      if (paragraph.startsWith('* ') || paragraph.startsWith('- ')) {
        const items = paragraph.split('\n');
        return (
          <ul key={idx} className="list-disc list-inside space-y-1 my-2 text-slate-300">
            {items.map((item, itemIdx) => {
              const cleanItem = item.replace(/^[\*\-]\s+/, '');
              return (
                <li key={itemIdx} className="leading-relaxed">
                  <span dangerouslySetInnerHTML={{
                    __html: cleanItem
                      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
                      .replace(/\*(.*?)\*/g, '<em class="text-teal-200">$1</em>')
                  }} />
                </li>
              );
            })}
          </ul>
        );
      }
      return (
        <p key={idx} className="my-2 leading-relaxed text-slate-300 text-sm sm:text-base">
          <span dangerouslySetInnerHTML={{
            __html: paragraph
              .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
              .replace(/\*(.*?)\*/g, '<em class="text-teal-200">$1</em>')
          }} />
        </p>
      );
    });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-135px)] max-w-5xl mx-auto px-2 sm:px-4">
      {/* Module Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 pt-1 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-500/10 border border-teal-500/30 text-teal-400">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-white flex items-center gap-2">
              Pulse AI Virtual Coach
              <span className="text-[11px] font-medium bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/20">
                Autonomous Sports Science Engine
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Biomechanics, Recovery, Workout Splits, Injury Prevention & Mood Optimization
            </p>
          </div>
        </div>

        <button
          onClick={() => {
            setMessages([messages[0]]);
          }}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 px-2.5 py-1.5 rounded-lg hover:bg-slate-800 transition"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Clear Chat</span>
        </button>
      </div>

      {/* Chat Messages Container */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-1 sm:pr-2">
        {messages.map((m) => {
          const isUser = m.role === 'user';
          return (
            <div
              key={m.id}
              className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* Avatar */}
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-xl text-xs font-bold ${
                  isUser
                    ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md'
                    : 'bg-gradient-to-br from-teal-500 to-emerald-600 text-slate-950 shadow-glow-teal'
                }`}
              >
                {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
              </div>

              {/* Message Bubble */}
              <div
                className={`relative max-w-[85%] sm:max-w-[78%] rounded-2xl px-4 py-3 shadow-md ${
                  isUser
                    ? 'bg-gradient-to-r from-teal-600 to-emerald-600 text-white rounded-tr-none'
                    : 'bg-slate-900/90 border border-slate-800/90 text-slate-200 rounded-tl-none'
                }`}
              >
                {/* Sentiment pill for assistant */}
                {!isUser && m.sentiment && (
                  <div className="mb-2 flex items-center justify-between border-b border-slate-800 pb-1.5">
                    <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-teal-400 bg-teal-950/60 px-2 py-0.5 rounded-md border border-teal-500/20">
                      <Sparkles className="h-3 w-3" />
                      Detected State: {m.sentiment}
                    </span>
                    <button
                      onClick={() => copyToClipboard(m.content, m.id)}
                      className="text-slate-500 hover:text-slate-300 transition"
                      title="Copy response"
                    >
                      {copiedId === m.id ? (
                        <Check className="h-3.5 w-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="h-3.5 w-3.5" />
                      )}
                    </button>
                  </div>
                )}

                {/* Content */}
                <div className="text-sm sm:text-base leading-relaxed">
                  {isUser ? <p className="whitespace-pre-wrap">{m.content}</p> : renderMarkdown(m.content)}
                </div>

                {/* Assistant Actionable Tips */}
                {!isUser && m.tips && m.tips.length > 0 && (
                  <div className="mt-3 rounded-xl bg-slate-950/60 p-2.5 border border-teal-500/20">
                    <p className="text-[11px] font-bold text-teal-400 uppercase tracking-wider flex items-center gap-1 mb-1">
                      <Zap className="h-3 w-3" /> Coach Takeaways
                    </p>
                    <ul className="space-y-1 text-xs text-slate-300">
                      {m.tips.map((tip, tIdx) => (
                        <li key={tIdx} className="flex items-start gap-1.5">
                          <span className="text-teal-400">•</span>
                          <span>{tip}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="mt-1 flex justify-end">
                  <span className={`text-[10px] ${isUser ? 'text-teal-200' : 'text-slate-500'}`}>
                    {m.timestamp}
                  </span>
                </div>
              </div>
            </div>
          );
        })}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-start gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 text-slate-950 shadow-glow-teal">
              <Bot className="h-4 w-4" />
            </div>
            <div className="rounded-2xl rounded-tl-none bg-slate-900 border border-slate-800 px-4 py-3 text-slate-300">
              <div className="flex items-center gap-2">
                <span className="text-xs text-teal-400 font-medium">Coach is analyzing kinematics & physiology...</span>
                <div className="flex gap-1">
                  <span className="h-2 w-2 rounded-full bg-teal-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="h-2 w-2 rounded-full bg-teal-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="h-2 w-2 rounded-full bg-teal-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompt Suggestions */}
      {messages.length <= 2 && (
        <div className="pb-3 pt-1">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-teal-400" /> Recommended Coach Inquiries
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {STARTER_PROMPTS.map((item, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(item.prompt)}
                className="text-left p-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-800/90 border border-slate-800 hover:border-teal-500/40 transition group"
              >
                <div className="flex items-center justify-between text-xs font-semibold text-teal-300 group-hover:text-teal-200">
                  <span>{item.title}</span>
                  <span className="text-[10px] text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">
                    {item.category}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1 line-clamp-1">{item.prompt}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Bar */}
      <div className="pt-2 pb-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="relative flex items-center rounded-2xl bg-slate-900 border border-slate-700/80 p-1.5 shadow-2xl focus-within:border-teal-500 focus-within:ring-1 focus-within:ring-teal-500/50"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about muscle fatigue, PPL vs Arnold split, knee pain, macros, or your mood today..."
            className="w-full bg-transparent px-3 py-2 text-sm sm:text-base text-slate-100 placeholder-slate-500 focus:outline-none"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 text-slate-950 font-bold transition hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed shadow-glow-teal"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
        <p className="text-[11px] text-slate-400 text-center mt-1.5">
          Pulse AI combines Google Gemini 2.5 with biomechanics science for elite training precision.
        </p>
      </div>
    </div>
  );
}
