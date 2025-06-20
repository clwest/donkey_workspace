import {
  Routes,
  Route,
  useParams,
  useNavigate,
  useLocation,
} from "react-router-dom";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";
import ProfilePage from "./pages/auth/ProfilePage";
import LogoutPage from "./pages/auth/LogoutPage";
import OnboardingWizardPage from "./pages/onboarding/OnboardingWizardPage";
import RitualOnboardingPage from "./pages/onboarding/RitualOnboardingPage";
import OnboardingWorldPage from "./pages/onboarding/OnboardingWorldPage";
import ArchetypeSelectionChamberPage from "./pages/onboarding/ArchetypeSelectionChamberPage";
import SummoningRitualConsolePage from "./pages/onboarding/SummoningRitualConsolePage";
import PersonalityOnboardingPage from "./pages/onboarding/PersonalityOnboardingPage";
import FirstUseTourPage from "./pages/onboarding/FirstUseTourPage";
import UserMythpathInitializerPage from "./pages/onboarding/UserMythpathInitializerPage";
import GlossaryBootPage from "./pages/onboarding/GlossaryBootPage";
import OnboardingPage from "./pages/assistants/OnboardingPage";
import WorldTimelinePage from "./pages/WorldTimelinePage";
import AssistantMythRebirthPage from "./pages/assistant/myth/AssistantMythRebirthPage";
import CodexBriefingPage from "./pages/codex/CodexBriefingPage";
import AssistantTutorialPage from "./pages/assistant/tutorial/AssistantTutorialPage";
import MythOSLandingPage from "./pages/MythOSLandingPage";
import WelcomePage from "./pages/WelcomePage";
import WelcomeBackPage from "./pages/home/WelcomeBackPage";
import useUserInfo from "./hooks/useUserInfo";
import useAuthGuard from "./hooks/useAuthGuard";
import ProtectedRoute from "./components/ProtectedRoute";

import PromptsPage from "./pages/prompts/PromptsPage";
import PromptDetailView from "./pages/prompts/PromptDetailView";
import PromptRemixPage from "./pages/prompts/PromptRemixPage";
import CreatePromptPage from "./pages/prompts/CreatePromptPage";
import EditPromptPage from "./pages/prompts/EditPromptPage";
import PromptCreationAssistant from "./pages/assistant/prompts/PromptCreationAssistant";
import PromptCapsuleManagerPage from "./pages/prompts/PromptCapsuleManagerPage";
import SwarmAgentRewirePage from "./pages/swarm/SwarmAgentRewirePage";
import RoleCollisionPage from "./pages/swarm/RoleCollisionPage";
import NarrativeMutationSimulatorPage from "./pages/simulation/NarrativeMutationSimulatorPage";
import MythgraphViewerPage from "./pages/mythgraph/MythgraphViewerPage";

// MCP_CORE
import ReflectionPage from "./pages/mcp_core/reflections/ReflectionPage";
import ReflectionHistoryPage from "./pages/mcp_core/reflections/ReflectionHistoryPage";
import ReflectionDetailPage from "./pages/mcp_core/reflections/ReflectionDetailPage";
import ReflectionTagsPage from "./pages/mcp_core/reflections/ReflectionTagsPage";
import HotTagsPage from "./pages/mcp_core/reflections/HotTagsPage";
import RecentReflectionsPage from "./pages/mcp_core/recent/RecentReflectionsPage";
import CustomReflectionPage from "./pages/mcp_core/reflections/CustomReflectionPage";
import PlanningPage from "./pages/dev/PlanningPage";
import PlanningGraphPage from "./pages/plan/PlanningGraphPage";
import TaskAssignmentPage from "./pages/plan/TaskAssignmentPage";
import ExecutionChainPage from "./pages/plan/ExecutionChainPage";
import BeliefForecastPage from "./pages/forecast/BeliefForecastPage";
import { SHOW_INACTIVE_ROUTES } from "./config/ui";
import ThreadDetailPage from "./pages/mcp_core/threads/ThreadDetailPage";
import ThreadsOverviewPage from "./pages/mcp_core/threads/ThreadsOverviewPage";
import ThreadEditorPage from "./pages/mcp_core/threads/ThreadEditorPage";
import AssistantSessionsPage from "./pages/assistant/sessions/AssistantSessionsPage";
import AssistantSessionDetailPage from "./pages/assistant/sessions/AssistantSessionDetailPage";
import apiFetch from "./utils/apiClient";

{
  /*User Memories */
}
import MemoryBrowserPage from "./pages/memories/entries/MemoryBrowserPage";
import MemoryDetailPage from "./pages/memories/entries/MemoryDetailPage";
import BookmarkedMemoriesPage from "./pages/memories/entries/BookmarkedMemoriesPage";

import MemoryChainBuilderPage from "./pages/memories/chains/MemoryChainBuilderPage";
import MemoryChainViewerPage from "./pages/memories/chains/MemoryChainViewerPage";
import MemoryChainsListPage from "./pages/memories/chains/MemoryChainsListPage";
import MemoryChainDetailPage from "./pages/memories/chains/MemoryChainDetailPage"; // 👈 ADD THIS
import MemoryEntryCreatePage from "./pages/memories/entries/MemoryEntryCreatePage";
import RelayChainViewerPage from "./pages/relay/chains/RelayChainViewerPage";

{
  /** Assistant */
}
import AssistantDashboardPage from "./pages/assistant/common/AssistantDashboardPage";
import AssistantList from "./pages/assistant/common/AssistantList";
import CertifiedAssistantsPage from "./pages/assistants/CertifiedAssistantsPage";
import AssistantDetailPage from "./pages/assistant/common/AssistantDetailPage";
import AssistantThoughtsPage from "./pages/assistant/common/AssistantThoughtsPage";
import AssistantThoughtDetailPage from "./pages/assistant/common/AssistantThoughtDetailPage";
import AssistantDemoPage from "./pages/assistant/common/AssistantDemoPage";
import DemoComparisonPage from "./pages/assistant/common/DemoComparisonPage";
import AssistantLauncherPage from "./pages/assistants/AssistantLauncherPage";
import AssistantIntroSplash from "./pages/assistant/common/AssistantIntroSplash";
import AssistantTrailRecap from "./pages/assistant/common/AssistantTrailRecap";
import TrustProfilePage from "./pages/assistants/trust/TrustProfilePage";
import GrowthPanelPage from "./pages/assistants/growth/GrowthPanelPage";
import AssistantPreferencesPage from "./pages/assistants/preferences/AssistantPreferencesPage";
import ChatWithAssistantPage from "./pages/assistant/common/ChatWithAssistantPage";
import ChatWithKnowledge from "./pages/assistants/[slug]/chat/ChatWithKnowledge";
import CreateNewAssistantPage from "./pages/assistant/common/CreateNewAssistantPage";
import EditAssistantPage from "./pages/assistant/common/EditAssistantPage";
import AssistantCapabilityEditor from "./pages/assistant/common/AssistantCapabilityEditor";
import AssistantInterfacePage from "./pages/assistant/interface/AssistantInterfacePage";
import AssistantRelayPage from "./pages/assistant/relay/AssistantRelayPage";
import RunTaskPage from "./pages/assistant/run_task/RunTaskPage";

