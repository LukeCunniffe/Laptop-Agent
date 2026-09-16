from pathlib import Path
import subprocess

PROJECTS_DIRECTORY = Path.home() / "projects"


def list_projects() -> list[str]:
    """Return folders contained in the user's Projects directory."""

    if not PROJECTS_DIRECTORY.exists():
        return []

    projects = []

    for item in PROJECTS_DIRECTORY.iterdir():
        if item.is_dir():
            projects.append(item.name)

    return sorted(projects)

def open_project(project_name: str) -> dict:
    """Find a project in ~/projects and open it in neovim."""

    if not PROJECTS_DIRECTORY.exists():
        return {
                "success": False,
                "message": "The projects directory does not exist."
                }

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
                project.name
                .lower()
                .replace("_", "")
                .replace("-", "")
                .replace(" ", "")
                )

        if actual_name == requested_name:

            try:
                process = subprocess.Popen(
                        [
                            "gnome-terminal",
                            "--",
                            "nvim",
                            str(project)
                            ],
                        start_new_session=True,
                        )

                return {
                        "success": True,
                        "project": project.name,
                        "path": str(project),
                        "message": f"Opened {project.name} in Neovim.",
                        "process_id": process.pid,
                        }

            except Exception as error:
                return {
                        "success": False,
                        "message": f"Failed to open project: {error}"
                        }

    return {
            "success": False,
            "message": f"Could not find a project matching '{project_name}'."
            }
