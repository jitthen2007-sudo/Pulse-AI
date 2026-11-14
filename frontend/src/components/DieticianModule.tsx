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
  ChevronRight, 
  Copy, 
  Check, 
  PieChart, 
  HeartHandshake 
} from 'lucide-react';

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

export default function DieticianModule() {
  const [weightKg, setWeightKg] = useState<number>(74);
  const [heightCm, setHeightCm] = useState<number>(178);
  const [goal, setGoal] = useState<string>('Lean Muscle Bulk');
  const [preference, setPreference] = useState<string>('Non-Veg');
  const [targetCalories, setTargetCalories] = useState<string>('');
  
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [plan, setPlan] = useState<NutritionResponse | null>(null);
  const [checkedGroceries, setCheckedGroceries] = useState<{ [key: string]: boolean }>({});
  const [copiedList, setCopiedList] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg(null);

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

      if (!response.ok) {
        throw new Error(`Server status: ${response.status}`);
      }

      const data: NutritionResponse = await response.json();
      setPlan(data);
      setCheckedGroceries({});
    } catch (err) {
      console.error(err);
      setErrorMsg(err instanceof Error ? err.message : 'Failed to generate nutrition strategy');
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
    navigator.clipboard.writeText(`🛒 Pulse AI Curated Grocery List:\n\n${text}`);
    setCopiedList(true);
    setTimeout(() => setCopiedList(false), 2500);
  };

  // BMI status color helper
  const getBmiBadge = (cat: string) => {
    switch (cat.toLowerCase()) {
      case 'normal weight':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'underweight':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'overweight':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      default:
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-500/10 border border-teal-500/30 text-teal-400">
              <Utensils className="h-5 w-5" />
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
              AI Dietician & Nutritionist
            </h2>
            <span className="rounded-full bg-teal-500/10 px-2.5 py-0.5 text-xs font-semibold text-teal-400 border border-teal-500/20">
              Gemini Powered
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Precision clinical metabolic calculations, bespoke meal plans, and a targeted 5-item grocery list.
          </p>
        </div>
      </div>

      {/* Main Grid: Form on Left, Output on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Form Column */}
        <div className="lg:col-span-4 space-y-4">
          <form
            onSubmit={handleSubmit}
            className="rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-xl space-y-4"
          >
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Scale className="h-4 w-4 text-teal-400" /> Biometric Profile
            </h3>

            {/* Weight */}
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                <span>Weight</span>
                <span className="text-teal-400 font-bold">{weightKg} kg</span>
              </div>
              <input
                type="range"
                min="40"
                max="160"
                step="1"
                value={weightKg}
                onChange={(e) => setWeightKg(Number(e.target.value))}
                className="w-full accent-teal-400 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                <span>40 kg</span>
                <span>100 kg</span>
                <span>160 kg</span>
              </div>
            </div>

            {/* Height */}
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                <span>Height</span>
                <span className="text-teal-400 font-bold">{heightCm} cm</span>
              </div>
              <input
                type="range"
                min="140"
                max="220"
                step="1"
                value={heightCm}
                onChange={(e) => setHeightCm(Number(e.target.value))}
                className="w-full accent-teal-400 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                <span>140 cm</span>
                <span>180 cm</span>
                <span>220 cm</span>
              </div>
            </div>

            {/* Goal Selector */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Primary Goal
              </label>
              <select
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                className="w-full rounded-xl bg-slate-950 border border-slate-700 px-3 py-2 text-sm text-slate-200 focus:border-teal-500 focus:outline-none"
              >
                <option value="Fat Loss & Shred">Fat Loss & Shred (Caloric Deficit)</option>
                <option value="Lean Muscle Bulk">Lean Muscle Bulk (Clean Surplus)</option>
                <option value="Athletic Recomposition">Body Recomposition (Maintenance)</option>
                <option value="Strength & Power">Strength & Power (High Carb Fuel)</option>
                <option value="Endurance & Stamina">Endurance & Glycogen Optimization</option>
              </select>
            </div>

            {/* Dietary Preference */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Dietary Preference
              </label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: 'Non-Veg', label: '🥩 Non-Veg' },
                  { id: 'Veg', label: '🥦 Veg' },
                  { id: 'Vegan', label: '🌱 Vegan' },
                  { id: 'Keto', label: '🥑 Keto' },
                ].map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setPreference(item.id)}
                    className={`rounded-xl px-3 py-2 text-xs font-medium text-left transition border ${
                      preference === item.id
                        ? 'bg-teal-500/20 text-teal-300 border-teal-500/50 shadow-glow-teal'
                        : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Optional Target Calories */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Target Daily Calories (Optional)
              </label>
              <input
                type="number"
                placeholder="Auto-calculated if blank"
                value={targetCalories}
                onChange={(e) => setTargetCalories(e.target.value)}
                className="w-full rounded-xl bg-slate-950 border border-slate-700 px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:border-teal-500 focus:outline-none"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 py-3 text-sm font-bold text-slate-950 transition hover:opacity-95 disabled:opacity-50 shadow-glow-teal"
            >
              {isLoading ? (
                <>
                  <Sparkles className="h-4 w-4 animate-spin" />
                  <span>Synthesizing Nutrition Protocol...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  <span>Generate AI Diet Strategy</span>
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

        {/* Results Column */}
        <div className="lg:col-span-8 space-y-6">
          {!plan && !isLoading && (
            <div className="rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 p-10 text-center flex flex-col items-center justify-center min-h-[400px]">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-500/10 text-teal-400 mb-4">
                <Utensils className="h-7 w-7" />
              </div>
              <h3 className="text-lg font-bold text-white">Your Tailored Fuel Strategy Awaits</h3>
              <p className="text-sm text-slate-400 max-w-md mt-1">
                Select your body metrics and nutritional preferences on the left. Pulse AI will compute your exact BMI, macronutrient balance, daily meal plan, and 5-item grocery cart.
              </p>
            </div>
          )}

          {isLoading && (
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-10 text-center flex flex-col items-center justify-center min-h-[400px] animate-pulse">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-500/20 text-teal-400 mb-4 animate-spin">
                <Sparkles className="h-7 w-7" />
              </div>
              <h3 className="text-lg font-bold text-white">Calculating Metabolic Energetics...</h3>
              <p className="text-sm text-teal-400 mt-1">Calibrating amino acid profiles and thermic effects of food with Gemini.</p>
            </div>
          )}

          {plan && !isLoading && (
            <div className="space-y-6 animate-fade-in">
              {/* Card 1: BMI & Strategy Overview */}
              <div className="rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900/95 to-slate-950 border border-teal-500/30 p-5 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-teal-500/5 rounded-full blur-2xl pointer-events-none" />

                <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                  <div className="flex items-center gap-3">
                    <div className="flex flex-col">
                      <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                        Calculated Body Mass Index
                      </span>
                      <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-black text-white">{plan.bmi}</span>
                        <span className="text-sm text-slate-400">kg/m²</span>
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getBmiBadge(plan.bmi_category)}`}>
                          {plan.bmi_category}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                      Target Energy
                    </span>
                    <div className="text-2xl font-black text-teal-400 flex items-center gap-1 justify-end">
                      <Flame className="h-5 w-5 text-amber-400" />
                      <span>{plan.daily_calories}</span>
                      <span className="text-xs text-slate-400 font-normal">kcal/day</span>
                    </div>
                  </div>
                </div>

                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                  <strong className="text-teal-300">Clinical Insights:</strong> {plan.bmi_analysis}
                </p>

                {/* Strategy Summary */}
                <p className="text-xs text-slate-400 mt-3 italic">
                  💡 {plan.strategy_summary}
                </p>
              </div>

              {/* Card 2: Macronutrient Breakdown */}
              <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-xl space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <PieChart className="h-4 w-4 text-teal-400" /> Daily Macronutrient Target
                </h3>

                <div className="grid grid-cols-3 gap-3">
                  {/* Protein */}
                  <div className="rounded-xl bg-slate-950/80 p-3.5 border border-indigo-500/20 text-center">
                    <span className="text-[11px] font-semibold text-indigo-400 uppercase">Protein</span>
                    <p className="text-xl sm:text-2xl font-black text-white mt-1">{plan.macros.protein_g}g</p>
                    <span className="text-[10px] text-slate-400">{plan.macros.protein_pct}% of total</span>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${plan.macros.protein_pct}%` }} />
                    </div>
                  </div>

                  {/* Carbs */}
                  <div className="rounded-xl bg-slate-950/80 p-3.5 border border-teal-500/20 text-center">
                    <span className="text-[11px] font-semibold text-teal-400 uppercase">Carbohydrates</span>
                    <p className="text-xl sm:text-2xl font-black text-white mt-1">{plan.macros.carbs_g}g</p>
                    <span className="text-[10px] text-slate-400">{plan.macros.carbs_pct}% of total</span>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div className="bg-teal-400 h-full rounded-full" style={{ width: `${plan.macros.carbs_pct}%` }} />
                    </div>
                  </div>

                  {/* Fats */}
                  <div className="rounded-xl bg-slate-950/80 p-3.5 border border-amber-500/20 text-center">
                    <span className="text-[11px] font-semibold text-amber-400 uppercase">Fats</span>
                    <p className="text-xl sm:text-2xl font-black text-white mt-1">{plan.macros.fats_g}g</p>
                    <span className="text-[10px] text-slate-400">{plan.macros.fats_pct}% of total</span>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div className="bg-amber-400 h-full rounded-full" style={{ width: `${plan.macros.fats_pct}%` }} />
                    </div>
                  </div>
                </div>
              </div>

              {/* Card 3: Meal Plan Timeline */}
              <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-xl space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <Clock className="h-4 w-4 text-teal-400" /> Daily Meal Architecture
                </h3>

                <div className="space-y-3">
                  {Object.entries(plan.meal_plan).map(([key, meal]) => {
                    if (!meal) return null;
                    const labels: { [k: string]: { name: string; icon: string } } = {
                      breakfast: { name: 'Breakfast', icon: '🌅' },
                      lunch: { name: 'Lunch', icon: '☀️' },
                      snack: { name: 'Afternoon Fuel', icon: '🍎' },
                      dinner: { name: 'Dinner', icon: '🌙' },
                      pre_post_workout: { name: 'Training Nutrition', icon: '⚡' }
                    };
                    const meta = labels[key] || { name: key, icon: '🍽️' };

                    return (
                      <div
                        key={key}
                        className="rounded-xl bg-slate-950/70 border border-slate-800/80 p-3.5 transition hover:border-teal-500/30"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                          <div className="flex items-center gap-2">
                            <span className="text-base">{meta.icon}</span>
                            <span className="text-xs font-bold uppercase tracking-wide text-teal-400">
                              {meta.name}
                            </span>
                            <span className="text-sm font-semibold text-white">
                              — {meal.title}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 text-xs">
                            <span className="rounded-md bg-slate-900 px-2 py-0.5 text-amber-300 font-semibold border border-amber-500/20">
                              {meal.calories} kcal
                            </span>
                            <span className="text-slate-400 text-[11px] font-mono">
                              {meal.macros}
                            </span>
                          </div>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed pl-6">
                          {meal.description}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Card 4: 5-Item Curated Grocery List */}
              <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-950 border border-teal-500/30 p-5 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ShoppingCart className="h-5 w-5 text-teal-400" />
                    <div>
                      <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                        5-Item Curated Grocery List
                      </h3>
                      <p className="text-xs text-slate-400">Everything needed for this protocol in one high-efficiency haul.</p>
                    </div>
                  </div>

                  <button
                    onClick={copyGroceryList}
                    className="flex items-center gap-1.5 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 text-teal-300 border border-teal-500/30 px-3 py-1.5 text-xs font-semibold transition"
                  >
                    {copiedList ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                    <span>{copiedList ? 'Copied!' : 'Copy List'}</span>
                  </button>
                </div>

                <div className="space-y-2.5">
                  {plan.grocery_list.map((item, idx) => {
                    const isChecked = !!checkedGroceries[item.name];
                    return (
                      <div
                        key={idx}
                        onClick={() => toggleGroceryItem(item.name)}
                        className={`flex items-start gap-3 rounded-xl p-3 border cursor-pointer transition ${
                          isChecked
                            ? 'bg-slate-950/40 border-slate-800/50 opacity-60'
                            : 'bg-slate-950/90 border-slate-800 hover:border-teal-500/40'
                        }`}
                      >
                        <div className="mt-0.5">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => {}}
                            className="rounded accent-teal-400 h-4 w-4 cursor-pointer"
                          />
                        </div>
                        <div className="flex-1">
                          <div className="flex flex-wrap items-center justify-between gap-1">
                            <span className={`text-sm font-bold ${isChecked ? 'line-through text-slate-500' : 'text-white'}`}>
                              {item.name}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] text-teal-400 bg-teal-950/60 px-2 py-0.5 rounded-md border border-teal-500/20">
                                {item.category}
                              </span>
                              <span className="text-xs text-slate-400 font-medium">
                                {item.quantity_est}
                              </span>
                            </div>
                          </div>
                          <p className={`text-xs mt-1 ${isChecked ? 'text-slate-500' : 'text-slate-400'}`}>
                            {item.benefit}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Card 5: Hydration & Timing */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-4 flex items-start gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    <Droplets className="h-5 w-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-300">
                      Hydration Protocol
                    </h4>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                      {plan.hydration_tip}
                    </p>
                  </div>
                </div>

                <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-4 flex items-start gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
                    <Clock className="h-5 w-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-teal-300">
                      Nutrient Timing Window
                    </h4>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                      {plan.timing_tip}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
