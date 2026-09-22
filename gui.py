import threading
import tkinter as tk
from tkinter import scrolledtext

from dotenv import load_dotenv

from agent.agent import LaptopAgent
from voice_input import VoiceRecorder

load_dotenv()


class LaptopAgentGUI:

    def __init__(self, root: tk.Tk):
        self.root = root

        self.agent = LaptopAgent(
            status_callback=self.agent_status
        )

        self.voice_recorder = VoiceRecorder()
        self.is_recording = False

        self.root.title("Laptop Agent")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)


        # -------------------------
        # Bottom controls
        # -------------------------

        self.bottom_frame = tk.Frame(root)

        self.bottom_frame.pack(
            side=tk.BOTTOM,
            fill=tk.X,
            padx=15,
            pady=(5, 15),
        )


        # Message input
        self.entry = tk.Text(
            self.bottom_frame,
            height=4,
            wrap=tk.WORD,
            font=("Sans", 11),
            padx=8,
            pady=8,
        )

        self.entry.pack(
            fill=tk.X,
        )

        self.entry.bind(
            "<Control-Return>",
            self.send_message,
        )


        # Button row
        self.button_frame = tk.Frame(
            self.bottom_frame
        )

        self.button_frame.pack(
            fill=tk.X,
            pady=(8, 0),
        )


        self.send_hint = tk.Label(
            self.button_frame,
            text="Ctrl+Enter to send",
            anchor="w",
        )

        self.send_hint.pack(
            side=tk.LEFT,
        )


        self.send_button = tk.Button(
            self.button_frame,
            text="Send",
            command=self.send_message,
        )

        self.send_button.pack(
            side=tk.RIGHT,
        )


        self.mic_button = tk.Button(
            self.button_frame,
            text="Mic",
            command=self.toggle_voice_input,
        )

        self.mic_button.pack(
            side=tk.RIGHT,
            padx=(0, 8),
        )


        self.clear_button = tk.Button(
            self.button_frame,
            text="Clear",
            command=self.clear_chat,
        )

        self.clear_button.pack(
            side=tk.RIGHT,
            padx=(0, 8),
        )


        # Status bar
        self.status = tk.Label(
            self.bottom_frame,
            text="Ready",
            anchor="w",
            relief=tk.SUNKEN,
            bd=1,
            padx=8,
            pady=5,
        )

        self.status.pack(
            fill=tk.X,
            pady=(8, 0),
        )


        # -------------------------
        # Chat area
        # -------------------------

        self.chat = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Sans", 11),
            padx=10,
            pady=10,
        )

        self.chat.pack(
            fill=tk.BOTH,
            expand=True,
            padx=15,
            pady=(15, 5),
        )


        # Message styling
        self.chat.tag_configure(
            "user_name",
            justify="right",
            font=("Sans", 10, "bold"),
            spacing1=6,
        )

        self.chat.tag_configure(
            "user_message",
            justify="right",
            font=("Sans", 11),
            spacing3=12,
        )

        self.chat.tag_configure(
            "agent_name",
            justify="left",
            font=("Sans", 10, "bold"),
            spacing1=6,
        )

        self.chat.tag_configure(
            "agent_message",
            justify="left",
            font=("Sans", 11),
            spacing3=12,
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

                "Using tool: get_system_status":
                "Checking laptop status",

                "Using tool: get_network_status":
                "Checking network status...",

                "Using tool: get_process_status":
                "Checking running processes...",
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

        self.chat.config(
                state=tk.NORMAL
                )

        if sender == "You":
            self.chat.insert(
                    tk.END,
                    "You\n",
                    "user_name",
                    )

            self.chat.insert(
                    tk.END,
                    f"{message}\n\n",
                    "user_message",
                    )

        else:
            self.chat.insert(
                    tk.END,
                    f"{sender}\n",
                    "agent_name",
                    )

            self.chat.insert(
                    tk.END,
                    f"{message}\n\n",
                    "agent_message",
                    )

        self.chat.config(
                state=tk.DISABLED
                )

        self.chat.see(
                tk.END
                )

    def send_message(self, event=None) -> str | None:

        message = self.entry.get(
                "1.0",
                tk.END
                ).strip()

        if not message:
            return

        self.entry.delete(
                "1.0",
                tk.END
                )

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

        if event is not None:
            return "break"
        return None

    def toggle_voice_input(self) -> None:

        if not self.is_recording:
            self.start_voice_input()
        else:
            self.stop_voice_input()


    def start_voice_input(self) -> None:

        try:
            self.voice_recorder.start_recording()

            self.is_recording = True

            self.mic_button.config(
                    text="Stop"
                    )

            self.status.config(
                    text="Listening..."
                    )

        except Exception as error:
            self.status.config(
                    text=f"Voice error: {error}"
                    )


    def stop_voice_input(self) -> None:

        self.is_recording = False

        self.mic_button.config(
                text="Mic",
                state=tk.DISABLED,
                )

        self.status.config(
                text="Transcribing..."
                )

        thread = threading.Thread(
                target=self.run_transcription,
                daemon=True,
                )

        thread.start()

    def run_transcription(self) -> None:

        try:
            transcription = (
                    self.voice_recorder.stop_and_transcribe()
                    )

            self.root.after(
                    0,
                    self.finish_voice_input,
                    transcription,
                    None,
                    )

        except Exception as error:

            self.root.after(
                    0,
                    self.finish_voice_input,
                    "",
                    str(error),
                    )

    def finish_voice_input(
            self,
            transcription: str,
            error: str | None,
            ) -> None:

        self.mic_button.config(
                text="Mic",
                state=tk.NORMAL,
                )

        if error:
            self.status.config(
                    text=f"Voice error: {error}"
                    )
            return

        if not transcription:
            self.status.config(
                    text="No speech detected"
                    )
            return

        self.entry.delete(
                "1.0",
                tk.END
                )

        self.entry.insert(
                "1.0",
                transcription
                )

        self.status.config(
                text="Voice input ready"
                )
        self.entry.focus()

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

    def clear_chat(self) -> None:

        self.chat.config(
                state=tk.NORMAL
                )

        self.chat.delete(
                "1.0",
                tk.END
                )

        self.chat.config(
                state=tk.DISABLED
                )

        self.status.config(
                text="Chat cleared"
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