import ProjectDetailPage from "./pages/assistant/projects/ProjectDetailPage";
import ProjectCreateFromMemoryPage from "./pages/assistant/projects/ProjectCreateFromMemoryPage";
import CreateProjectPage from "./pages/assistant/projects/CreateProjectPage";
import ProjectMissionBuilderPage from "./pages/assistant/projects/ProjectMissionBuilderPage";
import ProjectTaskBuilderPage from "./pages/assistant/projects/ProjectTaskBuilderPage";
import ProjectTaskEditor from "./pages/assistant/projects/ProjectTaskEditorPage";
import ProjectsDashboardPage from "./pages/assistant/projects/ProjectsDashboardPage";
import ProjectStatusBoardPage from "./pages/assistant/projects/ProjectStatusBoardPage";
import ProjectTaskManagerPage from "./pages/assistant/projects/ProjectTaskManagerPage";
import ProjectTimelinePage from "./pages/assistant/milestones/ProjectTimelinePage";
import ProjectObjectivesPage from "./pages/assistant/projects/ProjectObjectivesPage";
import AssistantThoughtLogPage from "./pages/assistant/thoughts/AssistantThoughtLogPage";
import ProjectThoughtLog from "./pages/assistant/thoughts/ProjectThoughtLog";
import AssistantThoughtMapPage from "./pages/assistant/thoughts/AssistantThoughtMap";
import AssistantMemoriesPage from "./pages/assistant/common/AssistantMemoriesPage";
import AssistantMemoryPage from "./pages/assistant/memory/AssistantMemoryPage";
import DelegationTracePage from "./pages/assistant/DelegationTracePage";
import AssistantSubAgentReflectionPage from "./pages/assistant/AssistantSubAgentReflectionPage";
import AssistantSelfReflectionPage from "./pages/assistants/AssistantSelfReflectionPage";
import DelegationSummaryPage from "./pages/assistants/DelegationSummaryPage";
import RagGroundingInspectorPage from "./pages/assistants/RagGroundingInspectorPage";
import RagDiagnosticsDashboard from "./pages/assistants/RagDiagnosticsDashboard";
import GlossaryDriftPage from "./pages/assistants/GlossaryDriftPage";
import GlossaryConvergencePage from "./pages/assistants/GlossaryConvergencePage";
import AnchorHealthDashboard from "./pages/assistants/AnchorHealthDashboard";
import AnchorConfidenceDashboard from "./pages/assistants/AnchorConfidenceDashboard";
import ToolConfidenceDashboard from "./pages/assistants/ToolConfidenceDashboard";
import DemoInsightsDashboard from "./pages/assistants/DemoInsightsDashboard";
import DemoSuccessShowcase from "./pages/assistants/DemoSuccessShowcase";
import DemoRecapPage from "./pages/assistants/DemoRecapPage";
import DemoOverlayPage from "./pages/assistants/DemoOverlayPage";
import DemoReplayPage from "./pages/assistants/DemoReplayPage";

import DemoFeedbackExplorer from "./pages/assistants/DemoFeedbackExplorer";

import ReflectionDriftHeatmapPage from "./pages/assistant/reflections/ReflectionDriftHeatmapPage";
import AssistantRagSelfTestPage from "./pages/assistants/AssistantRagSelfTestPage";
import AssistantDiagnosticsConsolePage from "./pages/assistants/AssistantDiagnosticsConsolePage";
import AssistantDiagnosticReportPage from "./pages/assistants/AssistantDiagnosticReportPage";
import SubAgentReflectionPage from "./pages/assistants/SubAgentReflectionPage";
import SkillGraphPage from "./pages/assistant/skills/SkillGraphPage";
import AssistantBadgesPage from "./pages/assistant/badges/AssistantBadgesPage";
import BadgesPage from "./pages/badges/BadgesPage";
import MemoryToTaskPage from "./pages/assistant/objectives/MemoryToTaskPage";
import MilestonesPage from "./pages/assistant/milestones/MilestonesPage";
import MilestoneCreatePage from "./pages/assistant/milestones/MilestoneCreatePage";
import MilestoneEditPage from "./pages/assistant/milestones/MilestoneEditPage";
import MemoryChainsPage from "./pages/assistant/memory_chains/MemoryChainsPage";
import MemoryNavigatorPage from "./pages/assistant/analysis/MemoryNavigatorPage";
import ArchetypeAffinityPage from "./pages/assistant/analysis/ArchetypeAffinityPage";
import BeliefEvolutionPage from "./pages/assistant/analysis/BeliefEvolutionPage";

import NextActionsPage from "./pages/assistant/objectives/NextActionsPage";
import ObjectivesPage from "./pages/assistant/objectives/ObjectivesPage";
import PrimaryAssistantDashboard from "./pages/assistant/dashboard/PrimaryAssistantDashboard";
import CreatePrimaryAssistantPage from "./pages/assistant/dashboard/CreatePrimaryAssistantPage";
import AssistantActionDashboardPage from "./pages/assistant/dashboard/AssistantActionDashboardPage";
import PrimaryAssistantPage from "./pages/assistant/common/PrimaryAssistantPage";

import AssistantSessionDashboardPage from "./pages/assistant/sessions/AssistantSessionDashboardPage";
import GroupedReflectionsPage from "./pages/mcp_core/reflections/GroupedReflectionsPage";
import SignalSourcesPage from "./pages/assistant/signal_sources/SignalSourcesPage";
import SignalCatchesPage from "./pages/assistant/signal_catches/SignalCatchesPage";
import CouncilDashboardPage from "./pages/assistant/council/CouncilDashboardPage";

