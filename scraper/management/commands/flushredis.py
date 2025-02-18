import redis
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Flush all Redis data, clearing Celery tasks & cache."

    def handle(self, *args, **kwargs):
        redis_url = settings.CELERY_BROKER_URL  # Get Redis URL from settings
        if not redis_url.startswith("redis://"):
            self.stderr.write(self.style.ERROR("Invalid Redis configuration."))
            return
        
        # Extract Redis host & port
        redis_host = redis_url.split("//")[1].split(":")[0]
        redis_port = redis_url.split(":")[-1].split("/")[0]

        self.stdout.write(self.style.WARNING(f"Flushing Redis at {redis_host}:{redis_port}"))
        confirm = input("⚠ Are you sure? This will delete all data in Redis. (yes/no): ").strip().lower()
        if confirm != "yes":
            self.stdout.write(self.style.ERROR("Aborted. Redis was not flushed."))
            return

        try:
            client = redis.Redis(host=redis_host, port=int(redis_port), db=0)
            client.flushall()
            self.stdout.write(self.style.SUCCESS("✅ Redis has been flushed successfully!"))
        except redis.ConnectionError:
            self.stderr.write(self.style.ERROR("❌ Could not connect to Redis. Is it running?"))
