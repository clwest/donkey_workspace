export default function MilestoneTimeline({ milestones = [] }) {
  return (
    <ul className="list-unstyled">
      {milestones.map((m, idx) => (
        <li key={idx} className="mb-1">
          ✅ {m}
        </li>
      ))}
    </ul>
  );
}
