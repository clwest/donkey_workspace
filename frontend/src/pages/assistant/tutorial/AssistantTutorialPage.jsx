import { useParams } from "react-router-dom";
import CinematicUILayer from "../../../components/cinematic/CinematicUILayer";

export default function AssistantTutorialPage() {
  const { id } = useParams();
  return (
    <CinematicUILayer title={`Assistant Tutorial ${id}`}>
      <p>Follow the steps to learn the system.</p>
    </CinematicUILayer>
  );
}
