from django.core.management.base import BaseCommand
import os
import re


class Command(BaseCommand):
    help = "Sorts all view functions in views.py by name"

    def handle(self, *args, **options):
        views_path = os.path.join("assistants", "views.py")  # Adjust if needed
        output_path = os.path.join("assistants", "views_sorted.py")

        if not os.path.exists(views_path):
            self.stderr.write("Could not find views.py")
            return

        with open(views_path, "r") as f:
            lines = f.readlines()

        functions = []
        current_func = []

        for line in lines:
            if re.match(r"^def\s", line) or re.match(r"^@api_view", line):
                if current_func:
                    functions.append(current_func)
                    current_func = []
            current_func.append(line)

        if current_func:
            functions.append(current_func)

        functions.sort(key=lambda f: f[0].strip())

        with open(output_path, "w") as f:
            for func in functions:
                f.writelines(func)
                f.write("\n")

        self.stdout.write(
            self.style.SUCCESS(f"✅ Sorted view functions written to {output_path}")
        )
