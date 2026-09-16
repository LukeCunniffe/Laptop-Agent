import shutil
import subprocess

APPLICATIONS = {
        "firefox": "firefox",
        "files": "nautilus",
        "terminal": "gnome-terminal",
        "nvim": ["gnome-terminal", "--", "nvim"],
        }

def launch_application(application: str) -> dict:
    """Launch an approved application on the laptop."""

    name = application.lower().strip()

    command = APPLICATIONS.get(name)

    if command is None:
        return {
                "success": False,
                "message": f"{application} is not in the approved application list."
                }
    executable = command[0]

    if shutil.which(executable) is None:
        return {
                "success": False,
                "message": f"{executable} is not installed or could not be found."
                }

    try:
        process = subprocess.Popen(
                command,
                start_new_session=True,
                )

    #subprocess.Popen(
            #[command],
            #stdout=subprocess.DEVNULL,
            #stderr=subprocess.DEVNULL,
            #)

        return {
                "success": True,
                "message": f"Opened {application}. Process ID: {process.pid}"
                }

    except Exception as error:
        return {
                "success": False,
                "message": f"Failed to open {application}: {error}"
                }

