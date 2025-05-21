import { useEffect, useState } from "react";
import { DragDropContext } from "@hello-pangea/dnd";
import ThreadColumn from "./ThreadColumn";
import apiFetch from "../../utils/apiClient";

export default function ThreadEditorPanel() {
  const [threads, setThreads] = useState([]);

  useEffect(() => {
    apiFetch("/mcp/threads/").then((data) => {
      if (!data) return;
      Promise.all(
        data.map((t) => apiFetch(`/mcp/threads/${t.id}/summary/`))
      ).then((details) => {
        setThreads(
          details.map((d) => ({
            id: d.id,
            title: d.title,
            items: [
              ...d.memories.map((m) => ({ ...m, type: "memory" })),
              ...d.thoughts.map((th) => ({ ...th, type: "thought" })),
            ],
          }))
        );
      });
    });
  }, []);

  async function handleDrag(result) {
    if (!result.destination) return;
    const { draggableId, source, destination } = result;
    if (source.droppableId === destination.droppableId) return;
    await apiFetch(`/mcp/memory/${draggableId}/relink/`, {
      method: "PATCH",
      body: JSON.stringify({ new_thread_id: destination.droppableId }),
    });
    setThreads((cols) => {
      const next = cols.map((c) => ({ ...c, items: [...c.items] }));
      const src = next.find((c) => c.id === source.droppableId);
      const dest = next.find((c) => c.id === destination.droppableId);
      const [moved] = src.items.splice(source.index, 1);
      dest.items.splice(destination.index, 0, moved);
      return next;
    });
  }

  return (
    <DragDropContext onDragEnd={handleDrag}>
      <div className="row gx-3 overflow-auto">
        {threads.map((thread) => (
          <ThreadColumn key={thread.id} thread={thread} />
        ))}
      </div>
    </DragDropContext>
  );
}
