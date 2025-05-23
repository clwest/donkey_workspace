import { useParams } from "react-router-dom";
import GuildFundingPanel from "../../components/guilds/GuildFundingPanel";

export default function GuildFundingPage() {
  const { id } = useParams();
  return <GuildFundingPanel guildId={id} />;
}
