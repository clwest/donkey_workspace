import { useEffect } from "react";
import { toast } from "react-toastify";

export default function ReflectionToastStatus({ status }) {
  useEffect(() => {
    if (!status) return;
    if (status === "success") {
      toast.success("✅ Reflection received. Myth updated.");
    } else if (status === "error") {
      toast.error("❌ Reflection failed. Symbolic memory may be unstable.");
    } else if (status === "retry") {
      toast.info("🔁 Reattempting insight synthesis…");
    }
  }, [status]);
  return null;
}
