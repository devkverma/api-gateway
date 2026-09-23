import os
import subprocess

from dotenv import load_dotenv

load_dotenv()


def run():
    token = os.getenv("SONAR_TOKEN")

    if not token:
        raise RuntimeError("SONAR_TOKEN is not set")

    try:
        subprocess.run(
            [
                "pytest",
                "--cov=src",
                "--cov-report=term-missing",
                "--cov-report=xml",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        if e.returncode == 5:
            print("No tests found. Continuing with SonarQube analysis...")
        else:
            raise

    subprocess.run(
        [
            "pysonar",
            "--sonar-host-url=http://localhost:9000",
            f"--sonar-token={token}",
        ],
        check=True,
    )