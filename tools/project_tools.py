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

def get_project_files(
        project_name: str,
        max_depth: int=3
        ) -> dict:
    """Return the file structure of a project."""

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

        if actual_name != requested_name:
            continue

        files = []

        for item in project.rglob("*"):

            relative = item.relative_to(project)

            # Ignore hidden/internal folders
            if any(
                    part.startswith(".")
                    for part in relative.parts
                    ):
                continue

            # Ignore Python cache folders
            if "__pycache__" in relative.parts:
                continue

            if len(relative.parts) > max_depth:
                continue

            if item.is_dir():
                files.append(f"{relative}/")
            else:
                files.append(str(relative))

        return {
                "success": True,
                "project": project.name,
                "path": str(project),
                "files": sorted(files),
                }

    return {
            "success": False,
            "message": f"Could not find project '{project_name}'."
            }

def read_project_file(
        project_name: str,
        file_path: str,
        max_characters: int = 4000
        ) -> dict:
    """Read a text file from inside an allowed project"""

    max_characters = min(max_characters, 4000)

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

        if actual_name != requested_name:
            continue

        target = (project / file_path).resolve()
        project_root = project.resolve()

        # Prevent the AI escaping the project directory
        if project_root not in target.parents:
            return {
                    "success": False,
                    "message": "Access outside the project directory is not allowed."
                    }

        if not target.exists():
            return {
                    "success": False,
                    "message": f"File '{file_path}' does not exist."
                    }

        if not target.is_file():
            return {
                    "success": False,
                    "message": f"'{file_path}' is not a file."
                    }

        try:
            content = target.read_text(
                    encoding="utf-8",
                    errors="replace"
                    )

            truncated = len(content) > max_characters

            return {
                    "success": True,
                    "project": project.name,
                    "file": str(target.relative_to(project)),
                    "content": content[:max_characters],
                    "truncated": truncated,
                    }
        except Exception as error:
            return {
                    "success": False,
                    "message": f"Could not read file: {error}"
                    }

    return {
            "success": False,
            "message": f"Could not find project '{project_name}'."
            }
