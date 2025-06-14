import { useEffect } from "react";
import { toast } from "react-toastify";

export default function UploadErrorToast({ status }) {
  useEffect(() => {
    if (!status) return;
    if (status.is_failed) {
      toast.error(`Upload failed: ${status.reason || "unknown error"}`);
    }
  }, [status]);
  return null;
}
