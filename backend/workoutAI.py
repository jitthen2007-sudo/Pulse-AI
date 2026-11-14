"""
workoutAI.py - Reference Computer Vision & Biomechanics Logic
=============================================================
CRITICAL ARCHITECTURAL DECISION:
Streaming live OpenCV video frames from Python to a browser over HTTP/WebSocket 
introduces 80-250ms of network latency, frame drops, and heavy server loads.

To achieve 60 FPS lag-free performance with zero server CPU cost and 100% user privacy,
the core logic in this file has been directly translated into a modern React component:
--> frontend/src/components/PoseCoachModule.tsx

Kinematic Algorithm:
1. MediaPipe Pose 33-point Landmark Detection:
   - Left Hip: Landmark Index 23
   - Left Knee: Landmark Index 25
   - Left Ankle: Landmark Index 27
2. Confidence Filter:
   - Reject any landmark frame where visibility score < 0.65
3. 2D Joint Angle Calculation:
   - radians = arctan2(c.y - b.y, c.x - b.x) - arctan2(a.y - b.y, a.x - b.x)
   - angle = abs(radians * 180.0 / PI)
   - if angle > 180.0: angle = 360.0 - angle
4. State Machine:
   - Squat Down (Depth Trigger): Angle dips below 95° -> stage = "down"
   - Squat Up (Rep Trigger): Angle rises above 160° from "down" -> stage = "up", rep_count += 1
5. Audio Coaching:
   - window.speechSynthesis.speak() on client-side for immediate voice feedback ("Good rep", "Go lower").
"""

import math

def calculate_angle(a, b, c):
    """
    Calculate 2D angle between three joints: a (hip), b (knee), c (ankle).
    Each point has 'x' and 'y' coordinates in [0.0, 1.0].
    """
    radians = math.atan2(c['y'] - b['y'], c['x'] - b['x']) - math.atan2(a['y'] - b['y'], a['x'] - b['x'])
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return round(angle, 1)

class SquatRepStateMachine:
    def __init__(self, depth_threshold=95.0, extension_threshold=160.0):
        self.depth_threshold = depth_threshold
        self.extension_threshold = extension_threshold
        self.counter = 0
        self.stage = "up"
        self.feedback = "Stand straight and begin"

    def process_frame(self, hip, knee, ankle, min_visibility=0.65):
        # Check visibility confidence
        if hip.get('visibility', 1.0) < min_visibility or \
           knee.get('visibility', 1.0) < min_visibility or \
           ankle.get('visibility', 1.0) < min_visibility:
            self.feedback = "Keep full body visible"
            return None, self.counter, self.feedback

        angle = calculate_angle(hip, knee, ankle)

        # State transition: descent into squat
        if angle < self.depth_threshold:
            if self.stage != "down":
                self.stage = "down"
                self.feedback = "Good depth! Now drive up"
        elif angle > self.extension_threshold:
            if self.stage == "down":
                self.stage = "up"
                self.counter += 1
                self.feedback = "Rep completed! Good job"
            else:
                self.feedback = "Squat down below 95°"
        elif 95.0 <= angle <= 120.0 and self.stage == "up":
            self.feedback = "Go a bit lower for full depth"

        return angle, self.counter, self.feedback

if __name__ == "__main__":
    print("Testing SquatRepStateMachine...")
    machine = SquatRepStateMachine()
    
    # Simulate a full squat
    frames = [
        ({'x': 0.5, 'y': 0.4}, {'x': 0.5, 'y': 0.6}, {'x': 0.5, 'y': 0.8}), # 180 deg (standing)
        ({'x': 0.5, 'y': 0.4}, {'x': 0.6, 'y': 0.6}, {'x': 0.5, 'y': 0.8}), # 135 deg (partial)
        ({'x': 0.5, 'y': 0.4}, {'x': 0.7, 'y': 0.6}, {'x': 0.5, 'y': 0.8}), # 90 deg (depth!)
        ({'x': 0.5, 'y': 0.4}, {'x': 0.5, 'y': 0.6}, {'x': 0.5, 'y': 0.8}), # 180 deg (back up)
    ]
    
    for f in frames:
        angle, reps, cue = machine.process_frame(f[0], f[1], f[2])
        print(f"Angle: {angle}° | Reps: {reps} | Cue: {cue}")