import ReflectionsPage from "./pages/assistant/reflections/ReflectionsPage";
import MemoryReflectionPage from "./pages/memories/reflections/MemoryReflectionPage";
import AssistantReflectPage from "./pages/assistant/reflections/AssistantReflectPage";
import UserReflectPage from "./pages/assistant/UserReflectPage";
import AssistantReflectionLogsPage from "./pages/assistant/reflections/AssistantReflectionLogsPage";
import AssistantReplayLogsPage from "@/pages/assistant/replays/AssistantReplayLogsPage";
import AssistantReplayDiffPage from "@/pages/assistant/replays/AssistantReplayDiffPage";
import AssistantReplayAuditPage from "./pages/assistants/AssistantReplayAuditPage";
import RAGPlaybackPanel from "./pages/assistants/playback/RAGPlaybackPanel";
import AssistantReflectionGroupsPage from "./pages/assistants/AssistantReflectionGroupsPage";
import AssistantReflectionGroups from "./pages/assistants/AssistantReflectionGroups";
import AssistantDriftDiagnosticsPage from "./pages/assistants/AssistantDriftDiagnosticsPage";
import AssistantInsightsPage from "./pages/assistants/insights/AssistantInsightsPage";
import FeedbackSummaryPage from "./pages/assistant/feedback/FeedbackSummaryPage";
import DevDashboard from "./pages/dev/DevDashboard";
import RoutesDebugPage from "./pages/dev/RoutesDebugPage";
import RouteCheckPage from "./pages/dev/RouteCheckPage";
import RouteExplorerPage from "./pages/dev/RouteExplorerPage";
import RouteViewer from "./pages/dev/routes/RouteViewer";
import CapabilityStatus from "./pages/dev/routes/CapabilityStatus";
import DemoCheckupPage from "./pages/dev/DemoCheckupPage";
import FeedbackReviewPage from "./pages/dev/FeedbackReviewPage";
import OnboardingDebugPage from "./pages/dev/OnboardingDebugPage";
import PageNotFound from "./pages/PageNotFound";
import GroupedReflectionPage from "./pages/dev/GroupedReflectionPage";
import GroupedReflectionDetailPage from "./pages/dev/GroupedReflectionDetailPage";
import DevDocReflectionDetailPage from "./pages/dev/DevDocReflectionDetailPage";
import IntelDebugTools from "./pages/dev/debug/IntelDebugTools";
import EmbeddingDebug from "./pages/dev/debug/EmbeddingDebug";
import EmbeddingAuditPanel from "./pages/dev/debug/EmbeddingAuditPanel";
import AuthDebugPage from "./pages/dev/AuthDebugPage";
import EmbeddingDriftLog from "./pages/dev/debug/EmbeddingDriftLog";
import UploadQueuePage from "./pages/dev/upload/UploadQueuePage";
import DocumentBrowserPage from "./pages/intel_core/DocumentBrowserPage";
import TopicSetListPage from "./pages/intel_core/TopicSetListPage";
import DocumentDetailPage from "./pages/intel_core/DocumentDetailPage";

import ImageGalleryPage from "./pages/media/ImageGalleryPage";
import ImageCreatePage from "./pages/media/ImageCreatePage";
import CharacterListPage from "./pages/media/CharacterListPage";
import StoryListPage from "./pages/media/StoryListPage";
import AgentPage from "./pages/agents/AgentPage";
import AgentDetailPage from "./pages/agents/AgentDetailPage";
import AgentArchivePage from "./pages/agents/AgentArchivePage";
import AgentDashboardPage from "./pages/agents/AgentDashboardPage";
import TrainedAgentsPage from "./pages/agents/TrainedAgentsPage";
import SwarmTimelinePage from "./pages/agents/SwarmTimelinePage";
import SwarmGraphPage from "./pages/swarm/SwarmGraphPage";
import OrchestrationTimelinePage from "./pages/orchestration/OrchestrationTimelinePage";
import RitualRewirePage from "./pages/ritual/RitualRewirePage";
import MemoryTimelinePage from "./pages/timeline/MemoryTimelinePage";
import RoutingHistoryPage from "./pages/assistant/routing/RoutingHistoryPage";
import StoryboardEditorPage from "./pages/storyboard/StoryboardEditorPage";
import NarrativeEventDetailPage from "./pages/storyboard/NarrativeEventDetailPage";
import RealityShaperDashboard from "./pages/lore/RealityShaperDashboard";
import WorldDashboardPage from "./pages/mythos/WorldDashboardPage";
import AssistantPresenceMapPage from "./pages/mythos/AssistantPresenceMapPage";
import MythflowHeatmapPage from "./pages/mythos/MythflowHeatmapPage";
import MythpathExplorerPage from "./pages/mythos/MythpathExplorerPage";
import SymbolicMemorySynthesizerPage from "./pages/memory/SymbolicMemorySynthesizerPage";
import TemporalReflectionLogsPage from "./pages/reflection/TemporalReflectionLogsPage";

