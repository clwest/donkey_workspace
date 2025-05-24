from rest_framework import serializers
from .models.assistant import (
    Assistant,
   
    AssistantChatMessage,
    AssistantMessage,
    AssistantRelayMessage,
    ChatSession,
    SpecializationDriftLog,
    
    DebateSession,
    DebateThoughtLog,
    DebateSummary,
    RoutingSuggestionLog,
    DelegationEvent,
    SessionHandoff,
    AssistantHandoffLog,
    AssistantSwitchEvent,
    AssistantSkill,
    SignalSource,
    SignalCatch,
    CouncilSession,
    CouncilThought,
    CouncilOutcome,
    OracleLayer,
    ProphecyNode,
    AssistantGuild,
    AssistantCivilization,
    AssistantReputation,
    ConscienceModule,
    DecisionFramework,
    PurposeRouteMap,
    AutonomyNarrativeModel,
   
)
from .models.project import (
    AssistantProject,
    AssistantObjective,
    AssistantTask,
    AssistantProjectRole,
    AssistantPromptLink,
    AssistantMemoryChain,
)
from assistants.models.interface import (
    SymbolicUXPlaybook,
    RoleDrivenUITemplate,
    SymbolicToolkitRegistry,
)
from .models.reflection import (
    AssistantReflectionLog,
    AssistantReflectionInsight,
)
from .models.thoughts import (
    AssistantThoughtLog,
    EmotionalResonanceLog,
    CollaborationLog,
)
from .models.extensions import (
    HapticFeedbackChannel,
    AssistantSensoryExtensionProfile,
)
from .models.project import AssistantNextAction, ProjectPlanningLog
from .models.core import  AssistantMythLayer

from project.models import (
    Project,
    ProjectTask,
    ProjectMilestone,
    ProjectMemoryLink,
    ProjectType,
    ProjectStatus,
)
from mcp_core.serializers_tags import TagSerializer
from intel_core.serializers import DocumentSerializer
from tools.models import Tool

from project.serializers import (
    ProjectSerializer,
    ProjectTaskSerializer,
    ProjectMilestoneSerializer,
    ProjectMemoryLinkSerializer,
)
from mcp_core.serializers_tags import NarrativeThreadSerializer
from mcp_core.models import NarrativeThread
from story.models import NarrativeEvent
from memory.models import MemoryEntry
from memory.serializers import MemoryEntrySerializer
from assistants.utils.bootstrap_helpers import generate_objectives_from_prompt


class DelegationEventSerializer(serializers.ModelSerializer):
    """Serialize delegation history for API responses."""

    parent = serializers.CharField(source="parent_assistant.name", read_only=True)
    child = serializers.CharField(source="child_assistant.name", read_only=True)
    child_slug = serializers.CharField(source="child_assistant.slug", read_only=True)
    memory_id = serializers.UUIDField(source="triggering_memory.id", read_only=True)
    session_id = serializers.UUIDField(source="triggering_session.id", read_only=True)
    objective_title = serializers.CharField(source="objective.title", read_only=True)

    class Meta:
        model = DelegationEvent
        fields = [
            "parent",
            "child",
            "child_slug",
            "handoff",
            "reason",
            "summary",
            "score",
            "trust_label",
            "notes",
            "memory_id",
            "session_id",
            "objective_title",
            "created_at",
        ]


class RecentDelegationEventSerializer(serializers.ModelSerializer):
    """Lightweight serializer used for the recent delegations feed."""

    parent = serializers.CharField(source="parent_assistant.name", read_only=True)
    child = serializers.CharField(source="child_assistant.name", read_only=True)
    child_slug = serializers.CharField(source="child_assistant.slug", read_only=True)

    class Meta:
        model = DelegationEvent
        fields = [
            "id",
            "parent",
            "child",
            "child_slug",
            "reason",
            "summary",
            "created_at",
        ]


class SessionHandoffSerializer(serializers.ModelSerializer):
    from_assistant = serializers.CharField(source="from_assistant.name", read_only=True)
    to_assistant = serializers.CharField(source="to_assistant.name", read_only=True)

    class Meta:
        model = SessionHandoff
        fields = [
            "id",
            "from_assistant",
            "to_assistant",
            "reason",
            "handoff_summary",
            "created_at",
        ]


