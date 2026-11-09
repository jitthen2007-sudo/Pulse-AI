'use client';

import React, { useState } from 'react';
import { 
  Dumbbell, 
  MapPin, 
  Trophy, 
  Target, 
  Gauge, 
  Sparkles, 
  Building2, 
  CheckCircle2, 
  Flame, 
  Clock, 
  Compass, 
  ChevronDown, 
  ChevronUp, 
  ArrowRight,
  ExternalLink
} from 'lucide-react';

interface Exercise {
  name: string;
  sets: string;
  reps: string;
  rest_seconds: number;
  key_cue: string;
}

interface WorkoutDay {
  day_title: string;
  target_muscles: string[];
  exercises: Exercise[];
}

interface WorkoutSplit {
  split_name: string;
  frequency: string;
  description: string;
  days: WorkoutDay[];
}

interface DailyChallenge {
  title: string;
  difficulty_badge: string;
  description: string;
  challenge_steps: string[];
  completion_time_est: string;
}

interface LocalGym {
  name: string;
  locality_context: string;
  vibe: string;
  key_amenities: string[];
  why_recommended: string;
}

interface RoutineResponse {
  workout_split: WorkoutSplit;
  daily_challenge: DailyChallenge;
  local_gyms: LocalGym[];
  coach_note: string;
  source: string;
}

interface RoutineModuleProps {
  onGoToPoseCoach?: () => void;
}

const LOCATION_SUGGESTIONS = [
  'Austin, TX',
  'London, UK',
  'New York, NY',
  'Indiranagar, Bangalore',
  'Los Angeles, CA',
  'Sydney, Australia'
];

