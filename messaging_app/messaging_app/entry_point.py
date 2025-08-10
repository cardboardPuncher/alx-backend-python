#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    # Ensure Django knows which settings to use
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "messaging_app.settings")

    subprocess.run(["python3", "manage.py", "makemigrations"], check=True)

    # (Optional) Run migrations automatically
    subprocess.run(["python", "manage.py", "migrate"], check=True)

    # subprocess.run(["python", "manage.py", "collectstatic"])

    # Start the development server
    subprocess.run(["python", "manage.py", "runserver", "0.0.0.0:8000"])

if __name__ == "__main__":
    sys.exit(main())
