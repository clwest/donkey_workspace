import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import ReflectionModal from "../../components/assistant/ReflectionModal";

export default function UserReflectPage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [show, setShow] = useState(true);

  const handleClose = () => {
    setShow(false);
    navigate(`/assistants/${slug}`);
  };

  return <ReflectionModal slug={slug} show={show} onClose={handleClose} />;
}
