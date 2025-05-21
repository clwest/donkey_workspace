import React from "react";

export default function MentoringThread({ events = [], onRequest }) {
  return (
    <div>
      <h5 className="mt-3">Mentoring Thread</h5>
      <ul className="list-unstyled">
        {events.map((e, idx) => (
          <li key={idx} className="mb-2">
            <span className="me-2">
              {e.teacher} → {e.learner}
            </span>
            {e.skill && (
              <span className="badge bg-secondary me-2">{e.skill}</span>
            )}
            {e.strength && (
              <span className="text-muted small">({e.strength})</span>
            )}
            {e.onView && (
              <button
                className="btn btn-sm btn-link"
                onClick={() => e.onView(e)}
              >
                View
              </button>
            )}
          </li>
        ))}
        {events.length === 0 && (
          <li className="text-muted">No mentoring events.</li>
        )}
      </ul>
      {onRequest && (
        <button className="btn btn-sm btn-outline-primary" onClick={onRequest}>
          Request Mentoring
        </button>
      )}
    </div>
  );
}
