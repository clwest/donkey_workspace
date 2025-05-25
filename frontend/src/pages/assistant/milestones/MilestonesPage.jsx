import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import MilestoneCard from "../../../components/assistant/milestones/MilestoneCard";
import MilestoneQuickCreate from "../../../components/assistant/milestones/MilestoneQuickCreate";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";

export default function MilestonesPage() {
  const { projectId } = useParams();
  const [milestones, setMilestones] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchMilestones() {
      const res = await fetch(`/api/assistants/projects/${projectId}/milestones/`);
      const data = await res.json();
      setMilestones(data);
    }
    fetchMilestones();
  }, [projectId]);

  async function updateMilestoneDescription(id, newDescription) {
    const res = await fetch(`/api/assistants/milestones/${id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: newDescription }),
    });
    if (res.ok) {
      setMilestones(prev =>
        prev.map(m => (m.id === id ? { ...m, description: newDescription } : m))
      );
    }
  }

  async function handleDragEnd(result) {
    if (!result.destination) return;

    const reordered = Array.from(milestones);
    const [moved] = reordered.splice(result.source.index, 1);
    reordered.splice(result.destination.index, 0, moved);

    setMilestones(reordered);
  }

  if (!milestones.length) return <div className="container my-5">Loading milestones...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">🏁 Project Milestones</h1>

      <div className="mb-4">
        <MilestoneQuickCreate projectId={projectId} onCreated={(newMilestone) => {
          setMilestones(prev => [newMilestone, ...prev]);
        }} />
      </div>

      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="milestones">
          {(provided) => (
            <div {...provided.droppableProps} ref={provided.innerRef} className="row g-3">
              {milestones.map((milestone, index) => (
                <Draggable key={milestone.id} draggableId={milestone.id} index={index}>
                  {(provided) => (
                    <div
                      className="col-md-6 col-lg-4"
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                    >
                      <MilestoneCard
                        milestone={milestone}
                        projectId={projectId}
                        onUpdate={(updated) => {
                          setMilestones(prev =>
                            prev.map(m => (m.id === updated.id ? updated : m))
                          );
                        }}
                        onUpdateDescription={updateMilestoneDescription} // ✅ Pass it properly here
                      />
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>

      <div className="mt-5">
        <Link to={`/projects/${projectId}/tasks`} className="btn btn-outline-secondary">
          🔙 Back to Project
        </Link>
      </div>
    </div>
  );
}