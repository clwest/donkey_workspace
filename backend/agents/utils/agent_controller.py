from typing import Optional, List
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from openai import OpenAI

from mcp_core.models import (
    MemoryContext,
    Plan,
    Task,
    Agent,
    ActionLog,
    AgentThoughtLog,
    Tag,
)
from embeddings.helpers.helpers_io import save_embedding

client = OpenAI()
User = get_user_model()


class AgentController:
    def __init__(self, user: Optional[User] = None):
        self.user = user

    def reflect(
        self,
        content: str,
        important: bool = False,
        category: Optional[str] = None,
        tag_names: Optional[List[str]] = None,
    ) -> MemoryContext:
        memory = MemoryContext.objects.create(
            target_content_type=ContentType.objects.get_for_model(User),
            target_object_id=self.user.id if self.user else None,
            content=content,
            important=important,
            category=category,
        )

        if tag_names:
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(
                    name=name, defaults={"slug": name.lower().replace(" ", "-")}
                )
                memory.tags.add(tag)

        self.log_action("reflect", f"Saved reflection: {content[:60]}")
        save_embedding(memory)
        return memory

    def create_plan(
        self,
        title: str,
        description: str = "",
        memory_context: Optional[MemoryContext] = None,
    ) -> Plan:
        plan = Plan.objects.create(
            title=title,
            description=description,
            memory_context=memory_context,
            created_by=self.user,
        )
        self.log_action("create", f"Created plan: {title}")
        save_embedding(plan)
        return plan

    def create_task(
        self,
        title: str,
        plan: Optional[Plan] = None,
        description: str = "",
        project: Optional[str] = None,
        assigned_to: Optional[Agent] = None,
    ) -> Task:
        task = Task.objects.create(
            title=title,
            description=description,
            plan=plan,
            project=project,
            assigned_to=assigned_to,
        )
        self.log_action("create", f"Created task: {title}")
        save_embedding(task)
        return task

    def assign_agent(self, task: Task, agent: Agent) -> Task:
        task.assigned_to = agent
        task.save()
        self.log_action(
            "assign", f"Assigned task '{task.title}' to agent '{agent.name}'"
        )
        return task

    def log_action(
        self,
        action_type: str,
        description: str,
        related_agent: Optional[Agent] = None,
        related_task: Optional[Task] = None,
        related_plan: Optional[Plan] = None,
    ) -> ActionLog:
        return ActionLog.objects.create(
            action_type=action_type,
            description=description,
            performed_by=self.user,
            related_agent=related_agent,
            related_task=related_task,
            related_plan=related_plan,
        )

    def think_with_agent(self, agent: Agent) -> str:
        prompt = f"""
        You are an AI agent named {agent.name}.
        Your specialty is: {agent.specialty or 'general problem solving'}.
        Purpose: {agent.metadata.get('purpose', '...') if agent.metadata else '...'}

        What are your current internal thoughts based on your identity and purpose?
        """

        thought_trace = ["Generated agent identity and purpose prompt."]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
        )

        thought = response.choices[0].message.content.strip()
        thought_trace.append("Received model response.")

        log = AgentThoughtLog.objects.create(
            agent=agent,
            thought=thought,
            thought_trace="\n".join(f"• {s}" for s in thought_trace),
        )

        save_embedding(log)
        return thought

    def chat_with_agent(
        self, agent: Agent, message: str, context: Optional[str] = None
    ) -> str:
        system_prompt = f"You are an AI agent named {agent.name}."
        if agent.specialty:
            system_prompt += f" Specialty: {agent.specialty}."
        if agent.metadata and agent.metadata.get("description"):
            system_prompt += f" Description: {agent.metadata['description']}"

        full_context = f"{context or ''}\n\nUser: {message}".strip()

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_context},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        reply = response.choices[0].message.content.strip()

        memory = MemoryContext.objects.create(
            target_content_type=ContentType.objects.get_for_model(Agent),
            target_object_id=agent.id,
            content=f"User: {message}\nAgent: {reply}",
            important=False,
            category="agent_chat",
        )
        save_embedding(memory)

        self.log_action("chat", f"Chatted with {agent.name}", related_agent=agent)

        return reply

    def log_thought(
        self, agent: Agent, thought: str, trace: Optional[List[str]] = None
    ) -> AgentThoughtLog:
        log = AgentThoughtLog.objects.create(
            agent=agent,
            thought=thought,
            thought_trace="\n".join(f"• {s}" for s in (trace or [])),
        )
        save_embedding(log)
        return log

    # CODEx MARKER: recommend_agent_for_task
    def recommend_agent_for_task(
        self, task_description: str, thread
    ) -> Optional[Agent]:
        """Select an agent based on tags, specialty, and thread overlap."""
        from agents.models import Agent as AgentModel
        from memory.models import MemoryEntry

        candidates = AgentModel.objects.all()
        best_score = 0.0
        best_agent = None
        thread_tags = (
            set(t.name.lower() for t in thread.tags.all())
            if hasattr(thread, "tags")
            else set()
        )

        for agent in candidates:
            score = 0.0
            if agent.specialty:
                for tag in thread_tags:
                    if tag in agent.specialty.lower():
                        score += 0.5
                        break
            if task_description.lower() in (agent.description or "").lower():
                score += 0.2
            if MemoryEntry.objects.filter(
                narrative_thread=thread, assistant=agent.parent_assistant
            ).exists():
                score += 0.3
            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent
