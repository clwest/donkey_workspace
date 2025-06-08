import PropTypes from "prop-types";
import CommonModal from "../CommonModal";
import { growthRules } from "../../data/growthRules";

export default function GrowthRecapModal({ stage, summary, onClose }) {
  const rule = growthRules[stage] || {};
  return (
    <CommonModal
      show={true}
      onClose={onClose}
      title={`Stage ${stage} Unlocked!`}
      footer={
        <button className="btn btn-primary" onClick={onClose}>
          Continue
        </button>
      }
    >
      {rule.unlocks && rule.unlocks.length > 0 && (
        <div className="mb-3">
          <h6>New Unlocks</h6>
          <ul>
            {rule.unlocks.map((u) => (
              <li key={u}>{u}</li>
            ))}
          </ul>
        </div>
      )}
      {summary && <p>{summary}</p>}
      <p>Keep evolving your assistant to unlock more features.</p>
    </CommonModal>
  );
}

GrowthRecapModal.propTypes = {
  stage: PropTypes.number.isRequired,
  summary: PropTypes.string,
  onClose: PropTypes.func.isRequired,
};
