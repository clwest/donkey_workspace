import LoreLedger from "../../components/lore/LoreLedger";
import RetconReviewPanel from "../../components/lore/RetconReviewPanel";

export default function RealityShaperDashboard() {
  return (
    <div className="container my-5">
      <h1>Reality Shaper Dashboard</h1>
      <div className="row mt-4">
        <div className="col-md-6">
          <LoreLedger />
        </div>
        <div className="col-md-6">
          <RetconReviewPanel />
        </div>
      </div>
    </div>
  );
}
