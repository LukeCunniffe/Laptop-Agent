import threading
import tkinter as tk
from tkinter import scrolledtext

from dotenv import load_dotenv

from agent.agent import LaptopAgent


load_dotenv()


class LaptopAgentGUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.agent = LaptopAgent(
                status_callback=self.agent_status
                )

        self.root.title("Laptop Agent")
        self.root.geometry("800x600")

        self.chat = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.chat.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=(10, 5),
        )

        self.input_frame = tk.Frame(root)
        self.input_frame.pack(
            fill=tk.X,
            padx=10,
            pady=(5, 5),
        )

        self.entry = tk.Entry(
            self.input_frame,
            font=("Sans", 12),
        )
        self.entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
        )

        self.entry.bind(
            "<Return>",
            self.send_message,
        )

        self.send_button = tk.Button(
            self.input_frame,
            text="Send",
            command=self.send_message,
        )
        self.send_button.pack(
            side=tk.RIGHT,
            padx=(10, 0),
        )

        self.status = tk.Label(
            root,
            text="Ready",
            anchor="w",
        )
        self.status.pack(
            fill=tk.X,
            padx=10,
            pady=(0, 10),
        )

        self.add_message(
            "Agent",
            "Laptop Agent v0.2 ready."
        )

        self.entry.focus()

    def agent_status(self, message: str) -> None:
        status_messages = {
                "Using tool: get_system_info":
                "Checking system information...",

                "Using tool: get_disk_usage":
                "Checking storage...",

                "Using tool: list_projects":
                "Looking through your projects...",

                "Using tool: get_project_files":
                "Inspecting project files...",

                "Using tool: read_project_file":
                "Reading project file...",

                "Using tool: get_recent_project_files":
                "Checking recently modified files...",

                "Using tool: search_project":
                "Searching project code...",

                "Using tool: get_git_status":
                "Checking Git status...",

                "Using tool: get_recent_commits":
                "Checking recent commits...",

                "Using tool: get_project_notes":
                "Checking project memory...",

                "Using tool: remember_project_note":
                "Saving that to memory...",

                "Using tool: complete_project_note":
                "Updating project memory...",

                "Using tool: launch_application":
                "Launching application...",

                "Using tool: open_project":
                "Opening project...",
                }
        display_message = status_messages.get(
                message,
                message
                )
        self.root.after(
                0,
                lambda: self.status.config(
                text=display_message
                )
                )

    def add_message(
        self,
        sender: str,
        message: str
    ) -> None:

        self.chat.config(state=tk.NORMAL)

        self.chat.insert(
            tk.END,
            f"{sender} > {message}\n\n"
        )

        self.chat.config(state=tk.DISABLED)
        self.chat.see(tk.END)

    def send_message(self, event=None) -> None:

        message = self.entry.get().strip()

        if not message:
            return

        self.entry.delete(0, tk.END)

        self.add_message(
            "You",
            message
        )

        self.entry.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)

        self.status.config(
            text="Agent is thinking..."
        )

        thread = threading.Thread(
            target=self.run_agent,
            args=(message,),
            daemon=True,
        )

        thread.start()

    def run_agent(self, message: str) -> None:

        try:
            response = self.agent.respond(message)

        except Exception as error:
            response = f"Error: {error}"

        self.root.after(
            0,
            self.finish_response,
            response,
        )

    def finish_response(
        self,
        response: str
    ) -> None:

        self.add_message(
            "Agent",
            response
        )

        self.entry.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)

        self.status.config(
            text="Ready"
        )

        self.entry.focus()


def main() -> None:

    root = tk.Tk()

    LaptopAgentGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()
