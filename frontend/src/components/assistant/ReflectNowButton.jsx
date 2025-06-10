import { useState } from "react";
import ReflectionModal from "./ReflectionModal";

export default function ReflectNowButton({ slug }) {
  const [show, setShow] = useState(false);

  const open = () => setShow(true);
  const close = () => setShow(false);

  return (
    <>
      <button className="btn btn-sm btn-outline-secondary" onClick={open}>
        Reflect Now
      </button>
      <ReflectionModal slug={slug} show={show} onClose={close} />
    </>
  );
}
