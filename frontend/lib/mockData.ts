// Mock data and async functions for Repsense

export interface ParsedCSVData {
  workoutsDetected: number;
  weeksCovered: number;
  avgSessionsPerWeek: number;
  topLifts: string[];
}

export interface Routine {
  id: string;
  name: string;
  goalTag: string;
  frequency: string;
  rationale: string;
  weeklyPlan: DayPlan[];
  estimatedDuration: string;
  recoveryNote: string;
}

export interface DayPlan {
  day: string;
  focus: string;
  exercises: Exercise[];
}

export interface Exercise {
  name: string;
  sets: number;
  reps: string;
  notes?: string;
}

// Simulate CSV parsing with delay
export const parseCSV = (): Promise<ParsedCSVData> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        workoutsDetected: 78,
        weeksCovered: 12,
        avgSessionsPerWeek: 4.2,
        topLifts: ["Bench Press", "Squat", "Deadlift"],
      });
    }, 1200);
  });
};

// Mock routine generation
export const generateRoutines = (focus: string): Promise<Routine[]> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        {
          id: "1",
          name: "Progressive Overload Builder",
          goalTag: "Strength",
          frequency: "4 days/week",
          rationale:
            "Based on your 4.2 sessions/week average and strong compound lift history, this program builds on your existing strength base with strategic progressive overload.",
          estimatedDuration: "60-75 min/session",
          recoveryNote:
            "Includes 2 active recovery days. Your data shows good recovery patterns—this program respects that rhythm.",
          weeklyPlan: [
            {
              day: "Monday",
              focus: "Upper Push",
              exercises: [
                { name: "Bench Press", sets: 4, reps: "6-8", notes: "Progressive overload focus" },
                { name: "Overhead Press", sets: 3, reps: "8-10" },
                { name: "Incline DB Press", sets: 3, reps: "10-12" },
                { name: "Lateral Raises", sets: 3, reps: "12-15" },
                { name: "Tricep Pushdowns", sets: 3, reps: "12-15" },
              ],
            },
            {
              day: "Tuesday",
              focus: "Lower Power",
              exercises: [
                { name: "Squat", sets: 4, reps: "5-6", notes: "Main strength movement" },
                { name: "Romanian Deadlift", sets: 3, reps: "8-10" },
                { name: "Leg Press", sets: 3, reps: "10-12" },
                { name: "Leg Curl", sets: 3, reps: "12-15" },
                { name: "Calf Raises", sets: 4, reps: "15-20" },
              ],
            },
            {
              day: "Thursday",
              focus: "Upper Pull",
              exercises: [
                { name: "Weighted Pull-ups", sets: 4, reps: "6-8" },
                { name: "Barbell Rows", sets: 4, reps: "8-10" },
                { name: "Face Pulls", sets: 3, reps: "15-20" },
                { name: "Hammer Curls", sets: 3, reps: "10-12" },
                { name: "Barbell Curls", sets: 2, reps: "12-15" },
              ],
            },
            {
              day: "Friday",
              focus: "Lower Hypertrophy",
              exercises: [
                { name: "Deadlift", sets: 3, reps: "5", notes: "Technique focus" },
                { name: "Bulgarian Split Squats", sets: 3, reps: "10-12/leg" },
                { name: "Hip Thrust", sets: 3, reps: "12-15" },
                { name: "Leg Extension", sets: 3, reps: "15-20" },
                { name: "Ab Wheel", sets: 3, reps: "10-15" },
              ],
            },
          ],
        },
        {
          id: "2",
          name: "Sustainable Hypertrophy",
          goalTag: "Hypertrophy",
          frequency: "5 days/week",
          rationale:
            "Your consistency over 12 weeks shows you can handle higher frequency. This program maximizes muscle growth while managing fatigue from your top lifts.",
          estimatedDuration: "50-60 min/session",
          recoveryNote:
            "Higher frequency but lower volume per session. Strategic deload every 4th week based on your training history.",
          weeklyPlan: [
            {
              day: "Monday",
              focus: "Chest & Triceps",
              exercises: [
                { name: "Incline Bench Press", sets: 4, reps: "8-10" },
                { name: "Cable Flyes", sets: 3, reps: "12-15" },
                { name: "Dips", sets: 3, reps: "8-12" },
                { name: "Overhead Tricep Extension", sets: 3, reps: "12-15" },
              ],
            },
            {
              day: "Tuesday",
              focus: "Back & Biceps",
              exercises: [
                { name: "Lat Pulldown", sets: 4, reps: "10-12" },
                { name: "Seated Cable Row", sets: 3, reps: "10-12" },
                { name: "Straight Arm Pulldown", sets: 3, reps: "12-15" },
                { name: "Incline DB Curl", sets: 3, reps: "10-12" },
              ],
            },
            {
              day: "Wednesday",
              focus: "Legs",
              exercises: [
                { name: "Hack Squat", sets: 4, reps: "10-12" },
                { name: "Walking Lunges", sets: 3, reps: "12/leg" },
                { name: "Leg Curl", sets: 4, reps: "12-15" },
                { name: "Seated Calf Raise", sets: 4, reps: "15-20" },
              ],
            },
            {
              day: "Thursday",
              focus: "Shoulders & Arms",
              exercises: [
                { name: "Seated DB Press", sets: 4, reps: "10-12" },
                { name: "Lateral Raises", sets: 4, reps: "15-20" },
                { name: "Rear Delt Flyes", sets: 3, reps: "15-20" },
                { name: "EZ Bar Curl", sets: 3, reps: "10-12" },
                { name: "Skull Crushers", sets: 3, reps: "10-12" },
              ],
            },
            {
              day: "Friday",
              focus: "Full Body Power",
              exercises: [
                { name: "Deadlift", sets: 3, reps: "6-8" },
                { name: "Bench Press", sets: 3, reps: "8-10" },
                { name: "Pull-ups", sets: 3, reps: "AMRAP" },
                { name: "Leg Press", sets: 3, reps: "12-15" },
              ],
            },
          ],
        },
        {
          id: "3",
          name: "Recovery & Rebuild",
          goalTag: "Recovery",
          frequency: "3 days/week",
          rationale:
            "Perfect for a deload phase or when life gets busy. Maintains your strength in Bench, Squat, and Deadlift while allowing full recovery.",
          estimatedDuration: "45-55 min/session",
          recoveryNote:
            "Maximum recovery between sessions. Ideal for 2-4 weeks before transitioning to a more intensive program.",
          weeklyPlan: [
            {
              day: "Monday",
              focus: "Full Body A",
              exercises: [
                { name: "Squat", sets: 3, reps: "8", notes: "RPE 7" },
                { name: "Bench Press", sets: 3, reps: "8", notes: "RPE 7" },
                { name: "Barbell Row", sets: 3, reps: "10" },
                { name: "Plank", sets: 3, reps: "45s" },
              ],
            },
            {
              day: "Wednesday",
              focus: "Full Body B",
              exercises: [
                { name: "Deadlift", sets: 3, reps: "6", notes: "RPE 7" },
                { name: "Overhead Press", sets: 3, reps: "8" },
                { name: "Pull-ups", sets: 3, reps: "8-10" },
                { name: "Face Pulls", sets: 3, reps: "15" },
              ],
            },
            {
              day: "Friday",
              focus: "Full Body C",
              exercises: [
                { name: "Front Squat", sets: 3, reps: "8" },
                { name: "Incline DB Press", sets: 3, reps: "10" },
                { name: "Cable Row", sets: 3, reps: "12" },
                { name: "Lateral Raises", sets: 3, reps: "15" },
                { name: "Hammer Curls", sets: 2, reps: "12" },
              ],
            },
          ],
        },
        {
          id: "4",
          name: "Lean & Mean Cut",
          goalTag: "Fat Loss",
          frequency: "4 days/week",
          rationale:
            "Preserves your hard-earned strength while optimizing for fat loss. Higher rep ranges and strategic conditioning based on your lifting preferences.",
          estimatedDuration: "55-65 min/session",
          recoveryNote:
            "Includes LISS cardio recommendations. Pair with slight caloric deficit for best results.",
          weeklyPlan: [
            {
              day: "Monday",
              focus: "Upper Strength",
              exercises: [
                { name: "Bench Press", sets: 4, reps: "6-8" },
                { name: "Barbell Row", sets: 4, reps: "6-8" },
                { name: "DB Shoulder Press", sets: 3, reps: "10-12" },
                { name: "Superset: Curls/Triceps", sets: 3, reps: "12-15" },
                { name: "Incline Walk", sets: 1, reps: "15 min", notes: "Post-workout" },
              ],
            },
            {
              day: "Tuesday",
              focus: "Lower Strength",
              exercises: [
                { name: "Squat", sets: 4, reps: "6-8" },
                { name: "Romanian Deadlift", sets: 3, reps: "10-12" },
                { name: "Leg Press", sets: 3, reps: "12-15" },
                { name: "Walking Lunges", sets: 2, reps: "12/leg" },
                { name: "Stair Climber", sets: 1, reps: "10 min", notes: "Post-workout" },
              ],
            },
            {
              day: "Thursday",
              focus: "Upper Volume",
              exercises: [
                { name: "Incline DB Press", sets: 3, reps: "12-15" },
                { name: "Cable Rows", sets: 3, reps: "12-15" },
                { name: "Lateral Raises", sets: 4, reps: "15-20" },
                { name: "Face Pulls", sets: 3, reps: "15-20" },
                { name: "Circuit: Arms", sets: 2, reps: "15 each" },
              ],
            },
            {
              day: "Friday",
              focus: "Lower Volume + Conditioning",
              exercises: [
                { name: "Deadlift", sets: 3, reps: "6" },
                { name: "Bulgarian Split Squats", sets: 3, reps: "12/leg" },
                { name: "Leg Curl", sets: 3, reps: "15" },
                { name: "KB Swings", sets: 3, reps: "20" },
                { name: "Farmer Walks", sets: 3, reps: "40m" },
              ],
            },
          ],
        },
      ]);
    }, 1500);
  });
};

export const focusPresets = [
  "Fat loss",
  "Strength",
  "Hypertrophy",
  "Recovery",
  "Consistency",
];
