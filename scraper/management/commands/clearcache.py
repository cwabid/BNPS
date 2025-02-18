import os
import shutil
from django.core.management.base import BaseCommand
from django.core.cache import cache

class Command(BaseCommand):
    help = "Clears Django cache and deletes all __pycache__ directories"

    def handle(self, *args, **kwargs):
        # Clearing Django cache
        self.stdout.write("🔄 Clearing Django cache...")
        cache.clear()
        self.stdout.write(self.style.SUCCESS("✅ Cache cleared successfully!"))

        # Deleting __pycache__ directories
        self.stdout.write("🗑 Deleting all __pycache__ directories...")
        project_dir = os.getcwd()
        deleted = 0

        for root, dirs, files in os.walk(project_dir):
            for dir_name in dirs:
                if dir_name == "__pycache__":
                    pycache_path = os.path.join(root, dir_name)
                    shutil.rmtree(pycache_path, ignore_errors=True)
                    deleted += 1
                    self.stdout.write(f"✅ Deleted: {pycache_path}")

        if deleted > 0:
            self.stdout.write(self.style.SUCCESS(f"✅ Removed {deleted} '__pycache__' directories."))
        else:
            self.stdout.write(self.style.WARNING("⚠ No '__pycache__' directories found."))

        self.stdout.write(self.style.SUCCESS("🎉 Cleanup completed!"))
