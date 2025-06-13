import { useState } from "react";
import PropTypes from "prop-types";
import apiFetch from "../../utils/apiClient";

export default function ReflectionGroupModal({ assistant, onCreated }) {
  const [slug, setSlug] = useState("");
  const [title, setTitle] = useState("");

  const create = async () => {
    if (!slug) return;
    await apiFetch(`/assistants/${assistant}/reflections/groups/`, {
      method: "POST",
      body: { slug, title },
    });
    setSlug("");
    setTitle("");
    if (onCreated) onCreated();
  };

  return (
    <div className="modal fade" id="groupModal" tabIndex="-1">
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">New Reflection Group</h5>
            <button type="button" className="btn-close" data-bs-dismiss="modal" />
          </div>
          <div className="modal-body">
            <input
              type="text"
              className="form-control mb-2"
              placeholder="Slug"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
            />
            <input
              type="text"
              className="form-control"
              placeholder="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <div className="modal-footer">
            <button className="btn btn-primary" onClick={create} data-bs-dismiss="modal">
              Create
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

ReflectionGroupModal.propTypes = {
  assistant: PropTypes.string.isRequired,
  onCreated: PropTypes.func,
};
