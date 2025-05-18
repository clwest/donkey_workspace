import React from "react";
import TagBadge from "../TagBadge";

export default function TagFilterBar({ tags = [], selectedTags = [], onToggle, onClear }) {
  return (
    <div className="d-flex flex-wrap align-items-center mb-4">
      {tags.map((tag) => {
        const isSelected = selectedTags.includes(tag.slug);
        return (
          <TagBadge
            key={tag.slug}
            tag={tag}
            className={`me-2 mb-2 ${isSelected ? "bg-primary text-white" : "bg-light text-dark"}`}
            onClick={() => onToggle(tag.slug)}
            style={{ cursor: "pointer" }}
          />
        );
      })}

      {selectedTags.length > 0 && (
        <button className="btn btn-sm btn-outline-secondary ms-2" onClick={onClear}>
          Clear
        </button>
      )}
    </div>
  );
}