class AssistantHandoffLogSerializer(serializers.ModelSerializer):
    from_assistant = serializers.CharField(source="from_assistant.name", read_only=True)
    to_assistant = serializers.CharField(source="to_assistant.name", read_only=True)

    class Meta:
        model = AssistantHandoffLog
        fields = [
            "id",
            "from_assistant",
            "to_assistant",
            "project",
            "summary",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AssistantSwitchEventSerializer(serializers.ModelSerializer):
    from_assistant = serializers.CharField(source="from_assistant.name", read_only=True)
    to_assistant = serializers.CharField(source="to_assistant.name", read_only=True)

    class Meta:
        model = AssistantSwitchEvent
        fields = [
            "id",
            "from_assistant",
            "to_assistant",
            "reason",
            "automated",
            "created_at",
        ]


class RoutingSuggestionLogSerializer(serializers.ModelSerializer):
    """Serialize routing suggestion logs for API responses."""

    assistant = serializers.CharField(source="suggested_assistant.name", read_only=True)
    assistant_slug = serializers.CharField(
        source="suggested_assistant.slug", read_only=True
    )

    class Meta:
        model = RoutingSuggestionLog
        fields = [
            "id",
            "context_summary",
            "tags",
            "assistant",
            "assistant_slug",
            "confidence_score",
            "reasoning",
            "selected",
            "user_feedback",
            "timestamp",
        ]
        read_only_fields = fields


class AssistantSkillSerializer(serializers.ModelSerializer):
    related_tools = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Tool.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = AssistantSkill
        fields = [
            "id",
            "name",
            "description",
            "confidence",
            "related_tools",
            "related_tags",
        ]
        read_only_fields = ["id"]


class AssistantReflectionLogSerializer(serializers.ModelSerializer):
    linked_event = serializers.SerializerMethodField()

    class Meta:
        model = AssistantReflectionLog
        fields = [
            "id",
            "project",
            "title",
            "mood",
            "summary",
            "llm_summary",
            "linked_event",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_linked_event(self, obj):
        if obj.linked_event:
            return {
                "id": str(obj.linked_event.id),
                "title": obj.linked_event.title,
            }
        return None


class AssistantReflectionLogListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    linked_event = serializers.SerializerMethodField()

    class Meta:
        model = AssistantReflectionLog
        fields = [
            "id",
            "created_at",
            "project",
            "summary",
            "linked_memory",
            "linked_event",
            "tags",
        ]
        read_only_fields = ["id", "created_at"]

    def get_linked_event(self, obj):
        if obj.linked_event:
            return {
                "id": str(obj.linked_event.id),
                "title": obj.linked_event.title,
            }
        return None


class AssistantReflectionLogDetailSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    linked_memory = MemoryEntrySerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    linked_event = serializers.SerializerMethodField()
    raw_summary = serializers.CharField(
        source="raw_prompt", allow_null=True, read_only=True
    )

    class Meta:
        model = AssistantReflectionLog
        fields = [
            "id",
            "assistant",
            "project",
            "summary",
            "raw_summary",
            "raw_prompt",
            "llm_summary",
            "insights",
            "linked_memory",
            "linked_event",
            "tags",
            "mood",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_linked_event(self, obj):
        if obj.linked_event:
            return {
                "id": str(obj.linked_event.id),
                "title": obj.linked_event.title,
            }
        return None


class ProjectPlanningLogSerializer(serializers.ModelSerializer):
    related_object_repr = serializers.SerializerMethodField()

    class Meta:
        model = ProjectPlanningLog
        fields = [
            "id",
            "project",
            "timestamp",
            "event_type",
            "summary",
            "related_object_repr",
        ]
        read_only_fields = ["id", "timestamp"]

    def get_related_object_repr(self, obj):
        return str(obj.related_object) if obj.related_object else None


class SpecializationDriftLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecializationDriftLog
        fields = [
            "id",
            "drift_score",
            "summary",
            "trigger_type",
            "auto_flagged",
            "resolved",
            "requires_retraining",
            "timestamp",
        ]
        read_only_fields = fields


class EmotionalResonanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionalResonanceLog
        fields = [
            "id",
            "assistant",
            "source_memory",
            "detected_emotion",
            "intensity",
            "comment",
            "context_tags",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AssistantNextActionSerializer(serializers.ModelSerializer):
    assigned_agent_slug = serializers.CharField(
        source="assigned_agent.slug", read_only=True
    )
    assigned_agent_name = serializers.CharField(
        source="assigned_agent.name", read_only=True
    )
    linked_thread_title = serializers.CharField(
        source="linked_thread.title", read_only=True
    )

    class Meta:
        model = AssistantNextAction
        fields = [
            "id",
            "objective",
            "content",
            "completed",
            "created_at",
            "assigned_agent",
            "assigned_agent_slug",
            "assigned_agent_name",
            "linked_thread",
            "linked_thread_title",
            "importance_score",
        ]
        read_only_fields = ["id", "created_at"]


class AssistantObjectiveSerializer(serializers.ModelSerializer):
    delegated_assistant_slug = serializers.CharField(
        source="delegated_assistant.slug", read_only=True
    )
    delegated_assistant_name = serializers.CharField(
        source="delegated_assistant.name", read_only=True
    )
    generated_from_reflection = serializers.UUIDField(
        source="generated_from_reflection.id", read_only=True
    )
    reflection_created_at = serializers.DateTimeField(
        source="generated_from_reflection.created_at", read_only=True
    )
    source_memory = serializers.UUIDField(source="source_memory.id", read_only=True)
    linked_event = serializers.PrimaryKeyRelatedField(
        queryset=NarrativeEvent.objects.all(),
        required=False,
        allow_null=True,
    )
    linked_event_title = serializers.CharField(
        source="linked_event.title", read_only=True
    )

    class Meta:
        model = AssistantObjective
        fields = [
            "id",
            "project",
            "title",
            "description",
            "is_completed",
            "delegated_assistant_slug",
            "delegated_assistant_name",
            "generated_from_reflection",
            "reflection_created_at",
            "source_memory",
            "linked_event",
            "linked_event_title",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AssistantTaskSerializer(serializers.ModelSerializer):
    assigned_assistant_name = serializers.CharField(
        source="assigned_assistant.name", read_only=True
    )
    assigned_assistant_slug = serializers.CharField(
        source="assigned_assistant.slug", read_only=True
    )

    class Meta:
        model = AssistantTask
        fields = [
            "id",
            "project",
            "objective",
            "title",
            "status",
            "notes",
            "priority",
            "source_type",
            "source_id",
            "proposed_by",
            "assigned_assistant",
            "assigned_assistant_name",
            "assigned_assistant_slug",
            "tone",
            "generated_from_mood",
            "confirmed_by_user",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AssistantObjectiveWithTasksSerializer(AssistantObjectiveSerializer):
    tasks = AssistantTaskSerializer(many=True, read_only=True)

    class Meta(AssistantObjectiveSerializer.Meta):
        fields = AssistantObjectiveSerializer.Meta.fields + ["tasks"]


class AssistantProjectSerializer(serializers.ModelSerializer):
    objectives = AssistantObjectiveSerializer(many=True, read_only=True)
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)
    next_actions = AssistantNextActionSerializer(many=True, read_only=True)
    reflections = serializers.SerializerMethodField()
    delegations = DelegationEventSerializer(
        many=True, read_only=True, source="delegation_events"
    )
    core_project_id = serializers.SerializerMethodField()

    class Meta:
        model = AssistantProject
        fields = [
            "id",
            "title",
            "slug",
            "assistant",
            "description",
            "mood",
            "memory_shift_score",
            "objectives",
            "milestones",
            "next_actions",
            "reflections",
            "delegations",
            "core_project_id",
            "created_at",
        ]
        read_only_fields = ["id", "slug", "created_at"]

    def get_core_project_id(self, obj):
        project = obj.linked_projects.first()
        return project.id if project else None

    def get_reflections(self, obj):
        return [
            {"id": r.id, "summary": r.summary}
            for r in obj.reflections.all()[:5]
        ]


class ProjectOverviewSerializer(serializers.ModelSerializer):
    objective_count = serializers.SerializerMethodField()
    active_milestones = serializers.SerializerMethodField()

    class Meta:
        model = AssistantProject
        fields = [
            "id",
            "title",
            "slug",
            "objective_count",
            "active_milestones",
            "summary",
            "mood",
            "memory_shift_score",
        ]

    def get_objective_count(self, obj):
        return obj.objectives.count()

    def get_active_milestones(self, obj):
        return obj.milestones.count()


class AssistantProjectRoleSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(source="assistant.name", read_only=True)
    assistant_slug = serializers.CharField(source="assistant.slug", read_only=True)
    avatar = serializers.CharField(source="assistant.avatar", read_only=True)

    class Meta:
        model = AssistantProjectRole
        fields = [
            "id",
            "assistant",
            "assistant_name",
            "assistant_slug",
            "avatar",
            "project",
            "role_name",
            "description",
            "is_primary",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {"project": {"required": False}}


# assistants/serializers.py
class AssistantDetailSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    projects = AssistantProjectSerializer(many=True, read_only=True)
    current_project = ProjectOverviewSerializer(read_only=True)
    child_assistants = serializers.SerializerMethodField()
    skills = AssistantSkillSerializer(many=True, read_only=True)
    source_document_title = serializers.SerializerMethodField()
    source_document_url = serializers.SerializerMethodField()
    drift_logs = SpecializationDriftLogSerializer(many=True, read_only=True)
    recent_drift = serializers.SerializerMethodField()

    class Meta:
        model = Assistant
        fields = [
            "id",
            "slug",
            "name",
            "archetype_path",
            "description",
            "specialty",
            "avatar",
            "is_active",
            "is_demo",
            "is_primary",
            "is_ephemeral",
            "expiration_event",
            "needs_recovery",
            "live_relay_enabled",
            "memory_summon_enabled",
            "collaboration_style",
            "preferred_conflict_resolution",
            "system_prompt",
            "personality",
            "tone",
            "persona_summary",
            "traits",
            "capabilities",
            "motto",
            "values",
            "ideology",
            "is_alignment_flexible",
            "documents",
            "projects",
            "current_project",
            "preferred_model",
            "mood_stability_index",
            "child_assistants",
            "skills",
            "drift_logs",
            "recent_drift",
            "source_document_title",
            "source_document_url",
            "created_at",
        ]
        read_only_fields = ["id", "slug", "created_at"]

    def get_child_assistants(self, obj):
        return AssistantSerializer(obj.sub_assistants.all(), many=True).data

    def get_source_document_title(self, obj):
        doc = obj.documents.first()
        return doc.title if doc else None

    def get_source_document_url(self, obj):
        doc = obj.documents.first()
        return doc.source_url if doc else None

    def get_recent_drift(self, obj):
        from django.utils import timezone
        from datetime import timedelta

        log = obj.drift_logs.order_by("-timestamp").first()
        if log and log.timestamp >= timezone.now() - timedelta(days=1):
            return SpecializationDriftLogSerializer(log).data
        return None


# serializers.py

from .constants import THOUGHT_CATEGORY_CHOICES


class AssistantThoughtLogSerializer(serializers.ModelSerializer):
    assistant_slug = serializers.SlugRelatedField(
        source="assistant", read_only=True, slug_field="slug"
    )
    assistant_name = serializers.CharField(source="assistant.name", read_only=True)
    linked_memory = serializers.PrimaryKeyRelatedField(read_only=True)
    linked_memories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    linked_reflection = serializers.PrimaryKeyRelatedField(read_only=True)
    linked_event = serializers.SerializerMethodField()
    linked_memory_preview = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    narrative_thread = serializers.PrimaryKeyRelatedField(read_only=True)
    replayed_thread = serializers.PrimaryKeyRelatedField(read_only=True)
    parent_thought = serializers.PrimaryKeyRelatedField(read_only=True)
    linked_event = serializers.PrimaryKeyRelatedField(read_only=True)
    category = serializers.ChoiceField(
        choices=THOUGHT_CATEGORY_CHOICES, default="other"
    )

    class Meta:
        model = AssistantThoughtLog
        fields = [
            "id",
            "assistant_slug",
            "assistant_name",
            "project",
            "thought",
            "thought_trace",
            "integrity_status",
            "thought_type",
            "role",
            "mode",
            "mood",
            "feedback",
            "event",
            "origin",
            "source_reason",
            "tags",
            "category",
            "linked_memory",  # UUID only
            "linked_memories",
            "linked_reflection",
            "parent_thought",
            "linked_event",
            "linked_memory_preview",  # 🆕 Text preview
            "narrative_thread",
            "replayed_thread",
            "linked_event",
            "summoned_memory_ids",
            "empathy_response",
            "resonated_with_user",
            "created_at",
        ]

    def get_linked_memory_preview(self, obj):
        return obj.linked_memory.event if obj.linked_memory else None

    def get_linked_event(self, obj):
        if obj.linked_event:
            return {
                "id": str(obj.linked_event.id),
                "title": obj.linked_event.title,
            }
        return None


class AssistantPromptLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantPromptLink
        fields = ["id", "project", "prompt", "reason", "linked_at"]
        read_only_fields = ["id", "linked_at"]


class AssistantMemoryChainSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantMemoryChain
        fields = [
            "id",
            "project",
            "title",
            "description",
            "mode",
            "filter_tags",
            "exclude_types",
            "memories",
            "is_team_chain",
            "team_members",
            "linked_project",
            "shared_tags",
            "visibility_scope",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AssistantReflectionInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantReflectionInsight
        fields = ["id", "project", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class SignalSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignalSource
        fields = ["id", "platform", "name", "url", "priority", "active", "created_at"]
        read_only_fields = ["id", "created_at"]


class SignalCatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignalCatch
        fields = [
            "id",
            "source",
            "original_content",
            "summary",
            "score",
            "is_meaningful",
            "reviewed",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class HapticFeedbackChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = HapticFeedbackChannel
        fields = [
            "id",
            "feedback_name",
            "trigger_event",
            "intensity_level",
            "symbolic_context",
            "linked_assistant",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AssistantSensoryExtensionProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantSensoryExtensionProfile
        fields = [
            "id",
            "assistant",
            "supported_modes",
            "feedback_triggers",
            "memory_response_style",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AssistantCollaborationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assistant
        fields = [
            "id",
            "slug",
            "name",
            "collaboration_style",
            "preferred_conflict_resolution",
        ]


# assistants/serializers.py


class ProjectSerializer(serializers.ModelSerializer):
    tasks = ProjectTaskSerializer(many=True, read_only=True)
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)
    objectives = AssistantObjectiveSerializer(many=True, read_only=True)
    next_actions = AssistantNextActionSerializer(many=True, read_only=True)
    linked_memories = ProjectMemoryLinkSerializer(many=True, read_only=True)
    linked_prompts = AssistantPromptLinkSerializer(many=True, read_only=True)
    reflections = AssistantReflectionLogSerializer(many=True, read_only=True)
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Project  # ✅ Now pointing to the unified Project model
        fields = [
            "id",
            "slug",
            "title",
            "description",
            "created_at",
            "tasks",
            "milestones",
            "objectives",
            "next_actions",
            "linked_memories",
            "linked_prompts",
            "reflections",
            "summary",
        ]
        read_only_fields = ["id", "slug", "created_at"]

    def get_summary(self, obj):
        last = obj.reflections.order_by("-created_at").first()
        return last.llm_summary if last else None


class AssistantChatMessageSerializer(serializers.ModelSerializer):
    topic = serializers.SerializerMethodField()

    class Meta:
        model = AssistantChatMessage
        fields = [
            "uuid",
            "role",
            "content",
            "created_at",
            "feedback",
            "topic",
            "message_type",
            "audio_url",
            "image_url",
            "tts_model",
            "style",
        ]

    def get_topic(self, obj):
        return obj.topic.name if obj.topic else None


class ChatSessionSerializer(serializers.ModelSerializer):
    narrative_thread = NarrativeThreadSerializer(read_only=True)

    class Meta:
        model = ChatSession
        fields = "__all__"


class DebateThoughtLogSerializer(serializers.ModelSerializer):
    assistant = serializers.SlugRelatedField(read_only=True, slug_field="slug")

    class Meta:
        model = DebateThoughtLog
        fields = [
            "id",
            "debate_session",
            "assistant",
            "round",
            "position",
            "content",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class DebateSessionSerializer(serializers.ModelSerializer):
    logs = DebateThoughtLogSerializer(many=True, read_only=True)

    class Meta:
        model = DebateSession
        fields = ["id", "topic", "memory", "project", "created_at", "logs"]
        read_only_fields = ["id", "created_at"]


class DebateSummarySerializer(serializers.ModelSerializer):
    created_by = serializers.SlugRelatedField(read_only=True, slug_field="slug")

    class Meta:
        model = DebateSummary
        fields = ["id", "session", "summary", "created_by", "created_at"]
        read_only_fields = ["id", "created_at"]


class AssistantMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    recipient = serializers.SlugRelatedField(read_only=True, slug_field="slug")

    class Meta:
        model = AssistantMessage
        fields = [
            "id",
            "sender",
            "recipient",
            "content",
            "status",
            "created_at",
            "session",
            "related_memory",
        ]
        read_only_fields = ["id", "created_at"]


class AssistantRelayMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    recipient = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    thought_log = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = AssistantRelayMessage
        fields = [
            "id",
            "sender",
            "recipient",
            "content",
            "status",
            "delivered",
            "delivered_at",
            "responded",
            "sent_at",
            "responded_at",
            "thought_log",
        ]
        read_only_fields = [
            "id",
            "sent_at",
            "delivered",
            "delivered_at",
            "responded",
            "responded_at",
            "status",
            "thought_log",
        ]


class AssistantSerializer(serializers.ModelSerializer):
    current_project = ProjectOverviewSerializer(read_only=True)
    trust = serializers.SerializerMethodField()
    delegation_events_count = serializers.SerializerMethodField()
    average_delegation_score = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    empathy_tags = serializers.ListField(child=serializers.CharField(), read_only=True)
    preferred_scene_tags = serializers.ListField(
        child=serializers.CharField(), read_only=True
    )

    class Meta:
        model = Assistant
        fields = [
            "id",
            "name",
            "slug",
            "archetype_path",
            "tone",
            "persona_summary",
            "traits",
            "capabilities",
            "motto",
            "values",
            "ideology",
            "is_alignment_flexible",
            "specialty",
            "preferred_model",
            "mood_stability_index",
            "is_primary",
            "needs_recovery",
            "live_relay_enabled",
            "collaboration_style",
            "preferred_conflict_resolution",
            "current_project",
            "document_set",
            "embedding_index",
            "avg_empathy_score",
            "trust",
            "delegation_events_count",
            "average_delegation_score",
            "tags",
            "empathy_tags",
            "preferred_scene_tags",
        ]

    def get_trust(self, obj):
        from assistants.utils.delegation_helpers import get_trust_score

        return get_trust_score(obj)

    def get_delegation_events_count(self, obj):
        from assistants.models import DelegationEvent
        from django.utils import timezone

        week_ago = timezone.now() - timezone.timedelta(days=7)
        return DelegationEvent.objects.filter(
            child_assistant=obj, created_at__gte=week_ago
        ).count()

    def get_average_delegation_score(self, obj):
        from assistants.models import DelegationEvent
        from django.db.models import Avg

        return (
            DelegationEvent.objects.filter(child_assistant=obj).aggregate(
                avg=Avg("score")
            )["avg"]
            or 0
        )

    def get_tags(self, obj):
        from mcp_core.models import Tag
        from mcp_core.serializers_tags import TagSerializer

        tags = Tag.objects.filter(assistant_thoughts__assistant=obj).distinct()[:5]
        return TagSerializer(tags, many=True).data


class AssistantProjectSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantProject
        fields = [
            "id",
            "title",
            "slug",
            "status",
            "mood",
            "memory_shift_score",
            "created_at",
        ]


class BootstrapResultSerializer(serializers.Serializer):
    assistant = AssistantSerializer()
    project = AssistantProjectSummarySerializer()


from prompts.models import Prompt


class AssistantFromPromptSerializer(serializers.Serializer):
    prompt_id = serializers.UUIDField()
    assistant_name = serializers.CharField(required=False)
    preferred_model = serializers.CharField(default="gpt-4o")
    is_demo = serializers.BooleanField(default=False)
    parent_assistant_id = serializers.UUIDField(required=False, allow_null=True)
    parent_thread_id = serializers.UUIDField(required=False, allow_null=True)

    def create(self, validated_data):
        prompt = Prompt.objects.get(id=validated_data["prompt_id"])
        assistant_name = validated_data.get(
            "assistant_name", f"Assistant for {prompt.title}"
        )
        parent_assistant_id = validated_data.pop("parent_assistant_id", None)
        parent_thread_id = validated_data.pop("parent_thread_id", None)

        thread = None
        parent_assistant = None
        if parent_thread_id:
            thread = NarrativeThread.objects.filter(id=parent_thread_id).first()

        if not thread and parent_assistant_id:
            parent_assistant = Assistant.objects.filter(id=parent_assistant_id).first()
            if parent_assistant:
                parent_project = (
                    Project.objects.filter(assistant=parent_assistant)
                    .order_by("-created_at")
                    .first()
                )
                if not parent_project:
                    parent_project = (
                        Project.objects.filter(
                            assistant_project__assistant=parent_assistant
                        )
                        .order_by("-created_at")
                        .first()
                    )
                if parent_project:
                    thread = parent_project.narrative_thread

        if not thread:
            thread = NarrativeThread.objects.create(
                title=f"{assistant_name} Thread",
                summary=f"Auto-generated thread for {assistant_name}",
            )

        assistant = Assistant.objects.create(
            name=assistant_name,
            system_prompt=prompt,
            tone=prompt.tone or "neutral",
            personality="Bootstrapped from prompt",
            specialty=prompt.source or "general",
            preferred_model=validated_data["preferred_model"],
            is_demo=validated_data["is_demo"],
            parent_assistant=parent_assistant,
        )

        project = AssistantProject.objects.create(
            assistant=assistant,
            title=f"Auto Project for {assistant_name}",
            goal=f"This project exists to help the assistant fulfill: {prompt.title}",
            description=prompt.content[:500].strip(),
            status="active",
        )

        request = self.context.get("request")
        if request and getattr(request, "user", None) and request.user.is_authenticated:
            user = request.user
        else:
            from django.contrib.auth import get_user_model

            user = get_user_model().objects.first()

        Project.objects.create(
            user=user,
            title=f"{assistant_name} Project",
            description=prompt.content[:500].strip(),
            assistant=assistant,
            assistant_project=project,
            narrative_thread=thread,
            thread=thread,
            project_type=ProjectType.ASSISTANT,
            status=ProjectStatus.ACTIVE,
        )

        generate_objectives_from_prompt(assistant, project, prompt.content)
        return {
            "assistant": assistant,
            "project": project,
        }


class CouncilSessionSerializer(serializers.ModelSerializer):
    members = AssistantSerializer(many=True, read_only=True)

    class Meta:
        model = CouncilSession
        fields = [
            "id",
            "topic",
            "linked_memory",
            "project",
            "created_by",
            "status",
            "created_at",
            "members",
        ]
        read_only_fields = ["id", "created_at"]


class CouncilThoughtSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(source="assistant.name", read_only=True)

    class Meta:
        model = CouncilThought
        fields = [
            "id",
            "assistant",
            "assistant_name",
            "council_session",
            "content",
            "round",
            "is_final",
            "mood",
            "role",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CouncilOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouncilOutcome
        fields = ["council_session", "summary", "created_at"]
        read_only_fields = ["created_at"]


class CollaborationLogSerializer(serializers.ModelSerializer):
    participants = AssistantSerializer(many=True, read_only=True)

    class Meta:
        model = CollaborationLog
        fields = [
            "id",
            "participants",
            "project",
            "mood_state",
            "style_conflict_detected",
            "resolution_action",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

class OracleLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OracleLayer
        fields = [
            "id",
            "assistant",
            "memory_focus",
            "tone",
            "tag_scope",
            "summary_insight",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]



class ProphecyNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProphecyNode
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class AssistantMythLayerSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(source="assistant.name", read_only=True)

    class Meta:
        model = AssistantMythLayer
        fields = [
            "id",
            "assistant",
            "assistant_name",
            "origin_story",
            "legendary_traits",
            "summary",
            "archived",
            "created_at",
            "last_updated",
        ]
        read_only_fields = ["id", "created_at", "last_updated"]


class AssistantGuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantGuild
        fields = ["id", "name", "purpose", "founding_myth", "created_at"]
        read_only_fields = ["id", "created_at"]


class AssistantCivilizationSerializer(serializers.ModelSerializer):
    founding_guilds = AssistantGuildSerializer(many=True, read_only=True)
    myth_root_title = serializers.CharField(source="myth_root.title", read_only=True)

    class Meta:
        model = AssistantCivilization
        fields = [
            "id",
            "name",
            "myth_root",
            "myth_root_title",
            "founding_guilds",
            "belief_alignment",
            "symbolic_domain",
            "legacy_score",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AssistantReputationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantReputation
        fields = "__all__"
        read_only_fields = ["id", "updated_at"]


class ConscienceModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConscienceModule
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class DecisionFrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionFramework
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class PurposeRouteMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurposeRouteMap
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class AutonomyNarrativeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutonomyNarrativeModel
        fields = "__all__"
        read_only_fields = ["id", "created_at"]



class SymbolicUXPlaybookSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicUXPlaybook
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RoleDrivenUITemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleDrivenUITemplate

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SymbolicToolkitRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicToolkitRegistry
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


