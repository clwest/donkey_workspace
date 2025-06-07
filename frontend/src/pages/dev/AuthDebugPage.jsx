import useAuthDebug from "@/hooks/useAuthDebug";

export default function AuthDebugPage() {
  const { access, refresh, authLost } = useAuthDebug();

  return (
    <div className="container mt-4">
      <h2 className="mb-3">🔐 Auth Debug</h2>
      <table className="table table-bordered">
        <tbody>
          <tr>
            <th>Access Token</th>
            <td className="text-break">{access || <em>None</em>}</td>
          </tr>
          <tr>
            <th>Refresh Token</th>
            <td className="text-break">{refresh || <em>None</em>}</td>
          </tr>
          <tr>
            <th>authLost</th>
            <td>{String(authLost)}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
