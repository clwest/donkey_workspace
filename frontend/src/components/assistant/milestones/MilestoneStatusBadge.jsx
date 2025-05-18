export default function MilestoneStatusBadge({ status }) {
    let colorClass = "badge bg-secondary";
  
    if (status === "Planned") {
      colorClass = "badge bg-info text-dark";
    } else if (status === "In Progress") {
      colorClass = "badge bg-warning text-dark";
    } else if (status === "Completed") {
      colorClass = "badge bg-success";
    }
  
    return <span className={colorClass}>{status}</span>;
  }