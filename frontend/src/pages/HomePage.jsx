import '../index.css';
import RouteMapTable from '../components/RouteMapTable';

export default function HomePage() {
  return (
    <>
      <div>
        <h1>Welcome To Donkey Betz</h1>
        <p>
          <a className="btn btn-outline-secondary me-2" href="/dev/route-explorer">
            🗺 Explore Routes
          </a>
        </p>
        <RouteMapTable />
      </div>
    </>
  );
}