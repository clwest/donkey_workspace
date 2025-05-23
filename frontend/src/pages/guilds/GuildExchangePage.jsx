import { useParams } from "react-router-dom";
import GuildExchangeDashboard from "../../components/guilds/GuildExchangeDashboard";

export default function GuildExchangePage() {
  const { id } = useParams();
  return <GuildExchangeDashboard guildId={id} />;
}
