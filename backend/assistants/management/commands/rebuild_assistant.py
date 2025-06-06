# # File: backend/assistants/management/commands/rebuild_assistant.py
# from django.core.management.base import BaseCommand
# from assistants.models import Assistant
# from assistants.utils.bootstrap import bootstrap_assistant
# from memory.utils import initialize_memory_context
# from assistants.utils.rag_diagnostics import run_assistant_rag_test
# from memory.utils.glossary_inference import infer_glossary_anchors_from_memory
# from memory.utils.mutation_suggestions import generate_missing_mutations_for_assistant
# from assistants.utils.assistant_reflection_engine import reflect_now

# class Command(BaseCommand):
#     help = "Rebuild an assistant with updated memory, anchors, and RAG setup"

#     def add_arguments(self, parser):
#         parser.add_argument("--slug", type=str, required=True, help="Assistant slug to rebuild")

#     def handle(self, *args, **options):
#         slug = options["slug"]
#         try:
#             assistant = Assistant.objects.get(slug=slug)
#         except Assistant.DoesNotExist:
#             self.stdout.write(self.style.ERROR(f"Assistant '{slug}' not found."))
#             return

#         self.stdout.write(self.style.SUCCESS(f"Rebuilding assistant '{slug}'..."))

#         # Step 1: Initialize memory context
#         initialize_memory_context(assistant)

#         # Step 2: Infer glossary anchors from memory
#         infer_glossary_anchors_from_memory(assistant)

#         # Step 3: Generate missing mutation suggestions
#         generate_missing_mutations_for_assistant(slug, stdout=self.stdout)

#         # Step 4: Run RAG diagnostics
#         run_assistant_rag_test(assistant, disable_scope=False)

#         # Step 5: Run reflection
#         reflect_now(assistant.slug)

#         self.stdout.write(self.style.SUCCESS(f"Assistant '{slug}' rebuilt successfully."))