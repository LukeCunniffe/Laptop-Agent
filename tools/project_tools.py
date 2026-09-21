from pathlib import Path
import subprocess
import difflib
import uuid
from datetime import datetime

PROJECTS_DIRECTORY = Path.home() / "projects"

PENDING_EDITS: dict[str, dict] = {}

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

def get_recent_project_files(
        project_name: str,
        count: int = 5
        ) -> dict:
    """Return the most recently modified files in a project"""

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

            if not item.is_file():
                continue

            relative = item.relative_to(project)

            if any(part.startswith(".") for part in relative.parts):
                continue

            if "__pycache__" in relative.parts:
                continue

            files.append(
                    {
                        "file": str(relative),
                        "modified": item.stat().st_mtime,
                        }
                    )

            files.sort(
                    key=lambda item: item["modified"],
                    reverse=True
                    )

            recent = []

            for item in files[:count]:

                recent.append(
                        {
                            "file": item["file"],
                            "modified": datetime.fromtimestamp(
                                item["modified"]
                                ).isoformat(timespec="seconds"),
                            }
                        )

                return {
                        "success": True,
                        "project": project.name,
                        "recent_files": recent,
                        }

    return {
            "success": False,
            "message": f"Could not find project '{project_name}'."
            }

def search_project(
        project_name: str,
        query:str,
        max_results: int = 20
        ) -> dict:
    """Search text/source files inside a project for a string"""

    requested_name = (
            project_name
            .lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
            )

    max_results = min(max(max_results, 1), 20)

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

        matches = []

        allowed_extensions = {
                ".py",
                ".cs",
                ".java",
                ".c",
                ".h",
                ".cpp",
                ".hpp",
                ".rs",
                ".js",
                ".ts",
                ".html",
                ".css",
                ".json",
                ".toml",
                ".yaml",
                ".yml",
                ".md",
                ".txt",
                }

        for item in project.rglob("*"):

            if not item.is_file():
                continue

            relative = item.relative_to(project)

            # Ignore hidden folders/files and caches
            if any(part.startswith(".") for part in relative.parts):
                continue

            if "__pycache__" in relative.parts:
                continue

            if item.suffix.lower() not in allowed_extensions:
                continue

            # Avoid accidentally reading enormous files
            try:
                if item.stat().st_size > 500_000:
                    continue
            except OSError:
                continue

            try:
                lines = item.read_text(
                        encoding="utf-8",
                        errors="replace"
                        ).splitlines()

            except Exception:
                continue

            for line_number, line in enumerate(lines, start=1):

                if query.lower() in line.lower():

                    matches.append(
                            {
                                "file": str(relative),
                                "line": line_number,
                                "text": line.strip()[:300],
                                }
                            )

                    if len(matches) >= max_results:
                        return {
                                "success": True,
                                "project": project.name,
                                "query": query,
                                "matches": matches,
                                "truncated": True,
                                }
        return {
                "success": True,
                "project": project.name,
                "query": query,
                "matches": matches,
                "truncated": False,
                }

    return {
            "success": False,
            "message": f"Could not find project '{project_name}'."
            }

def create_project_file(
        project_name: str,
        file_path: str,
        content: str,
        ) -> dict:
    """Create a new file inside an existing project"""

    normalised_name = (
            project_name
            .lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
            )

    for project in PROJECTS_DIRECTORY.iterdir():

        if not project.is_dir():
            continue

        project_normalised = (
                project_name
                .lower()
                .replace("_", "")
                .replace("-", "")
                .replace(" ", "")
                )

        if project_normalised != normalised_name:
            continue

        project_root = project.resolve()

        target = (
                project_root / file_path
                ).resolve()

        # Prevent writing outside the project
        if project_root not in target.parents:
            return {
                    "success": False,
                    "message": (
                        "File path must remain inside "
                        "the selected project."
                        ),
                    }

        # Never overwrite files wiht this tool
        if target.exists():
            return {
                    "success": False,
                    "message": (
                        f"File already exists: "
                        f"{target.relative_to(project_root)}"
                        ),
                    }

        # Create parent folder<s if necessary.
        target.parent.mkdir(
                parents=True,
                exist_ok=True,
                )

        target.write_text(
                content,
                encoding="utf-8",
                )

        return {
                "success": True,
                "project": project.name,
                "file": str(
                    target.relative_to(project_root)
                    ),
                "message": "File created successfully.",
                }
    return {
            "success": False,
            "message": (
                f"Project '{project_name}' was not found."
                ),
            }

