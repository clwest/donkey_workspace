import json
import time
from django.core.management.base import BaseCommand
from django.test import Client

class Command(BaseCommand):
    help = "Benchmark heavy endpoints using the Django test client"

    def add_arguments(self, parser):
        parser.add_argument("--slug", default="prompt-pal")
        parser.add_argument("--session", default="demo-session")
        parser.add_argument("--samples", type=int, default=5)

    def handle(self, *args, **options):
        slug = options["slug"]
        session_id = options["session"]
        samples = options["samples"]

        client = Client()
        endpoints = [
            f"/api/assistants/{slug}/demo_replay/{session_id}/",
            f"/api/assistants/{slug}/reflections/",
            f"/api/assistants/{slug}/rag_debug/",
        ]
        results = {}
        for url in endpoints:
            times = []
            for _ in range(samples):
                start = time.time()
                client.get(url)
                times.append((time.time() - start) * 1000)
            times.sort()
            p50 = times[len(times) // 2]
            p95 = times[int(samples * 0.95) - 1] if samples > 1 else times[0]
            results[url] = {"p50_ms": round(p50, 2), "p95_ms": round(p95, 2)}
        with open("benchmark_results.json", "w") as fh:
            json.dump(results, fh, indent=2)
        self.stdout.write(self.style.SUCCESS("Benchmark complete"))
