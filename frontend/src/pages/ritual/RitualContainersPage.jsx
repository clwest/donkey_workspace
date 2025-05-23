import RitualContractRunner from "../../components/swarm/RitualContractRunner";
import RitualArchiveViewer from "../../components/swarm/RitualArchiveViewer";

export default function RitualContainersPage() {
  return (
    <div className="container my-5">
      <h1 className="mb-3">Ritual Containers</h1>
      <RitualContractRunner />
      <RitualArchiveViewer />
    </div>
  );
}
