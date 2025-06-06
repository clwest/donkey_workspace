import { useEffect, useState } from "react";

export default function HintBubble({ content, position = {}, onDismiss, highlightSelector }) {
  const [style, setStyle] = useState(position);

  useEffect(() => {
    if (highlightSelector) {
      const el = document.querySelector(highlightSelector);
      if (el) {
        const rect = el.getBoundingClientRect();
        setStyle({
          position: "absolute",
          top: rect.bottom + window.scrollY + 8,
          left: rect.left + window.scrollX,
          ...position,
        });
      }
    }
  }, [highlightSelector]);

  return (
    <div
      className="hint-bubble bg-light border rounded shadow p-2"
      style={{ position: "absolute", zIndex: 2000, ...style }}
    >
      <button type="button" className="btn-close float-end" onClick={onDismiss} />
      <div dangerouslySetInnerHTML={{ __html: content }} />
    </div>
  );
}
