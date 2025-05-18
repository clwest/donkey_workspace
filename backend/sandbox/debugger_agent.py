from models import Fault, Task, Agent


class DebuggerAgent:
    def __init__(self, db_session):
        self.db = db_session

    def find_open_faults(self):
        return Fault.query.filter(Fault.status == "open").all()

    def suggest_debugging_agent(self):
        faults = self.find_open_faults()
        agents = Agent.query.all()
        suggestions = []

        for fault in faults:
            task = Task.query.get(fault.task_id)
            if task and agents:
                # Crude logic: suggest the same agent assigned to the original task, fallback random
                if task.assigned_agent:
                    assigned_agent = Agent.query.filter_by(
                        name=task.assigned_agent
                    ).first()
                    if assigned_agent:
                        agent = assigned_agent
                    else:
                        agent = agents[fault.id % len(agents)]
                else:
                    agent = agents[fault.id % len(agents)]

                suggestions.append(
                    {
                        "fault_id": fault.id,
                        "task_description": (
                            task.description if task else "Unknown task"
                        ),
                        "suggested_debugger": agent.name,
                    }
                )
        return suggestions

    def dashboard_debug_summary(self):
        return {
            "open_faults": len(self.find_open_faults()),
            "debugger_suggestions": self.suggest_debugging_agent(),
        }
