import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import DocumentStatusCard from "./DocumentStatusCard";
import apiFetch from "../../utils/apiClient";
import { Modal, Button, Spinner, Tooltip, OverlayTrigger, Badge } from "react-bootstrap";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend
);

export default function DocumentIngestingCard({ doc, highlightConflicts }) {
  const [localDoc, setLocalDoc] = useState(doc);
  const [showDetails, setShowDetails] = useState(false);
  const [startTime] = useState(new Date());
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState(null);
  const [processingHistory, setProcessingHistory] = useState([]);
  const [retryCount, setRetryCount] = useState(0);
  const [errorDetails, setErrorDetails] = useState(null);
  const [showErrorDetails, setShowErrorDetails] = useState(false);
  const [processingSpeed, setProcessingSpeed] = useState(null);

  useEffect(() => {
    setLocalDoc(doc);
  }, [doc]);

  const fetchErrorDetails = useCallback(async () => {
    if (!localDoc?.id) return;
    try {
      const details = await apiFetch(`/intel/documents/${localDoc.id}/error-details/`);
      setErrorDetails(details);
    } catch (err) {
      console.error("Failed to fetch error details", err);
    }
  }, [localDoc?.id]);

  useEffect(() => {
    if (localDoc?.progress_status === "error") {
      fetchErrorDetails();
    }
  }, [localDoc?.progress_status, fetchErrorDetails]);

  useEffect(() => {
    const pid = doc?.metadata?.progress_id;
    if (!pid) return;
    let stop = false;

    const fetchProgress = async () => {
      try {
        const data = await apiFetch(`/intel/documents/${pid}/progress/`);
        
        // Update processing history
        setProcessingHistory(prev => {
          const newHistory = [...prev, {
            timestamp: new Date(),
            processed: data.processed,
            embedded: data.embedded_chunks,
            total: data.total_chunks
          }].slice(-20); // Keep last 20 data points
          return newHistory;
        });

        setLocalDoc((prev) => ({
          ...prev,
          progress_status: data.status,
          progress_error: data.error_message,
          failed_chunks: data.failed_chunks,
          chunk_index: data.processed ?? prev.chunk_index,
          embedded_chunks: data.embedded_chunks ?? prev.embedded_chunks,
          num_embedded: data.embedded_chunks ?? prev.num_embedded,
          chunk_count: data.total_chunks ?? prev.chunk_count,
          num_chunks: data.total_chunks ?? prev.num_chunks,
        }));

        // Calculate processing speed
        if (data.processed && data.total_chunks) {
          const elapsedTime = (new Date() - startTime) / 1000; // in seconds
          const chunksPerSecond = data.processed / elapsedTime;
          setProcessingSpeed(chunksPerSecond);
          
          // Calculate estimated time remaining
          const remainingChunks = data.total_chunks - data.processed;
          const estimatedSeconds = chunksPerSecond > 0 ? remainingChunks / chunksPerSecond : null;
          setEstimatedTimeRemaining(estimatedSeconds);
        }

        if (data.status === "completed" || data.status === "failed") {
          const full = await apiFetch(`/intel/documents/${doc.id}/`);
          if (!stop) setLocalDoc((prev) => ({ ...prev, ...full }));
          clearInterval(interval);
        }
      } catch (err) {
        console.error("Progress poll failed", err);
      }
    };

    fetchProgress();
    const interval = setInterval(fetchProgress, 3000);
    return () => {
      stop = true;
      clearInterval(interval);
    };
  }, [doc.id, doc?.metadata?.progress_id, startTime]);

  const formatTimeRemaining = (seconds) => {
    if (!seconds || seconds < 0) return "Calculating...";
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m ${Math.round(seconds % 60)}s`;
  };

  const handleRetry = async () => {
    try {
      setRetryCount(prev => prev + 1);
      await apiFetch(`/intel/documents/${doc.id}/retry/`, { method: "POST" });
      setLocalDoc((prev) => ({ ...prev, progress_status: "processing" }));
      setErrorDetails(null);
    } catch (err) {
      console.error("Retry failed", err);
    }
  };

  const getProcessingChartData = () => {
    const labels = processingHistory.map(h => 
      new Date(h.timestamp).toLocaleTimeString()
    );
    
    return {
      labels,
      datasets: [
        {
          label: 'Processed Chunks',
          data: processingHistory.map(h => h.processed),
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        },
        {
          label: 'Embedded Chunks',
          data: processingHistory.map(h => h.embedded),
          borderColor: 'rgb(153, 102, 255)',
          tension: 0.1
        }
      ]
    };
  };

  if (!localDoc) return null;

  const title = localDoc.title || "Untitled";
  const sourceType = localDoc.source_type || "";
  const embedded = localDoc.embedded_chunks ?? localDoc.num_embedded ?? 0;
  const created = localDoc.chunk_index ?? localDoc.chunk_count ?? 0;
  const total = localDoc.chunk_count ?? localDoc.num_chunks ?? created;
  const failedCount = localDoc.failed_chunks?.length || 0;
  const tokenCount = localDoc.token_count || 0;
  const progressPct = total ? Math.round((embedded / total) * 100) : 0;

  const getStatusColor = () => {
    switch (localDoc.progress_status) {
      case "completed":
        return "success";
      case "failed":
        return "danger";
      case "processing":
        return "primary";
      default:
        return "secondary";
    }
  };

  const renderErrorDetails = () => (
    <div className="mt-3">
      <h6>Error Details</h6>
      <div className="alert alert-danger">
        <pre className="mb-0" style={{ fontSize: "0.875rem" }}>
          {errorDetails?.stack_trace || errorDetails?.message || "No detailed error information available"}
        </pre>
      </div>
      {errorDetails?.suggestions && (
        <div className="mt-2">
          <h6>Suggested Solutions:</h6>
          <ul className="list-unstyled">
            {errorDetails.suggestions.map((suggestion, index) => (
              <li key={index} className="mb-1">
                <i className="bi bi-lightbulb me-2"></i>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  return (
    <>
      <div
        className={`card mb-3 shadow-sm p-3 ${
          highlightConflicts && failedCount > 0 ? "border-danger" : ""
        }`}
      >
        {localDoc.progress_status === "error" && (
          <div className="text-danger mb-2">
            <i className="bi bi-exclamation-triangle-fill me-2"></i>
            Ingestion failed: {localDoc.progress_error || "Unknown error"}
            <Button
              variant="outline-danger"
              size="sm"
              className="ms-2"
              onClick={handleRetry}
            >
              Retry {retryCount > 0 && `(${retryCount})`}
            </Button>
            <Button
              variant="link"
              size="sm"
              className="ms-2"
              onClick={() => setShowErrorDetails(!showErrorDetails)}
            >
              {showErrorDetails ? "Hide Details" : "Show Details"}
            </Button>
          </div>
        )}
        {showErrorDetails && renderErrorDetails()}
        
        <h5 className="mb-1">{title}</h5>
        <div className="small text-muted mb-2">Source: {sourceType}</div>
        
        <div className="progress mb-2" style={{ height: "8px" }}>
          <div
            className={`progress-bar progress-bar-striped progress-bar-animated bg-${getStatusColor()}`}
            role="progressbar"
            style={{ width: `${progressPct}%` }}
            aria-valuenow={progressPct}
            aria-valuemin="0"
            aria-valuemax="100"
          />
        </div>

        <div className="d-flex justify-content-between align-items-center mb-2">
          <div className="small">
            <strong>Progress:</strong> {progressPct}%
            {estimatedTimeRemaining && localDoc.progress_status === "processing" && (
              <span className="ms-2 text-muted">
                (Est. {formatTimeRemaining(estimatedTimeRemaining)} remaining)
              </span>
            )}
          </div>
          <div className="d-flex align-items-center gap-2">
            {processingSpeed && (
              <Badge bg="info" className="me-2">
                {processingSpeed.toFixed(2)} chunks/s
              </Badge>
            )}
            <Button
              variant="link"
              size="sm"
              className="p-0"
              onClick={() => setShowDetails(true)}
            >
              Details
            </Button>
          </div>
        </div>

        <div className="d-flex align-items-center gap-2">
          <DocumentStatusCard doc={localDoc} />
          {localDoc.prompt_id && localDoc.progress_status === "completed" && (
            <Link
              to={`/prompts/${localDoc.prompt_id}`}
              className="small text-decoration-underline"
            >
              📄 View Reflection Prompt
            </Link>
          )}
        </div>
      </div>

      <Modal show={showDetails} onHide={() => setShowDetails(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Document Processing Details</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="row">
            <div className="col-md-6">
              <h6>Processing Status</h6>
              <ul className="list-unstyled">
                <li>
                  <strong>Status:</strong>{" "}
                  <span className={`text-${getStatusColor()}`}>
                    {localDoc.progress_status}
                  </span>
                </li>
                <li>
                  <strong>Chunks Processed:</strong> {created} / {total}
                </li>
                <li>
                  <strong>Chunks Embedded:</strong> {embedded} / {total}
                </li>
                <li>
                  <strong>Failed Chunks:</strong>{" "}
                  {failedCount > 0 ? (
                    <span className="text-danger">{failedCount}</span>
                  ) : (
                    "None"
                  )}
                </li>
                <li>
                  <strong>Total Tokens:</strong> {tokenCount.toLocaleString()}
                </li>
                {processingSpeed && (
                  <li>
                    <strong>Processing Speed:</strong>{" "}
                    {processingSpeed.toFixed(2)} chunks/second
                  </li>
                )}
              </ul>
            </div>
            <div className="col-md-6">
              <h6>Document Information</h6>
              <ul className="list-unstyled">
                <li>
                  <strong>Title:</strong> {title}
                </li>
                <li>
                  <strong>Source Type:</strong> {sourceType}
                </li>
                <li>
                  <strong>Created:</strong>{" "}
                  {new Date(localDoc.created_at).toLocaleString()}
                </li>
                {localDoc.updated_at && (
                  <li>
                    <strong>Last Updated:</strong>{" "}
                    {new Date(localDoc.updated_at).toLocaleString()}
                  </li>
                )}
                {retryCount > 0 && (
                  <li>
                    <strong>Retry Attempts:</strong> {retryCount}
                  </li>
                )}
              </ul>
            </div>
          </div>

          {processingHistory.length > 0 && (
            <div className="mt-4">
              <h6>Processing History</h6>
              <div style={{ height: "200px" }}>
                <Line
                  data={getProcessingChartData()}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                        title: {
                          display: true,
                          text: 'Chunks'
                        }
                      },
                      x: {
                        title: {
                          display: true,
                          text: 'Time'
                        }
                      }
                    }
                  }}
                />
              </div>
            </div>
          )}

          {failedCount > 0 && (
            <div className="mt-3">
              <h6>Failed Chunks</h6>
              <div className="alert alert-danger">
                <small>
                  Failed chunk indices: {localDoc.failed_chunks.join(", ")}
                </small>
              </div>
            </div>
          )}

          {errorDetails && (
            <div className="mt-3">
              <h6>Error Details</h6>
              <div className="alert alert-danger">
                <pre className="mb-0" style={{ fontSize: "0.875rem" }}>
                  {errorDetails.stack_trace || errorDetails.message || "No detailed error information available"}
                </pre>
              </div>
              {errorDetails.suggestions && (
                <div className="mt-2">
                  <h6>Suggested Solutions:</h6>
                  <ul className="list-unstyled">
                    {errorDetails.suggestions.map((suggestion, index) => (
                      <li key={index} className="mb-1">
                        <i className="bi bi-lightbulb me-2"></i>
                        {suggestion}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDetails(false)}>
            Close
          </Button>
          {localDoc.progress_status === "error" && (
            <Button variant="danger" onClick={handleRetry}>
              Retry Processing {retryCount > 0 && `(${retryCount})`}
            </Button>
          )}
        </Modal.Footer>
      </Modal>
    </>
  );
}