export default function RoutineModule({ onGoToPoseCoach }: RoutineModuleProps) {
  const [location, setLocation] = useState<string>('Austin, TX');
  const [goal, setGoal] = useState<string>('Hypertrophy & Muscle Size');
  const [performanceScore, setPerformanceScore] = useState<number>(68);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [data, setData] = useState<RoutineResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activeDayIdx, setActiveDayIdx] = useState<number>(0);
  const [checkedSteps, setCheckedSteps] = useState<{ [key: number]: boolean }>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!location.trim()) return;

    setIsLoading(true);
    setErrorMsg(null);

    try {
      const response = await fetch('/api/routines', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: location.trim(),
          goal: goal,
          performance_score: Number(performanceScore)
        })
      });

      if (!response.ok) {
        throw new Error(`Server status: ${response.status}`);
      }

      const resData: RoutineResponse = await response.json();
      setData(resData);
      setActiveDayIdx(0);
      setCheckedSteps({});
    } catch (err) {
      console.error(err);
      setErrorMsg(err instanceof Error ? err.message : 'Failed to fetch recommendations');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreTier = (score: number) => {
    if (score < 35) return { label: 'Foundation / Beginner', color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' };
    if (score < 75) return { label: 'Intermediate / Progressive Athlete', color: 'text-teal-400 bg-teal-500/10 border-teal-500/20' };
    return { label: 'Elite / Spartan Conditioning', color: 'text-rose-400 bg-rose-500/10 border-rose-500/20' };
  };

  const currentTier = getScoreTier(performanceScore);

  return (
    <div className="max-w-6xl mx-auto px-4 py-4 space-y-6">
      {/* Module Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-500/10 border border-teal-500/30 text-teal-400">
              <Dumbbell className="h-5 w-5" />
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
              Smart Gym & Routine Recommender
            </h2>
            <span className="rounded-full bg-teal-500/10 px-2.5 py-0.5 text-xs font-semibold text-teal-400 border border-teal-500/20">
              Hyperlocal AI
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Engineered workout splits, score-calibrated daily challenges, and real gym chains in your vicinity.
          </p>
        </div>
      </div>

      {/* Main Grid: Input Form & Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Form */}
        <div className="lg:col-span-4 space-y-4">
          <form
            onSubmit={handleSubmit}
            className="rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-xl space-y-4"
          >
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Compass className="h-4 w-4 text-teal-400" /> Training Parameters
            </h3>

            {/* Location Input */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Your City / Locality
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-2.5 h-4 w-4 text-teal-400" />
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. Austin, TX or Indiranagar, Bangalore"
                  required
                  className="w-full rounded-xl bg-slate-950 border border-slate-700 pl-9 pr-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:border-teal-500 focus:outline-none"
                />
              </div>

              {/* Quick suggestions */}
              <div className="flex flex-wrap gap-1.5 mt-2">
                {LOCATION_SUGGESTIONS.map((loc) => (
                  <button
                    key={loc}
                    type="button"
                    onClick={() => setLocation(loc)}
                    className="text-[10px] text-slate-400 bg-slate-950 hover:bg-slate-800 px-2 py-0.5 rounded-md border border-slate-800 transition"
                  >
                    {loc}
                  </button>
                ))}
              </div>
            </div>

            {/* Goal Selector */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Training Goal
              </label>
              <select
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                className="w-full rounded-xl bg-slate-950 border border-slate-700 px-3 py-2 text-sm text-slate-200 focus:border-teal-500 focus:outline-none"
              >
                <option value="Hypertrophy & Muscle Size">Hypertrophy & Muscle Size (PPL/Arnold)</option>
                <option value="Maximal Strength & Power">Maximal Strength & Power (Compound Focus)</option>
                <option value="Functional Athleticism">Functional Athleticism & Mobility</option>
                <option value="Fat Shred & Conditioning">Fat Shred & Anaerobic Conditioning</option>
              </select>
            </div>

            {/* Performance Score Slider */}
            <div>
              <div className="flex justify-between items-center text-xs font-medium text-slate-300 mb-1">
                <span className="flex items-center gap-1.5">
                  <Gauge className="h-3.5 w-3.5 text-teal-400" /> Performance Score
                </span>
                <span className="text-teal-400 font-bold text-sm">{performanceScore} / 100</span>
              </div>
              <input
                type="range"
                min="10"
                max="100"
                step="1"
                value={performanceScore}
                onChange={(e) => setPerformanceScore(Number(e.target.value))}
                className="w-full accent-teal-400 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                <span>Beginner (10)</span>
                <span>Athletic (50)</span>
                <span>Elite (100)</span>
              </div>
              <div className={`mt-2 rounded-lg px-2.5 py-1 text-[11px] font-semibold border ${currentTier.color}`}>
                Target Tier: {currentTier.label}
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading || !location.trim()}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 py-3 text-sm font-bold text-slate-950 transition hover:opacity-95 disabled:opacity-50 shadow-glow-teal"
            >
              {isLoading ? (
                <>
                  <Sparkles className="h-4 w-4 animate-spin" />
                  <span>Synthesizing Routines & Local Gyms...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  <span>Generate Custom Split & Gyms</span>
                </>
              )}
            </button>
          </form>

          {errorMsg && (
            <div className="rounded-xl bg-rose-950/40 border border-rose-500/30 p-3 text-xs text-rose-300">
              {errorMsg}
            </div>
          )}
        </div>

        {/* Right Output Column */}
        <div className="lg:col-span-8 space-y-6">
          {!data && !isLoading && (
            <div className="rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 p-10 text-center flex flex-col items-center justify-center min-h-[400px]">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-500/10 text-teal-400 mb-4">
                <Dumbbell className="h-7 w-7" />
              </div>
              <h3 className="text-lg font-bold text-white">Hyperlocal Training Protocol</h3>
              <p className="text-sm text-slate-400 max-w-md mt-1">
                Enter your location and target performance score. Pulse AI will design an exact workout split, daily fitness challenge, and discover 3 real gym chains in your neighborhood.
              </p>
            </div>
          )}

          {isLoading && (
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-10 text-center flex flex-col items-center justify-center min-h-[400px] animate-pulse">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-500/20 text-teal-400 mb-4 animate-spin">
                <Sparkles className="h-7 w-7" />
              </div>
              <h3 className="text-lg font-bold text-white">Analyzing Local Gyms & Movement Kinematics...</h3>
              <p className="text-sm text-teal-400 mt-1">Cross-referencing real gym chains in {location} with your score of {performanceScore}.</p>
            </div>
          )}

          {data && !isLoading && (
            <div className="space-y-6 animate-fade-in">
              {/* Daily Challenge Card */}
              <div className="rounded-2xl bg-gradient-to-r from-teal-950/60 via-slate-900 to-emerald-950/40 border border-teal-500/40 p-5 shadow-xl relative overflow-hidden">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2">
                    <Trophy className="h-5 w-5 text-amber-400" />
                    <span className="text-xs font-bold uppercase tracking-wider text-teal-300">
                      Score {performanceScore} Benchmark Challenge
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 flex items-center gap-1">
                      <Clock className="h-3 w-3" /> {data.daily_challenge.completion_time_est}
                    </span>
                    <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-teal-500/10 text-teal-300 border border-teal-500/20">
                      {data.daily_challenge.difficulty_badge}
                    </span>
                  </div>
                </div>

                <h3 className="text-lg font-black text-white">{data.daily_challenge.title}</h3>
                <p className="text-xs sm:text-sm text-slate-300 mt-1">{data.daily_challenge.description}</p>

                {/* Challenge Steps */}
                <div className="mt-4 space-y-2">
                  {data.daily_challenge.challenge_steps.map((step, sIdx) => {
                    const isDone = !!checkedSteps[sIdx];
                    return (
                      <div
                        key={sIdx}
                        onClick={() => setCheckedSteps((prev) => ({ ...prev, [sIdx]: !prev[sIdx] }))}
                        className={`flex items-start gap-3 p-2.5 rounded-xl border cursor-pointer transition ${
                          isDone
                            ? 'bg-slate-950/40 border-slate-800/40 opacity-60'
                            : 'bg-slate-950/80 border-slate-800 hover:border-teal-500/40'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isDone}
                          onChange={() => {}}
                          className="mt-0.5 rounded accent-teal-400 h-4 w-4 cursor-pointer"
                        />
                        <span className={`text-xs ${isDone ? 'line-through text-slate-500' : 'text-slate-200'}`}>
                          {step}
                        </span>
                      </div>
                    );
                  })}
                </div>

                {onGoToPoseCoach && (
                  <div className="mt-4 flex justify-end">
                    <button
                      onClick={onGoToPoseCoach}
                      className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 px-4 py-2 text-xs font-bold text-slate-950 hover:opacity-95 transition shadow-glow-teal"
                    >
                      <span>Track Squat Reps on AI Pose Coach</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </button>
                  </div>
                )}
              </div>

              {/* Workout Split Card */}
              <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-xl space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-teal-400">
                      Engineered Split Protocol
                    </span>
                    <h3 className="text-lg font-bold text-white">{data.workout_split.split_name}</h3>
                    <p className="text-xs text-slate-400 mt-0.5">{data.workout_split.frequency}</p>
                  </div>
                  <p className="text-xs text-slate-300 max-w-sm hidden sm:block italic">
                    "{data.workout_split.description}"
                  </p>
                </div>

                {/* Day selector tabs */}
                <div className="flex gap-2 overflow-x-auto pb-1">
                  {data.workout_split.days.map((day, idx) => (
                    <button
                      key={idx}
                      onClick={() => setActiveDayIdx(idx)}
                      className={`px-3 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition border ${
                        activeDayIdx === idx
                          ? 'bg-teal-500/20 text-teal-300 border-teal-500/40 shadow-glow-teal'
                          : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                      }`}
                    >
                      Day {idx + 1}: {day.target_muscles.slice(0, 2).join(', ')}
                    </button>
                  ))}
                </div>

                {/* Active Day Exercises */}
                {data.workout_split.days[activeDayIdx] && (
                  <div className="space-y-3 pt-2">
                    <div className="flex flex-wrap items-center justify-between gap-2 bg-slate-950 p-3 rounded-xl border border-slate-800">
                      <h4 className="text-sm font-bold text-teal-300">
                        {data.workout_split.days[activeDayIdx].day_title}
                      </h4>
                      <div className="flex flex-wrap gap-1">
                        {data.workout_split.days[activeDayIdx].target_muscles.map((m, mIdx) => (
                          <span
                            key={mIdx}
                            className="text-[10px] bg-slate-900 text-slate-300 border border-slate-800 px-2 py-0.5 rounded-md"
                          >
                            {m}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-2">
                      {data.workout_split.days[activeDayIdx].exercises.map((ex, exIdx) => (
                        <div
                          key={exIdx}
                          className="rounded-xl bg-slate-950/70 border border-slate-800/80 p-3 hover:border-teal-500/30 transition"
                        >
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <span className="text-sm font-bold text-white flex items-center gap-2">
                              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-800 text-[10px] text-teal-400 font-bold">
                                {exIdx + 1}
                              </span>
                              {ex.name}
                            </span>
                            <div className="flex items-center gap-2 text-xs">
                              <span className="rounded bg-teal-500/10 px-2 py-0.5 text-teal-300 font-bold border border-teal-500/20">
                                {ex.sets} Sets × {ex.reps}
                              </span>
                              <span className="text-slate-400 text-[11px]">
                                Rest: {ex.rest_seconds}s
                              </span>
                            </div>
                          </div>
                          <p className="text-xs text-slate-400 mt-1.5 pl-7">
                            <strong className="text-teal-400">Kinematic Cue:</strong> {ex.key_cue}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Local Real Gym Chains Card */}
              <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 p-5 shadow-xl space-y-4">
                <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                  <Building2 className="h-5 w-5 text-teal-400" />
                  <div>
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                      3 Real Gym Chains in {location}
                    </h3>
                    <p className="text-xs text-slate-400">
                      Selected to match your {goal} and performance tier.
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {data.local_gyms.map((gym, gIdx) => (
                    <div
                      key={gIdx}
                      className="rounded-xl bg-slate-950 border border-slate-800/90 p-4 flex flex-col justify-between hover:border-teal-500/40 transition"
                    >
                      <div>
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <h4 className="text-sm font-bold text-white">{gym.name}</h4>
                          <span className="text-[10px] font-bold text-teal-400 bg-teal-950 px-2 py-0.5 rounded border border-teal-500/20">
                            #{gIdx + 1}
                          </span>
                        </div>
                        <p className="text-[11px] text-teal-300 mb-2 font-medium">
                          📍 {gym.locality_context}
                        </p>
                        <span className="inline-block text-[10px] text-amber-300 bg-amber-950/60 border border-amber-500/20 px-2 py-0.5 rounded mb-3">
                          {gym.vibe}
                        </span>

                        <div className="space-y-1 mb-3">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                            Key Equipment & Amenities:
                          </span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {gym.key_amenities.map((am, aIdx) => (
                              <span
                                key={aIdx}
                                className="text-[10px] bg-slate-900 text-slate-300 border border-slate-800 px-1.5 py-0.5 rounded"
                              >
                                {am}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      <p className="text-xs text-slate-400 border-t border-slate-900 pt-2 mt-2 italic">
                        "{gym.why_recommended}"
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Coach Note */}
              <div className="rounded-xl bg-teal-950/30 border border-teal-500/20 p-4 text-xs text-slate-300 leading-relaxed flex items-start gap-3">
                <Sparkles className="h-5 w-5 text-teal-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-teal-300 font-bold block mb-0.5">Master Coach Guidance</strong>
                  {data.coach_note}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
