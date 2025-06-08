import Carousel from "react-bootstrap/Carousel";
import AssistantCard from "../assistant/AssistantCard";

export default function DemoSuccessCarousel({ assistants = [] }) {
  if (!assistants.length) return null;
  return (
    <div className="mb-4">
      <h2 className="h5 mb-3">Featured Conversion</h2>
      <Carousel indicators={false} interval={6000} className="shadow-sm">
        {assistants.map((a) => (
          <Carousel.Item key={a.slug} className="p-4">
            <div className="d-flex justify-content-center">
              <AssistantCard
                assistant={a}
                chatLink={`/assistants/${a.slug}/chat`}
              />
            </div>
            <Carousel.Caption>
              <small>{a.sessions} sessions · {a.messages} messages</small>
            </Carousel.Caption>
          </Carousel.Item>
        ))}
      </Carousel>
    </div>
  );
}
