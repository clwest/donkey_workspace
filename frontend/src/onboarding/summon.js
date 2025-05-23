import { useNavigate } from "react-router-dom";

export default function usePostSummonRouter() {
  const navigate = useNavigate();
  return (assistant) => {
    if (assistant && assistant.id) {
      navigate(`/assistants/${assistant.id}/interface`);
    }
  };
}