def propose_project_file_update(
        project_name: str,
        file_path: str,
        old_text: str,
        new_text: str,
        ) -> dict:
    """Prepare an edit without modifying the file"""

    normalised_name = (
            project_name
            .lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
            )

    for project in PROJECTS_DIRECTORY.iterdir():

        if not project.is_dir():
            continue

        project_normalised = (
                project.name
                .lower()
                .replace("_", "")
                .replace("-", "")
                .replace(" ", "")
                )

        if project_normalised != normalised_name:
            continue

        project_root = project.resolve()

        target = (
                project_root / file_path
                ).resolve()

        if project_root not in target.parents:
            return {
                    "success": False,
                    "message": (
                        "File path must remain inside "
                        "the selected project."
                        ),
                    }

        if not target.exists():
            return {
                    "success": False,
                    "message": "File does not exist.",
                    }

        if not target.is_file():
            return {
                    "success": False,
                    "message": "Target is not a file.",
                    }

        if not old_text:
            return {
                    "success": False,
                    "message": "Old text cannot be empty.",
                    }

        current_content = target.read_text(
                encoding="utf-8",
                errors="replace",
                )

        match_count = current_content.count(
                old_text
                )

        if match_count == 0:
            return {
                    "success": False,
                    "message": (
                        "The requested text was not found "
                        "in the new file."
                        ),
                    }
        if match_count > 1:
            return {
                    "success": False,
                    "message": (
                        "The requested text occurs more "
                        "than once. A more specific edit "
                        "is required."
                        ),
                    }

        updated_content = current_content.replace(
                old_text,
                new_text,
                1,
                )

        diff = "".join(
                difflib.unified_diff(
                    current_content.splitlines(
                        keepends=True
                        ),
                    updated_content.splitlines(
                        keepends=True
                        ),
                    fromfile=file_path,
                    tofile=file_path,
                    )
                )

        edit_id = str(uuid.uuid4())

        PENDING_EDITS[edit_id] = {
                "project": project.name,
                "file_path": file_path,
                "target": target,
                "original_content": current_content,
                "updated_content": updated_content,
                }

        return {
                "success": True,
                "edit_id": edit_id,
                "project": project.name,
                "file": file_path,
                "diff": diff,
                "message": (
                    "Edit prepared but not applied."
                    ),
                }

    return {
            "success": False,
            "message": (
                f"Project '{project_name}' was not found."
                )
            }

def apply_project_file_update(
        edit_id: str,
        ) -> dict:
    """Apply a previously proposed project edit."""
    pending_edit = PENDING_EDITS.get(
            edit_id
            )
    
    if pending_edit is None:
        return {
                "success": False,
                "message": (
                    "Pending edit was not found."
                    ),
                }

    target = pending_edit["target"]

    if not target.exists():
        return {
                "success": False,
                "message": (
                "The target file no longer exists."
                ),
                }

    current_content = target.read_text(
            encoding="utf-8",
            errors="replace",
            )

    # Important safety check:
    # Don't apply if something changed since
    # the proposal was generated.
    if current_content != pending_edit[
        "original_content"
        ]:

        return {
                "success": False,
                "message": (
                    "The file has changed since this "
                    "edit was proposed. Generate a new "
                    "proposal before applying it."
                    ),
                }

    target.write_text(
            pending_edit["updated_content"],
            encoding="utf-8",
            )

    del PENDING_EDITS[edit_id]

    return {
        "success": True,
        "project": pending_edit["project"],
        "file": pending_edit["file_path"],
        "message": (
            "The approved edit was applied."
        ),
    }

