import { useState } from "react";
import { Button, Spinner, OverlayTrigger, Tooltip } from "react-bootstrap";
import { suggestMissingGlossaryMutations } from "../../api/agents";

export default function AutoSuggestButton({ assistant, onComplete, className = "" }) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      await suggestMissingGlossaryMutations(assistant);
      if (onComplete) onComplete();
    } catch (err) {
      console.error("Auto-suggest failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <OverlayTrigger
      placement="top"
      overlay={<Tooltip>Auto-Suggest Missing Labels</Tooltip>}
    >
      <span className={"d-inline-block " + className}>
        <Button size="sm" disabled={loading} onClick={handleClick}>
          {loading ? (
            <>
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                aria-hidden="true"
                className="me-1"
              />
              Suggesting...
            </>
          ) : (
            "Auto-Suggest Missing Labels"
          )}
        </Button>
      </span>
    </OverlayTrigger>
  );
}


