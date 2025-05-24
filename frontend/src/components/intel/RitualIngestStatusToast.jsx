import React, { useEffect } from "react";
import { toast } from "react-toastify";

export default function RitualIngestStatusToast({ progress }) {
  useEffect(() => {
    if (!progress) return;
    if (progress.stage === "completed") {
      toast.success("🎯 Assistant Ready!");
    } else {
      toast.info(`🌀 ${progress.stage}...`);
    }
  }, [progress]);
  return null;
}
