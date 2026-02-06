"""Configuration and constants."""

EXERCISE_MUSCLE_MAP = {
    "Bench Press (Barbell)": {
        "exercise_id": "bench_press",
        "targeted_muscles": ["chest", "shoulders", "triceps"],
        "primary_muscle": "chest"
    },
    "Incline Chest Fly (Dumbbell)": {
        "exercise_id": "incline_fly",
        "targeted_muscles": ["chest"],
        "primary_muscle": "chest"
    },
    "Chest Fly (Machine)": {
        "exercise_id": "chest_fly_machine",
        "targeted_muscles": ["chest"],
        "primary_muscle": "chest"
    },
    "Bicep Curl (Barbell)": {
        "exercise_id": "bicep_curl",
        "targeted_muscles": ["biceps"],
        "primary_muscle": "biceps"
    },
    "Reverse Curl (Barbell)": {
        "exercise_id": "reverse_curl",
        "targeted_muscles": ["biceps", "forearms"],
        "primary_muscle": "biceps"
    },
    "Triceps Pushdown": {
        "exercise_id": "triceps_pushdown",
        "targeted_muscles": ["triceps"],
        "primary_muscle": "triceps"
    },
    "Triceps Extension (Barbell)": {
        "exercise_id": "triceps_extension",
        "targeted_muscles": ["triceps"],
        "primary_muscle": "triceps"
    },
    "Lat Pulldown (Cable)": {
        "exercise_id": "lat_pulldown",
        "targeted_muscles": ["lats", "upper_back", "biceps"],
        "primary_muscle": "lats"
    },
    "Lat Pulldown - Close Grip (Cable)": {
        "exercise_id": "lat_pulldown_close_grip",
        "targeted_muscles": ["lats", "upper_back", "biceps"],
        "primary_muscle": "lats"
    },
    "Shoulder Press (Dumbbell)": {
        "exercise_id": "shoulder_press",
        "targeted_muscles": ["shoulders", "triceps"],
        "primary_muscle": "shoulders"
    },
    "Shrug (Barbell)": {
        "exercise_id": "barbell_shrug",
        "targeted_muscles": ["traps"],
        "primary_muscle": "traps"
    },
    "Squat (Barbell)": {
        "exercise_id": "squat",
        "targeted_muscles": ["quads", "glutes", "core"],
        "primary_muscle": "quads"
    },
    "Deadlift (Barbell)": {
        "exercise_id": "deadlift",
        "targeted_muscles": ["lower_back", "glutes", "hamstrings", "core"],
        "primary_muscle": "lower_back"
    },
    "Romanian Deadlift (Barbell)": {
        "exercise_id": "romanian_deadlift",
        "targeted_muscles": ["hamstrings", "glutes", "lower_back"],
        "primary_muscle": "hamstrings"
    }
}

# INTENT_TYPES--------------------------------

class Intent:
    DATA_ACCESS = "DATA_ACCESS"
    REASONING = "REASONING"
    ROUTINE_GENERATION = "ROUTINE_GENERATION"
    FEEDBACK = "FEEDBACK"

DATE_FORMAT = "%d %b %Y, %H:%M"
#----------------------------------------------