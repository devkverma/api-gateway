import os
import subprocess
from dotenv import load_dotenv

load_dotenv()


def run():
    token = os.getenv("SONAR_TOKEN")

    subprocess.run(
        [
            "pysonar",
            "--sonar-host-url=http://localhost:9000",
            f"--sonar-token={token}",
        ],
        check=True,
    )