import MotionTestPage from "./pages/ui/MotionTestPage";
import MemoryEchoPage from "./pages/memories/entries/MemoryEchoPage";
import AssistantAuraPage from "./pages/assistant/common/AssistantAuraPage";
import KeeperLogViewer from "./pages/keeper/KeeperLogViewer";
import ProphecyEnginePage from "./pages/prophecy/ProphecyEnginePage";
import MemoryPredictionPage from "./pages/memory/MemoryPredictionPage";
import RitualForecastPage from "./pages/ritual/RitualForecastPage";
import RitualRewardsPage from "./pages/ritual/RitualRewardsPage";
import AssistantEconomyPage from "./pages/assistant/economy/AssistantEconomyPage";
import AssistantDeployPage from "./pages/assistant/deploy/AssistantDeployPage";
import AssistantToolsPage from "./pages/assistant/tools/AssistantToolsPage";
import ToolListPage from "./pages/tools/ToolListPage";
import ToolDetailPage from "./pages/tools/ToolDetailPage";
import ReviewIngestPage from "./pages/assistant/review_ingest/ReviewIngestPage";
import ArenaActivePage from "./pages/arena/ArenaActivePage";
import GuildFundingPage from "./pages/guilds/GuildFundingPage";
import GuildExchangePage from "./pages/guilds/GuildExchangePage";
import TokenMarketPage from "./pages/market/TokenMarketPage";
import RitualMarketPage from "./pages/market/RitualMarketPage";
import TrendReactivityPage from "./pages/assistant/trends/TrendReactivityPage";
import SystemStabilityPage from "./pages/system/SystemStabilityPage";
import RitualGrantPage from "./pages/ritual/RitualGrantPage";
import MythOSCodexPage from "./pages/mythos/MythOSCodexPage";
import DreamframePage from "./pages/agents/DreamframePage";
import MythOSRitualsPage from "./pages/mythos/MythOSRitualsPage";
import AssistantForkPage from "./pages/assistant/common/AssistantForkPage";
import AssistantLineagePage from "./pages/assistant/common/AssistantLineagePage";
import AssistantIdentityPage from "./pages/assistant/identity/AssistantIdentityPage";
import AssistantMythpathPage from "./pages/assistant/mythpath/AssistantMythpathPage";
import CodexConvergePage from "./pages/codex/CodexConvergePage";
import CodexProofPage from "./pages/codex/CodexProofPage";
import CodexContractPage from "./pages/codex/CodexContractPage";
import CodexClauseMutatorPage from "./pages/codex/CodexClauseMutatorPage";
import CascadeGraphPage from "./pages/codex/CascadeGraphPage";
import StabilizationCampaignPage from "./pages/codex/StabilizationCampaignPage";
import StabilizationCampaignDetailPage from "./pages/codex/StabilizationCampaignDetailPage";
import CodexInheritancePage from "./pages/codex/CodexInheritancePage";
import RitualContainersPage from "./pages/ritual/RitualContainersPage";
import ReplayEnginePage from "./pages/replay/ReplayEnginePage";
import FaultInjectorPage from "./pages/fault/FaultInjectorPage";
import DreamRebirthPage from "./pages/agents/DreamRebirthPage";
import ContinuityAnchorPage from "./pages/anchor/ContinuityAnchorPage";
import SymbolicAnchorAdminPage from "./pages/anchor/SymbolicAnchorAdminPage";
import SymbolicAnchorReviewPage from "./pages/anchor/SymbolicAnchorReviewPage";
import SymbolicAnchorDetailPage from "./pages/anchor/SymbolicAnchorDetailPage";
import GlossaryMutationReviewPanel from "./pages/anchor/GlossaryMutationReviewPanel";
import AnchorDiagnosticsPage from "./pages/anchor/AnchorDiagnosticsPage";
import AnchorSuggestionPage from "./pages/anchor/AnchorSuggestionPage";
import ArbitrationCouncilPage from "./pages/guilds/ArbitrationCouncilPage";
import TreatyForgePage from "./pages/treaty/TreatyForgePage";
import FederationCodicesPage from "./pages/federation/FederationCodicesPage";
import RitualLawPage from "./pages/law/RitualLawPage";
import DeployStandardsPage from "./pages/deploy/DeployStandardsPage";
import FederatedSummonPage from "./pages/summon/FederatedSummonPage";
import MemorySandboxPage from "./pages/memory/MemorySandboxPage";
import ThoughtLogPanel from "./pages/assistant/thoughts/ThoughtLogPanel";
import PersonalityDeckBuilder from "./pages/assistant/deck/PersonalityDeckBuilder";
import CodexPromptOrchestrator from "./pages/codex/CodexPromptOrchestrator";
import PromptMutationExplorer from "./pages/codex/PromptMutationExplorer";
import RitualComposerPage from "./pages/ritual/RitualComposerPage";
import RitualForkReplayPage from "./pages/ritual/RitualForkReplayPage";
import MythOSProjectComposerPage from "./pages/project/MythOSProjectComposerPage";
import PromptDebuggerPage from "./pages/debug/PromptDebuggerPage";
import RagRecallDebugPage from "./pages/debug/RagRecallDebugPage";
import RAGDiagnosticsDashboard from "./pages/debug/RAGDiagnosticsDashboard";
import RagFailureTable from "./pages/debug/RagFailureTable";
import CLIRunner from "./pages/dev/CLIRunnerPage";
import CLILogViewer from "./pages/dev/CLILogViewer";
import ToolIndexPanel from "./pages/tools/ToolIndexPanel";
import ChunkStatsDashboard from "./pages/debug/ChunkStatsDashboard";
import RagTestLogViewer from "./pages/assistants/RagTestLogViewer";
import SwarmTaskEvolutionPage from "./pages/evolve/SwarmTaskEvolutionPage";
import SkillPlannerPage from "./pages/plan/SkillPlannerPage";
import PromptFeedbackPage from "./pages/feedback/PromptFeedbackPage";

import { ToastContainer } from "react-toastify";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import { useState, useEffect } from "react";
import useOnboardingStatus from "./hooks/useOnboardingStatus";
import ActivityPage from "./pages/ActivityPage";
import "react-toastify/dist/ReactToastify.css";

// Route wrappers to force remount on param change
const AssistantDetailRoute = () => {
  const { slug } = useParams();
  return <AssistantDetailPage key={slug} />;
};

const DocumentDetailRoute = () => {
  const { id } = useParams();
  return <DocumentDetailPage key={id} />;
};

const AgentDetailRoute = () => {
  const { slug } = useParams();
  return <AgentDetailPage key={slug} />;
};

const ProjectDetailRoute = () => {
  const { id } = useParams();
  return <ProjectDetailPage key={id} />;
};

