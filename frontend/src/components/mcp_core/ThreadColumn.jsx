import { Droppable, Draggable } from "@hello-pangea/dnd";
import MemoryCard from "./MemoryCard";
import ThoughtCard from "./ThoughtCard";

export default function ThreadColumn({ thread }) {
  return (
    <div className="col" style={{ minWidth: 250 }}>
      <h5 className="text-center">{thread.title}</h5>
      <Droppable droppableId={thread.id}>
        {(provided) => (
          <div ref={provided.innerRef} {...provided.droppableProps}>
            {thread.items.map((item, index) => (
              <Draggable key={item.id} draggableId={item.id} index={index}>
                {(provided) => (
                  <div ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps}>
                    {item.type === "memory" ? (
                      <MemoryCard memory={item} />
                    ) : (
                      <ThoughtCard thought={item} />
                    )}
                  </div>
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  );
}
