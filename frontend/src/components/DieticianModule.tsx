'use client';

import React, { useState } from 'react';
import { 
  Utensils, 
  Scale, 
  Flame, 
  Apple, 
  ShoppingCart, 
  Droplets, 
  Clock, 
  CheckCircle, 
  Sparkles, 
  Copy, 
  Check, 
  PieChart, 
  Cpu,
  Compass,
  Zap
} from 'lucide-react';
import { generateClientDietPlan } from '@/lib/sportsEngine';

interface MacroBreakdown {
  protein_g: number;
  carbs_g: number;
  fats_g: number;
  protein_pct: number;
  carbs_pct: number;
  fats_pct: number;
}

interface MealItem {
  title: string;
  calories: number;
  macros: string;
  description: string;
}

interface GroceryItem {
  name: string;
  category: string;
  benefit: string;
  quantity_est: string;
}

interface NutritionResponse {
  bmi: number;
  bmi_category: string;
  bmi_analysis: string;
  daily_calories: number;
  macros: MacroBreakdown;
  strategy_summary: string;
  meal_plan: {
    breakfast?: MealItem;
    lunch?: MealItem;
    snack?: MealItem;
    dinner?: MealItem;
    pre_post_workout?: MealItem;
  };
  grocery_list: GroceryItem[];
  hydration_tip: string;
  timing_tip: string;
  source: string;
}

const INDIAN_PREFERENCES = [
  'Indian Vegetarian (Paneer, Soya, Dal, Dahi)',
  'Indian Non-Vegetarian (Eggs, Chicken, Fish)',
  'Indian Vegan (Soya Chunks, Tofu, Sattu, Chana)',
  'High-Protein Indian Muscle Gain',
  'Indian Caloric Deficit / Shred'
];

