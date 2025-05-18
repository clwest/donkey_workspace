from assistants.models import AssistantObjective
from prompts.utils.openai_utils import complete_chat  

def generate_objectives_from_prompt(assistant, project, prompt_text):
    system = "You are an assistant planning expert. Given a prompt, generate 3 clear objectives."
    user = (
        f"Assistant Prompt:\n{prompt_text}\n\n"
        "Create 3 key objectives for this assistant. "
        "Each should be in the format:\n"
        "Objective Title: A short, one-sentence description."
    )

    result = complete_chat(system=system, user=user)
    if not result:
        print("⚠️ No objectives returned.")
        return

    lines = [line.strip() for line in result.strip().split("\n") if ":" in line]
    for line in lines:
        try:
            title, desc = line.split(":", 1)
            AssistantObjective.objects.create(
                assistant=assistant,
                project=project,
                title=title.strip(),
                description=desc.strip(),
            )
        except Exception as e:
            print(f"⚠️ Failed to parse line: {line}\nError: {e}")