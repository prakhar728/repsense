export interface RoutineSet {
  type: "warmup" | "working" | "failure";
  weight: string;
  reps: number;
  notes?: string;
}

export interface RoutineExercise {
  name: string;
  sets: RoutineSet[];
}

export interface RoutineDay {
  day: string;
  focus: string;
  exercises: RoutineExercise[];
}

export interface DetailedRoutine {
  id: string;
  name: string;
  goalTag: string;
  frequency: string;
  weeklyPlan: RoutineDay[];
}

const mockRoutines: Record<string, DetailedRoutine> = {
  "1": {
    id: "1",
    name: "Progressive Overload Builder",
    goalTag: "Strength",
    frequency: "4 days/week",
    weeklyPlan: [
      {
        day: "Monday",
        focus: "Upper Push",
        exercises: [
          {
            name: "Bench Press (Barbell)",
            sets: [
              { type: "warmup", weight: "40kg", reps: 10 },
              { type: "warmup", weight: "60kg", reps: 6 },
              { type: "working", weight: "80kg", reps: 6 },
              { type: "working", weight: "85kg", reps: 6 },
              { type: "working", weight: "90kg", reps: 5 },
              { type: "failure", weight: "85kg", reps: 6 },
            ],
          },
          {
            name: "Overhead Press (Barbell)",
            sets: [
              { type: "warmup", weight: "20kg", reps: 8 },
              { type: "working", weight: "40kg", reps: 8 },
              { type: "working", weight: "45kg", reps: 8 },
              { type: "working", weight: "45kg", reps: 7 },
            ],
          },
          {
            name: "Incline Dumbbell Press",
            sets: [
              { type: "working", weight: "30kg", reps: 10 },
              { type: "working", weight: "32kg", reps: 10 },
              { type: "working", weight: "32kg", reps: 8 },
            ],
          },
          {
            name: "Lateral Raises (Dumbbell)",
            sets: [
              { type: "working", weight: "12kg", reps: 15 },
              { type: "working", weight: "12kg", reps: 14 },
              { type: "working", weight: "10kg", reps: 15 },
            ],
          },
          {
            name: "Tricep Pushdowns (Cable)",
            sets: [
              { type: "working", weight: "25kg", reps: 12 },
              { type: "working", weight: "25kg", reps: 12 },
              { type: "failure", weight: "20kg", reps: 15 },
            ],
          },
        ],
      },
      {
        day: "Tuesday",
        focus: "Lower Power",
        exercises: [
          {
            name: "Squat (Barbell)",
            sets: [
              { type: "warmup", weight: "40kg", reps: 8 },
              { type: "warmup", weight: "60kg", reps: 6 },
              { type: "working", weight: "100kg", reps: 5 },
              { type: "working", weight: "110kg", reps: 5 },
              { type: "working", weight: "115kg", reps: 4 },
              { type: "failure", weight: "100kg", reps: 6 },
            ],
          },
          {
            name: "Romanian Deadlift (Barbell)",
            sets: [
              { type: "warmup", weight: "40kg", reps: 8 },
              { type: "working", weight: "80kg", reps: 8 },
              { type: "working", weight: "90kg", reps: 8 },
              { type: "working", weight: "90kg", reps: 8 },
            ],
          },
          {
            name: "Leg Press",
            sets: [
              { type: "working", weight: "140kg", reps: 10 },
              { type: "working", weight: "160kg", reps: 10 },
              { type: "working", weight: "160kg", reps: 8 },
            ],
          },
          {
            name: "Leg Curl (Machine)",
            sets: [
              { type: "working", weight: "40kg", reps: 12 },
              { type: "working", weight: "45kg", reps: 12 },
              { type: "failure", weight: "40kg", reps: 15 },
            ],
          },
          {
            name: "Calf Raises (Standing)",
            sets: [
              { type: "working", weight: "60kg", reps: 15 },
              { type: "working", weight: "60kg", reps: 15 },
              { type: "working", weight: "60kg", reps: 15 },
              { type: "working", weight: "50kg", reps: 20 },
            ],
          },
        ],
      },
      {
        day: "Thursday",
        focus: "Upper Pull",
        exercises: [
          {
            name: "Pull-ups (Weighted)",
            sets: [
              { type: "warmup", weight: "BW", reps: 8 },
              { type: "working", weight: "+10kg", reps: 6 },
              { type: "working", weight: "+15kg", reps: 6 },
              { type: "working", weight: "+15kg", reps: 5 },
              { type: "failure", weight: "BW", reps: 8 },
            ],
          },
          {
            name: "Barbell Row",
            sets: [
              { type: "warmup", weight: "40kg", reps: 8 },
              { type: "working", weight: "70kg", reps: 8 },
              { type: "working", weight: "75kg", reps: 8 },
              { type: "working", weight: "80kg", reps: 7 },
              { type: "working", weight: "75kg", reps: 8 },
            ],
          },
          {
            name: "Face Pulls (Cable)",
            sets: [
              { type: "working", weight: "15kg", reps: 18 },
              { type: "working", weight: "15kg", reps: 17 },
              { type: "working", weight: "12kg", reps: 20 },
            ],
          },
          {
            name: "Hammer Curls (Dumbbell)",
            sets: [
              { type: "working", weight: "14kg", reps: 10 },
              { type: "working", weight: "16kg", reps: 10 },
              { type: "working", weight: "16kg", reps: 8 },
            ],
          },
          {
            name: "Barbell Curl",
            sets: [
              { type: "working", weight: "25kg", reps: 12 },
              { type: "failure", weight: "20kg", reps: 15 },
            ],
          },
        ],
      },
      {
        day: "Friday",
        focus: "Lower Hypertrophy",
        exercises: [
          {
            name: "Deadlift (Barbell)",
            sets: [
              { type: "warmup", weight: "60kg", reps: 6 },
              { type: "warmup", weight: "80kg", reps: 4 },
              { type: "working", weight: "120kg", reps: 5 },
              { type: "working", weight: "130kg", reps: 3 },
              { type: "working", weight: "120kg", reps: 5 },
            ],
          },
          {
            name: "Bulgarian Split Squat (Dumbbell)",
            sets: [
              { type: "working", weight: "20kg", reps: 10 },
              { type: "working", weight: "22kg", reps: 10 },
              { type: "working", weight: "22kg", reps: 10 },
            ],
          },
          {
            name: "Hip Thrust (Barbell)",
            sets: [
              { type: "working", weight: "80kg", reps: 12 },
              { type: "working", weight: "90kg", reps: 12 },
              { type: "working", weight: "90kg", reps: 10 },
            ],
          },
          {
            name: "Leg Extension (Machine)",
            sets: [
              { type: "working", weight: "50kg", reps: 15 },
              { type: "working", weight: "55kg", reps: 15 },
              { type: "failure", weight: "45kg", reps: 20 },
            ],
          },
          {
            name: "Ab Wheel Rollout",
            sets: [
              { type: "working", weight: "BW", reps: 12 },
              { type: "working", weight: "BW", reps: 10 },
              { type: "working", weight: "BW", reps: 10 },
            ],
          },
        ],
      },
    ],
  },
};

export function getRoutineById(id: string): DetailedRoutine | null {
  return mockRoutines[id] || null;
}
