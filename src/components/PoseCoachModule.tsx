'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { 
  Camera as CameraIcon, 
  VideoOff, 
  Volume2, 
  VolumeX, 
  RotateCcw, 
  Sparkles, 
  Flame, 
  CheckCircle2, 
  AlertTriangle, 
  Activity, 
  Play, 
  Square, 
  HelpCircle,
  Eye,
  Settings2,
  SwitchCamera,
  Smartphone
} from 'lucide-react';
import confetti from 'canvas-confetti';

interface Landmark {
  x: number;
  y: number;
  z: number;
  visibility?: number;
}

export default function PoseCoachModule() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const cameraInstanceRef = useRef<any>(null);
  const poseInstanceRef = useRef<any>(null);

  // Application State
  const [isCameraActive, setIsCameraActive] = useState<boolean>(false);
  const [repCount, setRepCount] = useState<number>(0);
  const [currentAngle, setCurrentAngle] = useState<number>(180);
  const [stage, setStage] = useState<'UP' | 'DOWN' | 'TRANSITION'>('UP');
  const [feedback, setFeedback] = useState<string>('Stand tall to begin');
  const [depthAchieved, setDepthAchieved] = useState<boolean>(false);
  const [isAudioMuted, setIsAudioMuted] = useState<boolean>(false);
  const [trackedLeg, setTrackedLeg] = useState<'left' | 'right'>('left');
  const [isModelLoading, setIsModelLoading] = useState<boolean>(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [isSimulationMode, setIsSimulationMode] = useState<boolean>(false);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const [fps, setFps] = useState<number>(0);

  // References to keep state available in frame callbacks without re-triggering effects
  const stateRef = useRef({
    repCount: 0,
    depthAchieved: false,
    inDescent: false,
    isAudioMuted: false,
    lastSpokenTime: 0,
    lowestAngleThisRep: 180,
    trackedLeg: 'left' as 'left' | 'right'
  });

  // Sync ref with state
  useEffect(() => {
    stateRef.current.isAudioMuted = isAudioMuted;
  }, [isAudioMuted]);

  useEffect(() => {
    stateRef.current.trackedLeg = trackedLeg;
  }, [trackedLeg]);

  // Audio Speech Synthesis Feedback with Non-blocking Debounce
  const speakFeedback = useCallback((text: string, force: boolean = false) => {
    if (stateRef.current.isAudioMuted) return;
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;

    const now = Date.now();
    // Enforce minimum 1.3 seconds between speeches to avoid audio lag or stacking
    if (!force && now - stateRef.current.lastSpokenTime < 1300) return;
    if (window.speechSynthesis.speaking && !force) return;

    try {
      window.speechSynthesis.cancel(); // Clear any stale utterance
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.15; // Slightly faster for punchy workout pacing
      utterance.pitch = 1.05;
      utterance.volume = 0.9;
      stateRef.current.lastSpokenTime = now;
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn('Speech synthesis error:', e);
    }
  }, []);

  // Mathematical 2D Angle Calculation between Hip (A), Knee (B), and Ankle (C)
  const calculateKneeAngle = (a: Landmark, b: Landmark, c: Landmark): number => {
    const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
    let angle = Math.abs((radians * 180.0) / Math.PI);
    if (angle > 180.0) {
      angle = 360.0 - angle;
    }
    return Math.round(angle);
  };

  // Process MediaPipe Pose Results
  const onPoseResults = useCallback((results: any) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // 1. Draw raw video feed onto canvas
    ctx.save();
    ctx.clearRect(0, 0, width, height);
    ctx.drawImage(results.image, 0, 0, width, height);

    const landmarks: Landmark[] = results.poseLandmarks;

    if (!landmarks || landmarks.length === 0) {
      ctx.restore();
      setFeedback('Searching for lifter in frame...');
      return;
    }

    // 2. High-Accuracy Visibility Filter: Filter landmarks with visibility < 0.65
    const VISIBILITY_THRESHOLD = 0.65;
    const filteredLandmarks = landmarks.map((lm) => {
      const isVisible = lm && (lm.visibility === undefined || lm.visibility >= VISIBILITY_THRESHOLD);
      return isVisible ? lm : { ...lm, visibility: 0 };
    });

    // 3. Draw virtual joints & skeletal connections using MediaPipe drawing utils
    const windowAny = window as any;
    if (windowAny.drawConnectors && windowAny.POSE_CONNECTIONS && windowAny.drawLandmarks) {
      // Connectors with glowing teal/emerald
      windowAny.drawConnectors(ctx, filteredLandmarks, windowAny.POSE_CONNECTIONS, {
        color: '#14b8a6',
        lineWidth: 3
      });

      // Joint Landmarks with glowing circles
      windowAny.drawLandmarks(ctx, filteredLandmarks, {
        color: '#22c55e',
        fillColor: '#0a0f1d',
        lineWidth: 2,
        radius: 4
      });
    }

    // 4. Select Landmarks for Knee Angle Calculation:
    // Left: 23 (LEFT_HIP), 25 (LEFT_KNEE), 27 (LEFT_ANKLE)
    // Right: 24 (RIGHT_HIP), 26 (RIGHT_KNEE), 28 (RIGHT_ANKLE)
    const isLeft = stateRef.current.trackedLeg === 'left';
    const hipIdx = isLeft ? 23 : 24;
    const kneeIdx = isLeft ? 25 : 26;
    const ankleIdx = isLeft ? 27 : 28;

    const hip = landmarks[hipIdx];
    const knee = landmarks[kneeIdx];
    const ankle = landmarks[ankleIdx];

    const hipVisible = hip && (hip.visibility ?? 1) >= VISIBILITY_THRESHOLD;
    const kneeVisible = knee && (knee.visibility ?? 1) >= VISIBILITY_THRESHOLD;
    const ankleVisible = ankle && (ankle.visibility ?? 1) >= VISIBILITY_THRESHOLD;

    if (hipVisible && kneeVisible && ankleVisible) {
      // Calculate knee joint angle
      const angle = calculateKneeAngle(hip, knee, ankle);
      setCurrentAngle(angle);

      // Track lowest angle reached during current repetition
      if (angle < stateRef.current.lowestAngleThisRep) {
        stateRef.current.lowestAngleThisRep = angle;
      }

      // Convert normalized coordinates (0..1) to canvas pixel coordinates
      const kneeX = knee.x * width;
      const kneeY = knee.y * height;
      const hipX = hip.x * width;
      const hipY = hip.y * height;

      // Draw highlighted tracking lines for the active squat leg
      ctx.beginPath();
      ctx.moveTo(hipX, hipY);
      ctx.lineTo(kneeX, kneeY);
      ctx.lineTo(ankle.x * width, ankle.y * height);
      ctx.lineWidth = 6;
      ctx.strokeStyle = angle <= 95 ? '#22c55e' : angle < 140 ? '#06b6d4' : '#f59e0b';
      ctx.stroke();

      // Draw glowing angle badge directly next to the active knee joint
      ctx.beginPath();
      ctx.arc(kneeX, kneeY, 12, 0, 2 * Math.PI);
      ctx.fillStyle = angle <= 95 ? '#22c55e' : '#14b8a6';
      ctx.fill();
      ctx.lineWidth = 3;
      ctx.strokeStyle = '#ffffff';
      ctx.stroke();

      // Render angle label on canvas
      ctx.fillStyle = '#0a0f1d';
      ctx.fillRect(kneeX + 15, kneeY - 20, 70, 26);
      ctx.lineWidth = 1;
      ctx.strokeStyle = angle <= 95 ? '#22c55e' : '#14b8a6';
      ctx.strokeRect(kneeX + 15, kneeY - 20, 70, 26);
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 14px monospace';
      ctx.fillText(`${angle}°`, kneeX + 25, kneeY - 2);

      // -------------------------------------------------------------
      // SQUAT REP STATE MACHINE:
      // Depth condition: Angle dips below 95 degrees
      // Full extension condition: Returns above 160 degrees
      // -------------------------------------------------------------
      if (angle <= 95) {
        // Deep Squat Target reached!
        if (!stateRef.current.depthAchieved) {
          stateRef.current.depthAchieved = true;
          setDepthAchieved(true);
          setStage('DOWN');
          setFeedback('Depth hit (<95°)! Drive through heels!');
        }
      } else if (angle < 140) {
        // Lifter is in descent
        stateRef.current.inDescent = true;
        setStage('TRANSITION');
        if (!stateRef.current.depthAchieved) {
          setFeedback('Descend lower... break 95°');
        }
      } else if (angle >= 160) {
        // Lifter returned to standing position (> 160°)
        setStage('UP');

        if (stateRef.current.depthAchieved) {
          // Successful Rep Completed!
          const newRep = stateRef.current.repCount + 1;
          stateRef.current.repCount = newRep;
          setRepCount(newRep);
          stateRef.current.depthAchieved = false;
          stateRef.current.inDescent = false;
          stateRef.current.lowestAngleThisRep = 180;
          setDepthAchieved(false);
          setFeedback(`Good rep! (${newRep})`);

          // Audio reinforcement
          speakFeedback('Good rep', true);

          // Milestone celebrations
          if (newRep > 0 && newRep % 5 === 0) {
            confetti({
              particleCount: 80,
              spread: 70,
              origin: { y: 0.6 }
            });
          }
        } else if (stateRef.current.inDescent && stateRef.current.lowestAngleThisRep > 95) {
          // User turned around without hitting 95 degrees!
          stateRef.current.inDescent = false;
          stateRef.current.lowestAngleThisRep = 180;
          setFeedback('Incomplete depth! Go lower!');
          speakFeedback('Go lower');
        } else {
          setFeedback('Ready for next rep. Keep chest proud.');
        }
      }
    } else {
      setFeedback(`Low landmark visibility on ${isLeft ? 'left' : 'right'} leg. Adjust lighting or angle.`);
    }

    ctx.restore();
  }, [speakFeedback]);

  // Start Camera and Initialize MediaPipe Pose
  const startCamera = async (mode?: 'user' | 'environment') => {
    setIsModelLoading(true);
    setCameraError(null);
    const activeFacing = (typeof mode === 'string' && (mode === 'user' || mode === 'environment')) ? mode : facingMode;

    try {
      const videoElement = videoRef.current;
      const canvasElement = canvasRef.current;
      if (!videoElement || !canvasElement) return;

      const windowAny = window as any;

      // Verify that Pose and Camera are loaded
      let PoseClass = windowAny.Pose;
      let CameraClass = windowAny.Camera;

      if (!PoseClass) {
        // Fallback dynamic import from npm
        const poseModule = await import('@mediapipe/pose');
        PoseClass = poseModule.Pose || windowAny.Pose;
      }
      if (!CameraClass) {
        const camModule = await import('@mediapipe/camera_utils');
        CameraClass = camModule.Camera || windowAny.Camera;
      }

      if (!PoseClass || !CameraClass) {
        throw new Error('MediaPipe Pose scripts still initializing. Please wait a second.');
      }

      // Initialize Pose Model
      const pose = new PoseClass({
        locateFile: (file: string) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
      });

      pose.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: false,
        smoothSegmentation: false,
        minDetectionConfidence: 0.65,
        minTrackingConfidence: 0.65
      });

      pose.onResults(onPoseResults);
      poseInstanceRef.current = pose;

      // Initialize WebCam Camera stream with facingMode
      const camera = new CameraClass(videoElement, {
        onFrame: async () => {
          if (videoRef.current && poseInstanceRef.current) {
            await poseInstanceRef.current.send({ image: videoRef.current });
          }
        },
        width: 640,
        height: 480,
        facingMode: activeFacing
      });

      await camera.start();
      cameraInstanceRef.current = camera;
      setIsCameraActive(true);
      setIsSimulationMode(false);
      setFeedback('Camera active. Step back until your hips and knees are visible.');
    } catch (err) {
      console.error('Camera initialization error:', err);
      setCameraError(err instanceof Error ? err.message : 'Webcam access failed. Note: Mobile browsers require HTTPS or localhost to enable camera permission.');
    } finally {
      setIsModelLoading(false);
    }
  };

  // Flip Camera (Front / Rear for mobile)
  const toggleCameraFacing = async () => {
    const nextMode = facingMode === 'user' ? 'environment' : 'user';
    setFacingMode(nextMode);
    if (isCameraActive) {
      stopCamera();
      setTimeout(() => {
        startCamera(nextMode);
      }, 300);
    }
  };

  // Stop Camera
  const stopCamera = () => {
    if (cameraInstanceRef.current) {
      try {
        cameraInstanceRef.current.stop();
      } catch (e) {
        console.warn(e);
      }
      cameraInstanceRef.current = null;
    }
    if (poseInstanceRef.current) {
      try {
        poseInstanceRef.current.close();
      } catch (e) {
        console.warn(e);
      }
      poseInstanceRef.current = null;
    }
    setIsCameraActive(false);
    setFeedback('Camera stopped.');
  };

  // Simulation Mode for testing without physical webcam hardware
  useEffect(() => {
    if (!isSimulationMode) return;

    let animationId: number;
    let simAngle = 175;
    let simDirection = -1; // -1 = descending, +1 = ascending

    const simLoop = () => {
      const canvas = canvasRef.current;
      if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.fillStyle = '#0f172a';
          ctx.fillRect(0, 0, canvas.width, canvas.height);

          // Simulated stick figure kinematics
          const hipX = canvas.width / 2;
          const hipY = 160 + (180 - simAngle) * 0.9;
          const kneeX = canvas.width / 2 + 50;
          const kneeY = 280;
          const ankleX = canvas.width / 2;
          const ankleY = 400;

          // Leg joints
          ctx.beginPath();
          ctx.moveTo(hipX, hipY);
          ctx.lineTo(kneeX, kneeY);
          ctx.lineTo(ankleX, ankleY);
          ctx.lineWidth = 6;
          ctx.strokeStyle = simAngle <= 95 ? '#22c55e' : '#14b8a6';
          ctx.stroke();

          // Knee circle
          ctx.beginPath();
          ctx.arc(kneeX, kneeY, 12, 0, 2 * Math.PI);
          ctx.fillStyle = simAngle <= 95 ? '#22c55e' : '#14b8a6';
          ctx.fill();

          // Angle badge
          ctx.fillStyle = '#ffffff';
          ctx.font = 'bold 18px monospace';
          ctx.fillText(`${Math.round(simAngle)}°`, kneeX + 25, kneeY);

          // Depth guideline
          ctx.setLineDash([6, 6]);
          ctx.strokeStyle = 'rgba(34, 197, 94, 0.4)';
          ctx.beginPath();
          ctx.moveTo(40, 280);
          ctx.lineTo(canvas.width - 40, 280);
          ctx.stroke();
          ctx.setLineDash([]);
          ctx.fillStyle = '#22c55e';
          ctx.font = '11px sans-serif';
          ctx.fillText('PARALLEL DEPTH (95°)', 50, 272);
        }
      }

      // Simulate motion
      if (simDirection === -1) {
        simAngle -= 1.8;
        if (simAngle <= 88) {
          simDirection = 1;
          stateRef.current.depthAchieved = true;
          setDepthAchieved(true);
          setStage('DOWN');
          setFeedback('Depth hit (88°)! Driving up!');
        }
      } else {
        simAngle += 2.0;
        if (simAngle >= 168) {
          simDirection = -1;
          setStage('UP');
          if (stateRef.current.depthAchieved) {
            const nextRep = stateRef.current.repCount + 1;
            stateRef.current.repCount = nextRep;
            setRepCount(nextRep);
            stateRef.current.depthAchieved = false;
            setDepthAchieved(false);
            setFeedback(`Good rep! (${nextRep})`);
            speakFeedback('Good rep', true);
            if (nextRep % 5 === 0) {
              confetti({ particleCount: 60, spread: 60, origin: { y: 0.6 } });
            }
          }
        }
      }

      setCurrentAngle(Math.round(simAngle));
      animationId = requestAnimationFrame(simLoop);
    };

    animationId = requestAnimationFrame(simLoop);

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [isSimulationMode, speakFeedback]);

  // Clean up camera on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const resetWorkout = () => {
    stateRef.current.repCount = 0;
    stateRef.current.depthAchieved = false;
    stateRef.current.inDescent = false;
    stateRef.current.lowestAngleThisRep = 180;
    setRepCount(0);
    setDepthAchieved(false);
    setFeedback('Workout counter reset to 0.');
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-4 space-y-5">
      {/* Module Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-500/10 border border-teal-500/30 text-teal-400">
              <CameraIcon className="h-5 w-5" />
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
              High-Accuracy AI Pose Coach
            </h2>
            <span className="rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
              100% Client-Side Vision
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Zero video latency. Zero server data transmission. Real-time joint kinematics & speech synthesis audio coach.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {/* Mute Toggle */}
          <button
            onClick={() => setIsAudioMuted(!isAudioMuted)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition ${
              isAudioMuted
                ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                : 'bg-teal-500/10 text-teal-300 border-teal-500/30'
            }`}
          >
            {isAudioMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
            <span>{isAudioMuted ? 'Muted' : 'Voice Coach'}</span>
          </button>

          {/* Flip Camera (Front / Rear for Mobile) */}
          <button
            onClick={toggleCameraFacing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-teal-300 border border-slate-700 transition"
            title="Flip Camera (Selfie / Rear)"
          >
            <SwitchCamera className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">{facingMode === 'user' ? 'Front' : 'Rear'}</span>
          </button>

          {/* Reset Reps */}
          <button
            onClick={resetWorkout}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 transition"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Main Viewport Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Canvas + Live HUD */}
        <div className="lg:col-span-8 flex flex-col items-center">
          <div className="relative w-full aspect-[4/3] max-w-[640px] rounded-2xl overflow-hidden bg-slate-950 border border-slate-800 shadow-2xl flex items-center justify-center">
            {/* Hidden Video Feed that feeds MediaPipe */}
            <video
              ref={videoRef}
              playsInline
              muted
              className="hidden"
            />

            {/* HTML5 Canvas with skeleton overlaid on webcam frames */}
            <canvas
              ref={canvasRef}
              width={640}
              height={480}
              className="w-full h-full object-cover"
            />

            {/* Overlay: Inactive State Banner */}
            {!isCameraActive && !isSimulationMode && (
              <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center bg-slate-950/90 backdrop-blur-sm space-y-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-teal-500/10 text-teal-400 border border-teal-500/30 shadow-glow-teal">
                  <CameraIcon className="h-8 w-8" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Activate Real-Time Squat Tracker</h3>
                  <p className="text-xs text-slate-400 max-w-sm mt-1">
                    Operates entirely inside your browser via MediaPipe Pose. No frames are ever uploaded.
                  </p>
                </div>

                <div className="flex flex-wrap items-center justify-center gap-3">
                  <button
                    onClick={() => startCamera()}
                    disabled={isModelLoading}
                    className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 px-5 py-2.5 text-sm font-bold text-slate-950 hover:opacity-95 transition shadow-glow-teal disabled:opacity-50"
                  >
                    {isModelLoading ? (
                      <>
                        <Sparkles className="h-4 w-4 animate-spin" />
                        <span>Initializing Vision Model...</span>
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 fill-slate-950" />
                        <span>Start Camera Coach</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => {
                      stopCamera();
                      setIsSimulationMode(true);
                      setFeedback('Simulation Active: Simulating squat repetitions at 60 FPS.');
                    }}
                    className="flex items-center gap-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-teal-300 border border-teal-500/30 px-4 py-2.5 text-xs font-bold transition"
                  >
                    <Eye className="h-4 w-4" />
                    <span>Run Test Simulation</span>
                  </button>
                </div>

                {cameraError && (
                  <div className="mt-2 rounded-xl bg-amber-950/50 border border-amber-500/30 p-3 text-xs text-amber-300 max-w-md">
                    <p className="font-semibold flex items-center justify-center gap-1">
                      <AlertTriangle className="h-4 w-4" /> Notice
                    </p>
                    <p className="mt-1">{cameraError}</p>
                  </div>
                )}
              </div>
            )}

            {/* Live On-Screen HUD Overlay (When Active) */}
            {(isCameraActive || isSimulationMode) && (
              <>
                {/* Top HUD: Status Bar */}
                <div className="absolute top-3 left-3 right-3 flex items-center justify-between pointer-events-none">
                  {/* Rep Badge */}
                  <div className="flex items-center gap-3 rounded-xl bg-slate-950/85 backdrop-blur-md px-4 py-2 border border-teal-500/40 shadow-glow-teal">
                    <span className="text-xs font-bold uppercase tracking-wider text-teal-400">Reps</span>
                    <span className="text-3xl font-black text-white">{repCount}</span>
                  </div>

                  {/* Knee Angle Live Gauge */}
                  <div className={`flex items-center gap-2 rounded-xl bg-slate-950/85 backdrop-blur-md px-3.5 py-2 border transition ${
                    currentAngle <= 95 ? 'border-emerald-500 text-emerald-400' : 'border-slate-800 text-white'
                  }`}>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Angle</span>
                    <span className="text-2xl font-black font-mono">{currentAngle}°</span>
                    <span className="text-[10px] text-slate-400">(Target &lt;95°)</span>
                  </div>
                </div>

                {/* Bottom HUD: Live Feedback Coach Pill */}
                <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between pointer-events-none">
                  <div className={`flex items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold backdrop-blur-md border ${
                    depthAchieved
                      ? 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50'
                      : stage === 'TRANSITION'
                      ? 'bg-cyan-950/90 text-cyan-300 border-cyan-500/40'
                      : 'bg-slate-950/90 text-slate-200 border-slate-800'
                  }`}>
                    <Activity className="h-4 w-4 shrink-0 animate-pulse" />
                    <span>{feedback}</span>
                  </div>

                  {/* Stop Camera Button */}
                  <div className="pointer-events-auto">
                    <button
                      onClick={() => {
                        stopCamera();
                        setIsSimulationMode(false);
                      }}
                      className="flex items-center gap-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 px-3 py-1.5 text-xs font-bold transition"
                    >
                      <Square className="h-3.5 w-3.5 fill-rose-300" />
                      <span>Stop</span>
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Right Column: Coaching Metrics & Kinematics Guide */}
        <div className="lg:col-span-4 space-y-4">
          {/* Real-Time Depth Meter */}
          <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-xl space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
              <span>Squat Depth Progress</span>
              <span className={`text-xs font-bold ${currentAngle <= 95 ? 'text-emerald-400' : 'text-slate-400'}`}>
                {currentAngle <= 95 ? 'DEPTH ACHIEVED' : `${Math.max(0, currentAngle - 95)}° TO PARALLEL`}
              </span>
            </h3>

            {/* Depth Gauge Bar */}
            <div className="relative w-full bg-slate-950 h-5 rounded-full overflow-hidden border border-slate-800">
              {/* Target 95° marker */}
              <div className="absolute left-[52%] top-0 bottom-0 w-0.5 bg-emerald-400 z-10" />
              {/* Progress fill (inverted: 180° = 0%, 95° = 52%, 70° = 100%) */}
              <div
                className={`h-full transition-all duration-100 ${
                  currentAngle <= 95
                    ? 'bg-gradient-to-r from-teal-500 to-emerald-400'
                    : 'bg-gradient-to-r from-slate-700 to-cyan-500'
                }`}
                style={{
                  width: `${Math.min(100, Math.max(0, ((180 - currentAngle) / (180 - 80)) * 100))}%`
                }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>Standing (180°)</span>
              <span className="text-emerald-400 font-bold">Target (&lt;95°)</span>
              <span>Deep (70°)</span>
            </div>
          </div>

          {/* Tracking Configuration */}
          <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-xl space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Settings2 className="h-4 w-4 text-teal-400" /> Tracking Settings
            </h3>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Active Tracking Leg
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setTrackedLeg('left')}
                  className={`rounded-xl py-2 px-3 text-xs font-bold transition border ${
                    trackedLeg === 'left'
                      ? 'bg-teal-500/20 text-teal-300 border-teal-500/50 shadow-glow-teal'
                      : 'bg-slate-950 text-slate-400 border-slate-800'
                  }`}
                >
                  Left Leg (23-25-27)
                </button>
                <button
                  onClick={() => setTrackedLeg('right')}
                  className={`rounded-xl py-2 px-3 text-xs font-bold transition border ${
                    trackedLeg === 'right'
                      ? 'bg-teal-500/20 text-teal-300 border-teal-500/50 shadow-glow-teal'
                      : 'bg-slate-950 text-slate-400 border-slate-800'
                  }`}
                >
                  Right Leg (24-26-28)
                </button>
              </div>
            </div>

            <div className="rounded-xl bg-slate-950/80 p-3 border border-slate-800 text-xs text-slate-300 space-y-1.5">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-400">Visibility Filter:</span>
                <span className="text-emerald-400 font-mono font-bold">&gt; 0.65 score</span>
              </div>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-400">Depth Trigger:</span>
                <span className="text-teal-400 font-mono font-bold">&lt; 95°</span>
              </div>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-400">Return Trigger:</span>
                <span className="text-indigo-400 font-mono font-bold">&gt; 160°</span>
              </div>
            </div>
          </div>

          {/* Form Coaching & Kinematics Checklist */}
          <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-950 border border-teal-500/20 p-5 shadow-xl space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-teal-400" /> Biomechanical Checklist
            </h3>

            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-start gap-2">
                <span className="text-teal-400 font-bold">•</span>
                <span>
                  <strong className="text-white">Camera Angle:</strong> Position camera 6 to 9 feet away at hip-height facing your profile side.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-teal-400 font-bold">•</span>
                <span>
                  <strong className="text-white">Depth Parallel:</strong> Descend until your hip crease breaks below the top of your patella (&lt; 95°).
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-teal-400 font-bold">•</span>
                <span>
                  <strong className="text-white">Lockout:</strong> Stand tall and lock out your hips (&gt; 160°) to log the repetition credit.
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