export default function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const toggleSidebar = () => setSidebarCollapsed((c) => !c);
  const location = useLocation();
  const publicPaths = [
    "/login",
    "/register",
    "/",
    "/welcome",
    "/assistants/launch",
    "/assistants/demo",
  ];
  const allowUnauth = publicPaths.includes(location.pathname);
  const { user, authChecked, authError } = useAuthGuard({
    allowUnauthenticated: allowUnauth,
  });
  const userInfo = useUserInfo();
  const navigate = useNavigate();
  const [onboardingRedirectHandled, setOnboardingRedirectHandled] =
    useState(false);
  const {
    loading: onboardingLoading,
    primarySlug,
    onboardingComplete,
  } = useOnboardingStatus();

  useEffect(() => {
    if (!user || onboardingLoading || onboardingRedirectHandled) return;
    const path = location.pathname;
    if (onboardingComplete) {
      if (path === "/assistants/create" || path.startsWith("/onboarding")) {
        navigate(`/assistants/${primarySlug}`, { replace: true });
        setOnboardingRedirectHandled(true);
      }
    } else if (userInfo?.assistant_count === 0) {
      if (path !== "/assistants/create") {
        navigate("/assistants/create", { replace: true });
        setOnboardingRedirectHandled(true);
      }
    } else if (!path.startsWith("/assistants")) {
      const slug = userInfo?.primary_assistant_slug || primarySlug;
      navigate(slug ? `/assistants/${slug}` : "/assistants/create", {
        replace: true,
      });
      setOnboardingRedirectHandled(true);
    }
  }, [
    user,
    onboardingLoading,
    onboardingComplete,
    primarySlug,
    userInfo,
    location.pathname,
    navigate,
    onboardingRedirectHandled,
  ]);

  if (!authChecked) {
    return <div className="text-center mt-5">Loading...</div>;
  }

  if (authError) {
    return (
      <div className="container mt-5">
        <div className="alert alert-warning">
          Authentication error. Please refresh or log in again.
        </div>
      </div>
    );
  }

  return (
    <div className="d-flex">
      <Sidebar collapsed={sidebarCollapsed} />
      <div className="flex-grow-1">
        <ToastContainer position="bottom-right" autoClose={3000} />
        <Navbar onToggleSidebar={toggleSidebar} />

        <Routes>
          {/* Auth */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/logout" element={<LogoutPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/onboarding" element={<UserMythpathInitializerPage />} />
          <Route path="/onboarding/world" element={<OnboardingWorldPage />} />
          <Route path="/onboarding/glossary" element={<GlossaryBootPage />} />
          <Route
            path="/onboarding/archetype"
            element={<ArchetypeSelectionChamberPage />}
          />
          <Route
            path="/onboarding/summon"
            element={<SummoningRitualConsolePage />}
          />
          <Route
            path="/onboarding/personality"
            element={<PersonalityOnboardingPage />}
          />
          <Route path="/onboarding/wizard" element={<OnboardingWizardPage />} />
          <Route path="/onboarding/ritual" element={<RitualOnboardingPage />} />
          <Route path="/codex/briefing" element={<CodexBriefingPage />} />
          <Route
            path="/assistant/:id/tutorial"
            element={<AssistantTutorialPage />}
          />
          {/* Prompts */}
          <Route path="/" element={<MythOSLandingPage />} />
          <Route path="/home" element={<WelcomeBackPage />} />
          <Route path="/welcome" element={<WelcomePage />} />
          <Route path="/prompts" element={<PromptsPage />} />
          <Route
            path="/prompts/capsules"
            element={<PromptCapsuleManagerPage />}
          />
          <Route
            path="/feedback/prompts/:id"
            element={<PromptFeedbackPage />}
          />
          <Route path="/prompts/:slug/remix" element={<PromptRemixPage />} />
          <Route path="/prompts/:slug/edit" element={<EditPromptPage />} />
          <Route path="/prompts/:slug" element={<PromptDetailView />} />
          <Route path="/prompts/create" element={<CreatePromptPage />} />
          <Route
            path="/prompts/assistant"
            element={<PromptCreationAssistant />}
          />
          {/* Memories */}
          <Route path="/memories/new" element={<MemoryEntryCreatePage />} />
          <Route path="/memories" element={<MemoryBrowserPage />} /> {/* ➕ */}
          <Route
            path="/memories/bookmarked"
            element={<BookmarkedMemoriesPage />}
          />
          <Route path="/memories/:id" element={<MemoryDetailPage />} />{" "}
          <Route path="/memory/:id/echo" element={<MemoryEchoPage />} />
          {/* 🧠 */}
          <Route path="/memories/reflect" element={<MemoryReflectionPage />} />
          <Route path="/memories/chains" element={<MemoryChainsListPage />} />
          <Route
            path="/memories/chains/create"
            element={<MemoryChainBuilderPage />}
          />
          <Route
            path="/memories/chains/:id"
            element={<MemoryChainViewerPage />}
          />
          <Route
            path="/memories/chain/:id"
            element={<MemoryChainDetailPage />}
          />{" "}
          {/* 🔗 Chain Viewer */}
          <Route path="/relay/chains/:id" element={<RelayChainViewerPage />} />
          {/* Assistant & Projects */}
          <Route path="/assistants" element={<AssistantList />} />
          <Route path="/certified/assistants" element={<CertifiedAssistantsPage />} />
          <Route
            path="/assistant-dashboard"
            element={<AssistantDashboardPage />}
          />
          <Route path="/tour" element={<FirstUseTourPage />} />
          <Route
            path="/assistants/create"
            element={<CreateNewAssistantPage />}
          />
          <Route
            path="/assistants/onboarding"
            element={
              <ProtectedRoute>
                <OnboardingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assistants/primary"
            element={<PrimaryAssistantDashboard />}
          />
          <Route
            path="/assistants/primary/create"
            element={<CreatePrimaryAssistantPage />}
          />
          <Route
            path="/assistants/primary/dashboard"
            element={<PrimaryAssistantPage />}
          />
          {/* Project and Milestone Routes */}
          <Route
            path="/assistants/projects/create"
            element={<CreateProjectPage />}
          />
          <Route
            path="/assistants/projects"
            element={<ProjectsDashboardPage />}
          />
          <Route
            path="/assistants/projects/create-from-memory"
            element={<ProjectCreateFromMemoryPage />}
          />
          <Route
            path="/assistants/projects/:id"
            element={<ProjectDetailRoute />}
          />
          <Route
            path="/assistants/projects/:id/build"
            element={<ProjectTaskBuilderPage />}
          />
          <Route
            path="/assistants/projects/:id/edit-tasks"
            element={<ProjectTaskEditor />}
          />
          <Route
            path="/assistants/projects/:id/tasks"
            element={<ProjectTaskManagerPage />}
          />
          <Route
            path="/assistants/projects/:id/status-board"
            element={<ProjectStatusBoardPage />}
          />
          <Route
            path="/assistants/projects/:id/mission"
            element={<ProjectMissionBuilderPage />}
          />
          <Route
            path="/assistants/projects/:projectId/timeline"
            element={<ProjectTimelinePage />}
          />
          <Route
            path="/assistants/projects/:projectId/objectives"
            element={<ProjectObjectivesPage />}
          />
          <Route
            path="/assistants/projects/:projectId/milestones"
            element={<MilestonesPage />}
          />
          <Route
            path="/assistants/projects/:projectId/milestones/create"
            element={<MilestoneCreatePage />}
          />
          <Route
            path="/assistants/projects/:projectId/milestones/:milestoneId/edit"
            element={<MilestoneEditPage />}
          />
          {/* Top-level Assistant Views */}
          <Route
            path="/assistants/projects/:id/thoughts"
            element={<ProjectThoughtLog />}
          />
          <Route
            path="/assistants/next-actions"
            element={<NextActionsPage />}
          />
          <Route
            path="/assistants/memory/:memoryId/to-task"
            element={<MemoryToTaskPage />}
          />
          <Route
            path="/assistants/memory-chains"
            element={<MemoryChainsPage />}
          />
          <Route path="/assistants/reflections" element={<ReflectionsPage />} />
          <Route
            path="/assistants/sessions/"
            element={<AssistantSessionsPage />}
          />
          <Route
            path="/assistants/sessions/:sessionId"
            element={<AssistantSessionDetailPage />}
          />
          <Route path="/assistants/sources" element={<SignalSourcesPage />} />
          <Route path="/assistants/signals" element={<SignalCatchesPage />} />
          <Route
            path="/assistants/routing-history"
            element={<RoutingHistoryPage />}
          />
          <Route
            path="/assistants/council/:id"
            element={<CouncilDashboardPage />}
          />
          <Route path="/assistants-demos" element={<AssistantDemoPage />} />
          <Route
            path="/assistants/demos/compare"
            element={<DemoComparisonPage />}
          />
          <Route
            path="/assistants/demos/insights"
            element={<DemoInsightsDashboard />}
          />
          <Route
            path="/assistants/demos/success"
            element={<DemoSuccessShowcase />}
          />
          <Route
            path="/assistants/demos/feedback"
            element={<DemoFeedbackExplorer />}
          />
          <Route
            path="/assistants/launch"
            element={<AssistantLauncherPage />}
          />
          <Route
            path="/assistants/:slug/intro"
            element={<AssistantIntroSplash />}
          />
          <Route
            path="/assistants/:slug/trail"
            element={<AssistantTrailRecap />}
          />
          <Route
            path="/assistants/:slug/demo_recap/:sessionId"
            element={<DemoRecapPage />}
          />
          <Route
            path="/assistants/:slug/demo_overlay/"
            element={<DemoOverlayPage />}
          />
          <Route
            path="/assistants/:slug/demo_replay/:sessionId"
            element={<DemoReplayPage />}
          />
          <Route
            path="/assistants/:slug/trust_profile/"
            element={<TrustProfilePage />}
          />
          <Route
            path="/assistants/:slug/growth/"
            element={<GrowthPanelPage />}
          />
          <Route
            path="/assistants/:slug/preferences/"
            element={<AssistantPreferencesPage />}
          />
          <Route
            path="/assistants/:slug/settings/"
            element={<AssistantPreferencesPage />}
          />
          {/* Assistant Detail Subroutes */}
          <Route
            path="/assistants/:slug/log_thought"
            element={<AssistantThoughtLogPage />}
          />
          <Route
            path="/assistants/:slug/thoughts/:id"
            element={<AssistantThoughtDetailPage />}
          />
          <Route
            path="/assistants/:slug/thought-map"
            element={<AssistantThoughtMapPage />}
          />
          <Route
            path="/assistants/:slug/timeline"
            element={<MemoryNavigatorPage />}
          />
          <Route
            path="/assistants/:slug/affinity"
            element={<ArchetypeAffinityPage />}
          />
          <Route
            path="/assistants/:slug/belief"
            element={<BeliefEvolutionPage />}
          />
          <Route
            path="/assistants/:slug/memory"
            element={<AssistantMemoryPage />}
          />
          <Route
            path="/assistants/:slug/memories"
            element={<AssistantMemoriesPage />}
          />
          <Route
            path="/assistants/:slug/objectives"
            element={<ObjectivesPage />}
          />
          <Route
            path="/assistants/:slug/reflections"
            element={<AssistantReflectionLogsPage />}
          />
          <Route
            path="/assistants/:slug/reflections/groups/"
            element={<AssistantReflectionGroupsPage />}
          />
          <Route
            path="/assistants/:slug/reflection-groups/"
            element={<AssistantReflectionGroups />}
          />
          <Route
            path="/assistants/:slug/insights/"
            element={<AssistantInsightsPage />}
          />
          <Route
            path="/assistants/:slug/replays"
            element={<AssistantReplayLogsPage />}
          />
          <Route
            path="/assistants/:slug/replays/:uuid"
            element={<AssistantReplayDiffPage />}
          />
          <Route
            path="/assistants/:slug/replay"
            element={<AssistantReplayAuditPage />}
          />
          <Route
            path="/assistants/:slug/rag_playback/:uuid"
            element={<RAGPlaybackPanel />}
          />
          <Route
            path="/assistants/:slug/rag_playback/compare/:uuid"
            element={<RAGPlaybackPanel compareMode />}
          />
          <Route
            path="/assistants/:slug/reflect"
            element={<UserReflectPage />}
          />
          <Route
            path="/assistants/:slug/dashboard"
            element={<AssistantActionDashboardPage />}
          />
          <Route
            path="/assistants/:slug/sessions"
            element={<AssistantSessionDashboardPage />}
          />
          <Route
            path="/assistants/:slug/delegation-trace"
            element={<DelegationTracePage />}
          />
          <Route
            path="/assistants/:slug/subagent_reflect/:id"
            element={<AssistantSubAgentReflectionPage />}
          />
          <Route
            path="/delegation/subagent_reflect/:id"
            element={<AssistantSubAgentReflectionPage />}
          />
          <Route
            path="/assistants/:slug/reflect_on_self/"
            element={<AssistantSelfReflectionPage />}
          />
          <Route
            path="/assistants/:slug/summarize_delegations/"
            element={<DelegationSummaryPage />}
          />
          <Route
            path="/assistants/:slug/rag-inspector"
            element={<RagGroundingInspectorPage />}
          />
          <Route
            path="/assistants/:slug/rag-drift"
            element={<GlossaryDriftPage />}
          />
          <Route
            path="/assistants/:slug/rag_diagnostics/"
            element={<RagDiagnosticsDashboard />}
          />
          <Route
            path="/assistants/:slug/rag-tests/"
            element={<RagTestLogViewer />}
          />
          <Route
            path="/assistants/:slug/anchor-health"
            element={<AnchorHealthDashboard />}
          />
          <Route
            path="/assistants/:slug/anchor-confidence"
            element={<AnchorConfidenceDashboard />}
          />
          <Route
            path="/assistants/:slug/tools/confidence"
            element={<ToolConfidenceDashboard />}
          />
          <Route
            path="/assistants/:slug/reflections/drift_map"
            element={<ReflectionDriftHeatmapPage />}
          />
          <Route
            path="/assistants/:slug/badges"
            element={<AssistantBadgesPage />}
          />
          <Route path="/badges" element={<BadgesPage />} />
          <Route
            path="/assistants/:slug/glossary"
            element={<GlossaryConvergencePage />}
          />
          <Route
            path="/assistants/:slug/diagnostics"
            element={<AssistantRagSelfTestPage />}
          />
          <Route
            path="/assistants/:slug/diagnostics/console/"
            element={<AssistantDiagnosticsConsolePage />}
          />
          <Route
            path="/assistants/:slug/diagnostic_report/"
            element={<AssistantDiagnosticReportPage />}
          />
          <Route
            path="/assistants/:slug/diagnostics/drift/"
            element={<AssistantDriftDiagnosticsPage />}
          />
          <Route
            path="/assistants/:slug/subagent_reflect/:event_id/"
            element={<SubAgentReflectionPage />}
          />
          <Route
            path="/assistants/:slug/skillgraph"
            element={<SkillGraphPage />}
          />
          <Route
            path="/assistants/:slug/thoughts"
            element={<AssistantThoughtsPage />}
          />
          <Route
            path="/assistants/:slug/feedback"
            element={<FeedbackSummaryPage />}
          />
          <Route
            path="/assistants/:slug/chat"
            element={<ChatWithAssistantPage />}
          />
          <Route
            path="/assistants/:slug/chat/knowledge"
            element={<ChatWithKnowledge />}
          />
          <Route
            path="/assistants/:id/thoughts"
            element={<ThoughtLogPanel />}
          />
          <Route
            path="/assistants/:id/deck"
            element={<PersonalityDeckBuilder />}
          />
          <Route
            path="/assistants/:id/interface"
            element={<AssistantInterfacePage />}
          />
          <Route path="/assistants/:id/run-task" element={<RunTaskPage />} />
          <Route
            path="/assistants/:id/relay"
            element={<AssistantRelayPage />}
          />
          <Route path="/assistants/:id/fork" element={<AssistantForkPage />} />
          <Route
            path="/assistants/:id/lineage"
            element={<AssistantLineagePage />}
          />
          <Route
            path="/assistants/:id/rebirth"
            element={<AssistantMythRebirthPage />}
          />
          <Route
            path="/assistants/:id/identity"
            element={<AssistantIdentityPage />}
          />
          <Route
            path="/assistants/:id/mythpath"
            element={<AssistantMythpathPage />}
          />
          <Route
            path="/assistants/:slug/edit"
            element={<EditAssistantPage />}
          />
          <Route
            path="/assistants/:slug/capabilities"
            element={<AssistantCapabilityEditor />}
          />
          <Route path="/assistants/:slug" element={<AssistantDetailRoute />} />
          {/* MCP Core */}
          <Route path="/reflect" element={<ReflectionPage />} />
          <Route path="/reflections" element={<ReflectionHistoryPage />} />
          <Route path="/reflections/:id" element={<ReflectionDetailPage />} />
          <Route path="/reflection-tags" element={<ReflectionTagsPage />} />
          <Route
            path="/reflection-tags/:tag"
            element={<ReflectionTagsPage />}
          />
          <Route
            path="/grouped-reflections"
            element={<GroupedReflectionsPage />}
          />
          <Route path="/hot-tags" element={<HotTagsPage />} />
          <Route
            path="/recent-reflections"
            element={<RecentReflectionsPage />}
          />
          <Route path="/activity" element={<ActivityPage />} />
          <Route
            path="/reflections/custom"
            element={<CustomReflectionPage />}
          />
          <Route path="/threads/overview" element={<ThreadsOverviewPage />} />
          <Route path="/threads" element={<ThreadsOverviewPage />} />
          <Route path="/threads/editor" element={<ThreadEditorPage />} />
          <Route path="/threads/:id" element={<ThreadDetailPage />} />
          <Route path="/dev-dashboard" element={<DevDashboard />} />
          <Route path="/dev/routes" element={<RouteViewer />} />
          <Route path="/dev/route-health" element={<RouteViewer />} />
          <Route path="/dev/route-explorer" element={<RouteExplorerPage />} />
          <Route
            path="/dev/routes/capabilities"
            element={<CapabilityStatus />}
          />
          <Route path="/dev/route-check" element={<RouteCheckPage />} />
          <Route path="/dev/debug/intel" element={<IntelDebugTools />} />
          <Route
            path="/devtools/embedding-debug"
            element={<EmbeddingDebug />}
          />
          <Route
            path="/devtools/embedding-audit"
            element={<EmbeddingAuditPanel />}
          />
          <Route path="/devtools/drift-log" element={<EmbeddingDriftLog />} />
          <Route path="/dev/auth-debug" element={<AuthDebugPage />} />
          <Route
            path="/dev/onboarding-debug"
            element={<OnboardingDebugPage />}
          />
          <Route path="/dev/upload" element={<UploadQueuePage />} />
          <Route path="/dev/upload/queue" element={<UploadQueuePage />} />
          <Route path="/dev/demo-checkup" element={<DemoCheckupPage />} />
          <Route path="/dev/feedback-review" element={<FeedbackReviewPage />} />
          <Route path="/debug/prompts" element={<PromptDebuggerPage />} />
          <Route path="/debug/rag-recall" element={<RagRecallDebugPage />} />
          <Route path="/debug/rag-failures" element={<RagFailureTable />} />
          <Route path="/debug/rag" element={<RAGDiagnosticsDashboard />} />
          <Route path="/dev/cli" element={<CLIRunner />} />
          <Route path="/cli/logs/:id/" element={<CLILogViewer />} />
          <Route path="/debug/chunk-stats" element={<ChunkStatsDashboard />} />
          <Route path="/planning" element={<PlanningPage />} />
          <Route path="/plan/graph" element={<PlanningGraphPage />} />
          <Route path="/plan/assign" element={<TaskAssignmentPage />} />
          <Route path="/plan/chains" element={<ExecutionChainPage />} />
          <Route path="/plan/skills/:id" element={<SkillPlannerPage />} />
          <Route
            path="/grouped-reflection"
            element={<GroupedReflectionPage />}
          />
          <Route
            path="/grouped-reflection/:id"
            element={<GroupedReflectionDetailPage />}
          />
          <Route path="/agents" element={<AgentPage />} />
          <Route path="/agents/dashboard" element={<AgentDashboardPage />} />
          <Route path="/agents/archive" element={<AgentArchivePage />} />
          <Route path="/agents/trained" element={<TrainedAgentsPage />} />
          <Route path="/swarm/timeline" element={<SwarmTimelinePage />} />
          <Route path="/swarm/graph" element={<SwarmGraphPage />} />
          <Route path="/swarm/collisions" element={<RoleCollisionPage />} />
          <Route path="/ritual/rewire" element={<RitualRewirePage />} />
          <Route
            path="/orchestration/timeline"
            element={<OrchestrationTimelinePage />}
          />
          <Route path="/swarm/rewire" element={<SwarmAgentRewirePage />} />
          <Route path="/timeline" element={<WorldTimelinePage />} />
          <Route path="/timeline/memory" element={<MemoryTimelinePage />} />
          <Route
            path="/memory/sandbox/:assistantId"
            element={<MemorySandboxPage />}
          />
          <Route path="/agents/:slug" element={<AgentDetailRoute />} />
          <Route path="/intel/documents" element={<DocumentBrowserPage />} />
          <Route path="/topic_sets" element={<TopicSetListPage />} />
          
          <Route
            path="/intel/documents/:id"
            element={<DocumentDetailRoute />}
          />
          <Route path="/images" element={<ImageGalleryPage />} />
          <Route path="/images/new" element={<ImageCreatePage />} />
          <Route path="/characters" element={<CharacterListPage />} />
          <Route path="/stories" element={<StoryListPage />} />
          <Route path="/storyboard" element={<StoryboardEditorPage />} />
          <Route
            path="/storyboard/events/:id"
            element={<NarrativeEventDetailPage />}
          />
          <Route path="/dashboard/world" element={<WorldDashboardPage />} />
          <Route
            path="/map/assistants"
            element={<AssistantPresenceMapPage />}
          />
          <Route path="/heatmap/mythflow" element={<MythflowHeatmapPage />} />
          <Route path="/timeline/explore" element={<MythpathExplorerPage />} />
          <Route
            path="/memory/synthesize"
            element={<SymbolicMemorySynthesizerPage />}
          />
          <Route
            path="/reflection/logs"
            element={<TemporalReflectionLogsPage />}
          />
          <Route path="/lore" element={<RealityShaperDashboard />} />
          {/* MythOS symbolic gateways */}
          <Route path="/codex" element={<MythOSCodexPage />} />
          <Route path="/codex/evolve" element={<PromptMutationExplorer />} />
          <Route
            path="/codex/orchestrator/:assistantId"
            element={<CodexPromptOrchestrator />}
          />
          <Route path="/codex/converge" element={<CodexConvergePage />} />
          <Route path="/codex/proof" element={<CodexProofPage />} />
          <Route
            path="/codex/contracts/:promptId"
            element={<CodexContractPage />}
          />
          <Route
            path="/codex/mutator/:clauseId"
            element={<CodexClauseMutatorPage />}
          />
          <Route
            path="/codex/cascade/:clauseId"
            element={<CascadeGraphPage />}
          />
          <Route
            path="/codex/stabilize"
            element={<StabilizationCampaignPage />}
          />
          <Route
            path="/codex/stabilize/:campaignId"
            element={<StabilizationCampaignDetailPage />}
          />
          <Route
            path="/codex/inheritance/:assistantId"
            element={<CodexInheritancePage />}
          />
          <Route path="/dream" element={<DreamframePage />} />
          <Route path="/dream/rebirth" element={<DreamRebirthPage />} />
          <Route path="/ritual" element={<MythOSRitualsPage />} />
          <Route path="/ritual/containers" element={<RitualContainersPage />} />
          <Route path="/ritual/composer" element={<RitualComposerPage />} />
          <Route
            path="/ritual/fork/replay"
            element={<RitualForkReplayPage />}
          />
          <Route path="/reflection" element={<ReflectionPage />} />
          <Route path="/prophecy/engine" element={<ProphecyEnginePage />} />
          <Route path="/memory/predict" element={<MemoryPredictionPage />} />
          <Route path="/ritual/forecast" element={<RitualForecastPage />} />
          <Route path="/forecast/belief" element={<BeliefForecastPage />} />
          <Route path="/evolve/swarm" element={<SwarmTaskEvolutionPage />} />
          <Route path="/ritual/rewards" element={<RitualRewardsPage />} />
          <Route path="/replay/engine" element={<ReplayEnginePage />} />
          <Route
            path="/simulate/narrative"
            element={<NarrativeMutationSimulatorPage />}
          />
          <Route path="/mythgraph/:id" element={<MythgraphViewerPage />} />
          <Route path="/fault/injector" element={<FaultInjectorPage />} />
          <Route path="/deploy/standards" element={<DeployStandardsPage />} />
          <Route
            path="/project/composer"
            element={<MythOSProjectComposerPage />}
          />
          <Route path="/summon/federated" element={<FederatedSummonPage />} />
          <Route path="/anchor/continuity" element={<ContinuityAnchorPage />} />
          <Route
            path="/anchor/mutations"
            element={<GlossaryMutationReviewPanel />}
          />
          <Route path="/anchor/suggestions" element={<AnchorSuggestionPage />} />
          <Route
            path="/anchor/symbolic"
            element={<SymbolicAnchorReviewPage />}
          />
          <Route
            path="/anchor/symbolic/:slug"
            element={<SymbolicAnchorDetailPage />}
          />
          <Route path="/anchor/diagnostics" element={<AnchorDiagnosticsPage />} />
          <Route path="/keeper/logs" element={<KeeperLogViewer />} />
          <Route path="/tools" element={<ToolListPage />} />
          <Route path="/tools/index" element={<ToolIndexPanel />} />
          <Route path="/tools/:id" element={<ToolDetailPage />} />
          <Route
            path="/assistants/:id/economy"
            element={<AssistantEconomyPage />}
          />
          <Route
            path="/assistants/:id/deploy"
            element={<AssistantDeployPage />}
          />
          <Route
            path="/assistants/:id/tools"
            element={<AssistantToolsPage />}
          />
          <Route
            path="/assistants/:slug/review-ingest/:doc_id"
            element={<ReviewIngestPage />}
          />
          <Route path="/arena/active" element={<ArenaActivePage />} />
          <Route path="/guilds/council" element={<ArbitrationCouncilPage />} />
          <Route path="/guilds/:id/funding" element={<GuildFundingPage />} />
          <Route path="/guilds/:id/exchange" element={<GuildExchangePage />} />
          <Route path="/treaty/forge" element={<TreatyForgePage />} />
          <Route
            path="/federation/codices"
            element={<FederationCodicesPage />}
          />
          <Route path="/law/ritual" element={<RitualLawPage />} />
          <Route path="/market/tokens" element={<TokenMarketPage />} />
          <Route path="/market/rituals" element={<RitualMarketPage />} />
          <Route path="/ritual/grants" element={<RitualGrantPage />} />
          <Route
            path="/assistants/trend-reactivity"
            element={<TrendReactivityPage />}
          />
          <Route path="/system/stability" element={<SystemStabilityPage />} />
          <Route path="/ui/motion" element={<MotionTestPage />} />
          <Route path="/assistants/:id/aura" element={<AssistantAuraPage />} />
          <Route path="/assistants/sources" element={<SignalSourcesPage />} />
          <Route path="/assistants/signals" element={<SignalCatchesPage />} />
          <Route
            path="/assistants/routing-history"
            element={<RoutingHistoryPage />}
          />
          <Route
            path="/assistants/council/:id"
            element={<CouncilDashboardPage />}
          />
          <Route path="*" element={<PageNotFound />} />
        </Routes>
      </div>
    </div>
  );
}
