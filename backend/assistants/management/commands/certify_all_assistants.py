from django.core.management.base import BaseCommand, call_command

class Command(BaseCommand):
    help = "Generate diagnostic reports and auto-certify all assistants"

    def handle(self, *args, **options):
        call_command("generate_diagnostic_reports")
        self.stdout.write(self.style.SUCCESS("Certification run complete"))
