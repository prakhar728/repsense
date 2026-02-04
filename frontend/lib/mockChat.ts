export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export interface ChatSession {
  id: string;
  title: string;
  lastMessage: string;
  date: string;
}

export const mockSessions: ChatSession[] = [
  {
    id: "1",
    title: "Bench press plateau help",
    lastMessage: "Try incorporating pause reps at 80% of your...",
    date: "Today",
  },
  {
    id: "2",
    title: "Recovery after leg day",
    lastMessage: "Based on your squat volume, I'd recommend...",
    date: "Yesterday",
  },
  {
    id: "3",
    title: "Deadlift form check tips",
    lastMessage: "Your pull frequency is solid. Focus on hip hinge...",
    date: "Jan 30",
  },
  {
    id: "4",
    title: "Weekly split optimization",
    lastMessage: "Given your 4.2 sessions/week average, an upper...",
    date: "Jan 28",
  },
];

const mockReplies = [
  "Based on your training data, your bench press has been trending upward over the last 4 weeks. Your estimated 1RM is around 225 lbs. To keep progressing, I'd suggest adding a secondary bench variation — something like close-grip or paused bench — on your upper pull day. This gives you extra pressing volume without overloading your recovery.\n\nHere's what I'd recommend:\n- **Main bench day**: 4x5 at 85% 1RM\n- **Secondary day**: 3x8 close-grip at 70%\n- Keep rest periods at 2-3 minutes for the heavy sets.",

  "Looking at your squat history, you've been averaging about 12 working sets per week for quads. That's solid for maintenance, but if you want to push strength, we could bump that to 15-16 sets.\n\nYour best recent session was 315 lbs for 3 reps — that puts your estimated 1RM around 335. Here's a progression plan:\n1. Week 1-2: 4x4 at 290 lbs\n2. Week 3-4: 4x3 at 305 lbs\n3. Week 5: Test — work up to a heavy triple\n\nMake sure you're getting 7+ hours of sleep. Your data shows performance dips correlate with shorter rest periods between sessions.",

  "Great question! Your training consistency has been excellent — 4.2 sessions per week over 12 weeks is above average. Based on the exercises you've been doing, your program is well-balanced between push, pull, and legs.\n\nOne thing I notice is that your rear delt and upper back work is relatively low compared to your pressing volume. I'd recommend adding:\n- **Face pulls**: 3x15-20 twice per week\n- **Band pull-aparts**: 2x25 as a warm-up\n\nThis will help balance your shoulders and potentially improve your bench press too.",

  "I've put together a new 4-day strength program based on your data. It builds on your existing compound lift numbers with strategic progressive overload and proper warmup sets.\n\nView your updated routine here: [routine:1]\n\nThe program includes dedicated warmup sets before your working weight, and I've added failure sets on the last exercise of each session to push your limits. Let me know if you want me to adjust anything.",
];

let replyIndex = 0;

export function getMockReply(): Promise<string> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const reply = mockReplies[replyIndex % mockReplies.length];
      replyIndex++;
      resolve(reply);
    }, 1200);
  });
}

export const suggestedPrompts = [
  "How can I break through my bench press plateau?",
  "What does my training volume look like?",
  "Am I recovering enough between sessions?",
  "Suggest a deload week based on my data",
];