export default function DieticianModule() {
  const [weightKg, setWeightKg] = useState<number>(72);
  const [heightCm, setHeightCm] = useState<number>(175);
  const [goal, setGoal] = useState<string>('Muscle Hypertrophy & Strength');
  const [preference, setPreference] = useState<string>('Indian Vegetarian (Paneer, Soya, Dal, Dahi)');
  const [targetCalories, setTargetCalories] = useState<string>('');
  
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [plan, setPlan] = useState<NutritionResponse | null>(() => {
    // Initialize immediately with Indian Diet plan so UI is never blank
    return generateClientDietPlan(72, 175, 'Muscle Hypertrophy', 'Indian Vegetarian', null) as NutritionResponse;
  });
  const [checkedGroceries, setCheckedGroceries] = useState<{ [key: string]: boolean }>({});
  const [copiedList, setCopiedList] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('/api/nutrition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          weight_kg: Number(weightKg),
          height_cm: Number(heightCm),
          goal: goal,
          preference: preference,
          target_calories: targetCalories ? parseInt(targetCalories) : null
        })
      });

      if (response.ok) {
        const data: NutritionResponse = await response.json();
        setPlan(data);
        setCheckedGroceries({});
        return;
      }
      throw new Error('Backend offline');
    } catch (err) {
      // Seamless Zero-Error Fallback: Client-Side Indian Diet Engine
      const fallbackData = generateClientDietPlan(
        Number(weightKg),
        Number(heightCm),
        goal,
        preference,
        targetCalories ? parseInt(targetCalories) : null
      );
      setPlan(fallbackData as NutritionResponse);
      setCheckedGroceries({});
    } finally {
      setIsLoading(false);
    }
  };

  const toggleGroceryItem = (name: string) => {
    setCheckedGroceries((prev) => ({
      ...prev,
      [name]: !prev[name]
    }));
  };

  const copyGroceryList = () => {
    if (!plan?.grocery_list) return;
    const text = plan.grocery_list
      .map((item, i) => `${i + 1}. ${item.name} (${item.quantity_est}) - ${item.benefit}`)
      .join('\n');
    navigator.clipboard.writeText(`🛒 Pulse AI Indian Grocery Protocol:\n\n${text}`);
    setCopiedList(true);
    setTimeout(() => setCopiedList(false), 2500);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Sleek Cyber Futuristic Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-cyan-500/20 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Utensils className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-lg sm:text-xl font-black text-white font-mono uppercase tracking-wider flex items-center gap-2">
              PULSE // INDIAN DIET HUD
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                ACTIVE
              </span>
            </h2>
            <p className="text-xs text-slate-400 font-mono">
              High-Protein Indian Nutrition • Paneer, Soya, Dal & Desi Eggs
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-cyan-400">
          <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
          <span>CLIMATE: TROPICAL HYDRATION CALIBRATED</span>
        </div>
      </div>

      {/* Futuristic Parameter Input Grid */}
      <form onSubmit={handleSubmit} className="p-4 sm:p-5 rounded-2xl bg-[#050811]/90 border border-cyan-500/20 backdrop-blur-xl space-y-4 shadow-[0_0_25px_rgba(6,182,212,0.04)]">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div>
            <label className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
              Weight (KG)
            </label>
            <input
              type="number"
              value={weightKg}
              onChange={(e) => setWeightKg(Number(e.target.value))}
              min={35}
              max={250}
              className="w-full rounded-lg bg-slate-900 border border-slate-700/80 px-3 py-2 text-xs sm:text-sm text-white font-mono focus:border-cyan-400 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
              Height (CM)
            </label>
            <input
              type="number"
              value={heightCm}
              onChange={(e) => setHeightCm(Number(e.target.value))}
              min={100}
              max={230}
              className="w-full rounded-lg bg-slate-900 border border-slate-700/80 px-3 py-2 text-xs sm:text-sm text-white font-mono focus:border-cyan-400 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
              Primary Objective
            </label>
            <select
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              className="w-full rounded-lg bg-slate-900 border border-slate-700/80 px-3 py-2 text-xs sm:text-sm text-white font-mono focus:border-cyan-400 focus:outline-none"
            >
              <option value="Muscle Hypertrophy & Strength">Hypertrophy (Lean Bulk)</option>
              <option value="Fat Loss & Belly Shred">Fat Loss (Caloric Deficit)</option>
              <option value="Recomposition & Maintenance">Body Recomposition</option>
            </select>
          </div>

          <div>
            <label className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
              Indian Diet Type
            </label>
            <select
              value={preference}
              onChange={(e) => setPreference(e.target.value)}
              className="w-full rounded-lg bg-slate-900 border border-slate-700/80 px-3 py-2 text-xs sm:text-sm text-white font-mono focus:border-cyan-400 focus:outline-none"
            >
              {INDIAN_PREFERENCES.map((pref, i) => (
                <option key={i} value={pref}>{pref}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
          <div className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5">
            <Zap className="h-3.5 w-3.5 text-cyan-400" />
            <span>Mifflin-St Jeor + Indian Macro Ratio (2.0g Protein/kg)</span>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-400 to-emerald-500 text-slate-950 font-mono font-bold text-xs uppercase tracking-wider hover:opacity-90 transition-all shadow-glow-cyan"
          >
            {isLoading ? 'CALCULATING MACROS...' : 'RECALIBRATE DIET'}
          </button>
        </div>
      </form>

      {/* Rendered Strategy Blueprint */}
      {plan && (
        <div className="space-y-6">
          {/* Telemetry Metric Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="p-4 rounded-xl bg-[#050811]/80 border border-cyan-500/20 backdrop-blur-md">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-1">
                Body Mass Index
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-black text-white font-mono">{plan.bmi}</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  {plan.bmi_category}
                </span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#050811]/80 border border-cyan-500/20 backdrop-blur-md">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-1">
                Target Daily Energy
              </span>
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-black text-cyan-400 font-mono">{plan.daily_calories}</span>
                <span className="text-xs font-mono text-slate-400">KCAL</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#050811]/80 border border-cyan-500/20 backdrop-blur-md">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-1">
                Protein Target
              </span>
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-black text-emerald-400 font-mono">{plan.macros.protein_g}</span>
                <span className="text-xs font-mono text-slate-400">GRAMS / DAY</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#050811]/80 border border-cyan-500/20 backdrop-blur-md">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-1">
                Climate Hydration
              </span>
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-black text-amber-400 font-mono">4.0</span>
                <span className="text-xs font-mono text-slate-400">LITERS + PINK SALT</span>
              </div>
            </div>
          </div>

          {/* Futuristic Macro Proportions Bar */}
          <div className="p-4 rounded-xl bg-[#050811]/80 border border-cyan-500/20 space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-cyan-400">PROTEIN: {plan.macros.protein_g}g ({plan.macros.protein_pct}%)</span>
              <span className="text-emerald-400">CARBS: {plan.macros.carbs_g}g ({plan.macros.carbs_pct}%)</span>
              <span className="text-amber-400">FATS: {plan.macros.fats_g}g ({plan.macros.fats_pct}%)</span>
            </div>
            <div className="h-2 w-full rounded-full bg-slate-800 flex overflow-hidden">
              <div style={{ width: `${plan.macros.protein_pct}%` }} className="bg-cyan-400" />
              <div style={{ width: `${plan.macros.carbs_pct}%` }} className="bg-emerald-400" />
              <div style={{ width: `${plan.macros.fats_pct}%` }} className="bg-amber-400" />
            </div>
          </div>

          {/* Indian 5-Meal Schedule */}
          <div className="space-y-3">
            <h3 className="text-xs font-mono uppercase tracking-widest text-cyan-400 flex items-center gap-2">
              <Clock className="h-3.5 w-3.5" /> 5-PHASE DAILY INDIAN MEAL PROTOCOL
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(plan.meal_plan).map(([phase, item], idx) => {
                if (!item) return null;
                return (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-[#070c18] border border-slate-800 hover:border-cyan-500/30 transition-all space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                        {phase.replace('_', ' ')}
                      </span>
                      <span className="text-xs font-mono text-emerald-400">{item.calories} kcal</span>
                    </div>
                    <h4 className="text-sm font-bold text-white tracking-wide">{item.title}</h4>
                    <p className="text-xs text-slate-400 leading-relaxed">{item.description}</p>
                    <p className="text-[11px] font-mono text-slate-500 pt-1 border-t border-slate-800/80">
                      ⚡ Macros: {item.macros}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 5-Item Indian Grocery Protocol */}
          <div className="p-4 sm:p-5 rounded-2xl bg-[#050811]/90 border border-cyan-500/20 space-y-3">
            <div className="flex items-center justify-between border-b border-cyan-500/15 pb-3">
              <div className="flex items-center gap-2">
                <ShoppingCart className="h-4 w-4 text-cyan-400" />
                <h3 className="text-xs font-mono uppercase tracking-widest text-white">
                  5-ITEM ESSENTIAL INDIAN GROCERY PROTOCOL
                </h3>
              </div>
              <button
                onClick={copyGroceryList}
                className="flex items-center gap-1.5 text-[11px] font-mono px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:text-white hover:border-cyan-400 transition-colors"
              >
                {copiedList ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{copiedList ? 'COPIED' : 'EXPORT LIST'}</span>
              </button>
            </div>

            <div className="space-y-2">
              {plan.grocery_list.map((item, idx) => {
                const isChecked = !!checkedGroceries[item.name];
                return (
                  <div
                    key={idx}
                    onClick={() => toggleGroceryItem(item.name)}
                    className={`flex items-start gap-3 p-3 rounded-xl border transition-all cursor-pointer ${
                      isChecked
                        ? 'bg-emerald-950/20 border-emerald-500/30 opacity-60'
                        : 'bg-slate-900/60 border-slate-800 hover:border-cyan-500/30'
                    }`}
                  >
                    <div className={`mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border ${
                      isChecked ? 'bg-emerald-500 border-emerald-500 text-slate-950' : 'border-slate-600'
                    }`}>
                      {isChecked && <Check className="h-3 w-3 stroke-[3]" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <span className={`text-xs sm:text-sm font-bold ${isChecked ? 'line-through text-slate-400' : 'text-white'}`}>
                          {item.name}
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 whitespace-nowrap">
                          {item.quantity_est}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-0.5">{item.benefit}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
