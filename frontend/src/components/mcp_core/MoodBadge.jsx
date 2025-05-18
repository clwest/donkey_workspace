// frontend/components/mcp_core/MoodBadge.jsx

export const moodColors = {
    optimistic: "success",
    positive: "success",
    neutral: "secondary",
    concerned: "warning",
    anxious: "danger",
    frustrated: "danger",
    thoughtful: "info",
    focused: "primary",
    overwhelmed: "danger",
    energized: "success",
    cautious: "warning",
    analytical: "info",
  };
  
  export default function MoodBadge({ mood }) {
    if (!mood) return null;
  
    const color = moodColors[mood.toLowerCase()] || "dark";
  
    return (
      <span className={`badge bg-${color} rounded-pill`}>
        {mood.charAt(0).toUpperCase() + mood.slice(1)}
      </span>
    );
  }