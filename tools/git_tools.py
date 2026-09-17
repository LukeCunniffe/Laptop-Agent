import subprocess
from pathlib import Path

PROJECTS_DIRECTORY = Path.home() / "projects"

def get_git_status(project_name: str) -> dict:
    """Return the Git status of a project."""

    requested_name = (
            project_name
            .lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
            )

    for project in PROJECTS_DIRECTORY.iterdir():

        if not project.is_dir():
            continue

        actual_name = (
                project_name
                .lower()
                .replace("_", "")
                .replace("-", "")
                .replace(" ", "")
                )

        if actual_name == requested_name:

            git_folder = project / ".git"

            if not git_folder.exists():
                return {
                        "success": False,
                        "message": f"{project.name} is not a Git repository."
                        }

            try:
                result = subprocess.run(
                        ["git", "status", "--short"],
                        cwd=project,
                        capture_output=True,
                        text=True,
                        check=True,
                        )

                status = result.stdout.strip()

                if not status:
                    status = "Working tree is clean."

                return {
                        "success": True,
                        "project": project.name,
                        "status": status,
                        }

            except subprocess.CalledProcessError as error:
                return {
                        "success": False,
                        "message": f"Git failed: {error}"
                        }

    return {
            "success": False,
            "message": f"Could not find project '{project_name}'."
            }

def get_recent_commits(project_name: str, count: int=5) -> dict:
    """Return the most recent Git commits for a project."""

    requested_name = (
            project_name
            .lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
            )

    for project in PROJECTS_DIRECTORY.iterdir():

        if not project.is_dir():
            continue

        actual_name = (
                project_name
                .lower()
                .replace("_", "")
                .replace("-", "")
                .replace(" ", "")
                )

        if actual_name == requested_name:

            if not (project / ".git").exists():
                return {
                        "success": False,
                        "message": f"{project.name} is not a Git repository."
                        }

            try:
                result = subprocess.run(
                        [
                            "git",
                            "log",
                            f"-{count}",
                            "--pretty=format:%h | %ad | %s",
                            "--date=short",
                            ],
                        cwd=project,
                        capture_output=True,
                        text=True,
                        check=True,
                        )

                return {
                        "success": True,
                        "project": project.name,
                        "commits": result.stdout.strip(),
                        }

            except subprocess.CalledProcessError as error:
                return {
                        "success": False,
                        "message": f"Git failed: {error}"
                        }

    return {
            "success": False,
            "message": f"Could not find project '{project_name}'."
            }
