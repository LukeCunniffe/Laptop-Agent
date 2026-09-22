from groq import Groq
from groq.types.chat import ChatCompletionMessageParam
from groq.types.chat.chat_completion_tool_param import ChatCompletionToolParam

from agent.prompts import SYSTEM_PROMPT
from tools.system_tools import (
        get_system_info, 
        get_disk_usage,
        get_system_status,
        get_network_status,
        get_process_status,
        )
from tools.project_tools import (
        list_projects, 
        open_project,
        get_project_files,
        read_project_file,
        get_recent_project_files,
        search_project,
        create_project_file,
        propose_project_file_update,
        apply_project_file_update,
        )

from tools.application_tools import launch_application
from tools.git_tools import get_git_status, get_recent_commits
from typing import cast

from tools.memory_tools import (
        remember_project_note,
        get_project_notes,
        complete_project_note,
        )

import json

class LaptopAgent:

    def __init__(self, status_callback=None):
        self.status_callback = status_callback

        self.client = Groq()
        self.model = "openai/gpt-oss-120b"
        

        self.messages: list[ChatCompletionMessageParam] = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                    }
                ]

        self.available_tools = {
                "get_system_info": get_system_info,
                "get_disk_usage": get_disk_usage,
                "list_projects": list_projects,
                "launch_application": launch_application,
                "open_project": open_project,
                "get_git_status": get_git_status,
                "get_recent_commits": get_recent_commits,
                "get_project_files": get_project_files,
                "read_project_file": read_project_file,
                "get_recent_project_files": get_recent_project_files,
                "search_project": search_project,
                "remember_project_note": remember_project_note,
                "get_project_notes": get_project_notes,
                "complete_project_note": complete_project_note,
                "create_project_file": create_project_file,
                "propose_project_file_update": propose_project_file_update,
                "apply_project_file_update": apply_project_file_update,
                "get_system_status": get_system_status,
                "get_network_status": get_network_status,
                "get_process_status": get_process_status,
                }

        self.tools: list[ChatCompletionToolParam] = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_system_info",
                        "description": "Get basic information about the user's laptop.",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            },
                        },
                    },
                {
                    "type": "function",
                    "function": {
                        "name": "get_disk_usage",
                        "description": "Get total, used, and free disk space on the user's laptop.",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            },
                        },
                    },
                {
                    "type": "function",
                    "function": {
                        "name": "list_projects",
                        "description": (
                            "List the names of projects inside ~/projects. Use only when "
                            "the user asks what projects exist or the project name is unknown."
                            ),
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            },
                        },
                    },
                {
                    "type": "function",
                    "function": {
                        "name": "launch_application",
                        "description": (
                            "Launch an approved application. ONLY use this when the user "
                            "explicitly asks to launch or open an application."
                            ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "application": {
                                    "type": "string",
                                    "decription": "The application to launch, such as firefox, files, terminal, or nvim."
                                    }
                                },
                            "required": ["application"],
                            },
                        },
                    },
                {
                        "type": "function",
                        "function": {
                            "name": "open_project",
                            "description": (
                                "Open a project in Neovim. ONLY use this when the user "
                                "explicitly asks to open a project."
                                ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "project_name": {
                                        "type": "string",
                                        "description": (
                                            "The name of the project to open, "
                                            "for example 'laptop agent'."
                                            ),
                                        }
                                    },
                                "required": ["project_name"],
                                },
                            },
                        },
                {
                        "type": "function",
                        "function": {
                            "name": "get_git_status",
                            "description": (
                                "Check the git status of a project inside the user's "
                                "~/projects directory and report modified, staged, "
                                "or untracked files."
                                ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "project_name": {
                                        "type": "string",
                                        "description": "The name of the project to inspect."
                                        }
                                    },
                                "required": ["project_name"],
                                },
                            },
                        },
                {
                        "type": "function",
                        "function": {
                            "name": "get_recent_commits",
                            "description": (
                                "Get the most recent Git commits for a project "
                                "inside the user's ~/projects directory."
                                ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "project_name": {
                                        "type": "string",
                                        "description": "The name of the project."
                                        },
                                    "count": {
                                        "type": "integer",
                                        "description": "How many recent commits to return."
                                        }
                                    },
                                "required": ["project_name"],
                                },
                            },
                        },
                {
                        "type": "function",
                        "function": {
                            "name": "get_project_files",
                            "description": (
                                "Return the file and folder structure of a project. Use when "
                                "the user asks about the project's structure, files, or folders. "
                                "Do not use it when an exact file path has already been supplied."
                                ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "project_name": {
                                        "type": "string",
                                        "description": "The name of the project to inspect."
                                        },
                                    "max_depth": {
                                        "type": "integer",
                                        "description": (
                                            "Maximum folder depth to inspect. "
                                            "Usually 2 or 3 is sufficient."
                                            )
                                        }
                                    },
                                "required": ["project_name"],
                                },
                            },
                        },
                {
                        "type": "function",
                        "function": {
                            "name": "read_project_file",
                            "description": (
                                "Read the contents of a specific text or source-code file "
                                "inside a project. Use this directly when the user provides "
                                "a project name and file path. After a successful read, answer "
                                "the user's question rather than calling unrelated tools."
                                ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "project_name": {
                                        "type": "string",
                                        "description": "The project conatining the file."
                                        },
                                    "file_path": {
                                        "type": "string",
                                        "description": (
                                            "Path to the file relative to the project root, "
                                            "for example 'agent/agent.py'."
                                            )
                                        },
                                    "max_characters": {
                                        "type": "integer",
                                        "description": "Maximum number of characters to read.",
                                        "maximum": 4000,
                                        }
                                    },
                                "required": ["project_name", "file_path"],
                                },
                            },
                        },
                {
                        "type": "function",
                        "function": {
                            "name": "get_recent_project_files",
                            "description": (
                                "Return the most recently modified files inside a project. "
                                "Use this when the user asks what they were recently working "
                                "on or requests a project catch-up."
                                ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "project_name": {
                                        "type": "string",
                                        "description": "The name of the project."
                                        },
                                    "count": {
                                        "type": "integer",
                                        "description": "Number of recent files to return.",
                                        "minimum": 1,
                                        "maximum": 10,
                                        }
                                    },
                                "required": ["project_name"],
                                },
                            },
                        },
                {
                        "type": "function",
                        "function": {
                            "name": "search_project",
                            "description": (
                                "Search source code and text files inside a project for "
                                "a word, function name, class name, setting, or other text. "
                                "Use this when the user asks where something is implemented "
                                "or when you need to locate a relevant file before reading it."
                                ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "project_name": {
                                        "type": "string",
                                        "description": "The name of the project."
                                        },
                                    "query": {
                                        "type": "string",
                                        "description": (
                                            "The text to search for, such as a function name, "
                                            "class name, variable, or keyword."
                                            )
                                        },
                                    "max_results": {
                                        "type": "integer",
                                        "description": "Maximum number of matches to return.",
                                        "minimum": 1,
                                        "maximum": 20,
                                        }
                                    },
                                "required": [
                                    "project_name",
                                    "query"
                                    ],
                                },
                            },
                        },
                {
                        "type": "function",
                        "function": {
                            "name": "remember_project_note",
                            "description": (
                                "Store a persistent note about a project. "
                                "Only use this when the user explicitly asks to remember, "
                                "save, record, or note something for later."
                                ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "project_name": {
                                        "type": "string",
                                        "description": "The relevant project name."
                                        },
                                    "note": {
                                        "type": "string",
                                        "description": "The information to remember."
                                        }
                                    },
                                "required": ["project_name", "note"],
                                },
                            },
                        },
                {
                        "type": "function",
                        "function": {
                            "name": "get_project_notes",
                            "description": (
                                "Retrieve persistent notes previously saved about a project. "
                                "Use this when the user asks what they planned to do, "
                                "what was remembered, or what they wanted to do next."
                                ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "project_name": {
                                        "type": "string",
                                        "description": "The project whose notes should be retrieved."
                                        },
                                    "limit": {
                                        "type": "integer",
                                        "description": "Maximum number of notes to return.",
                                        "minimum": 1,
                                        "maximum": 20,
                                        }
                                    },
                                "required": ["project_name"],
                                },
                            },
                        },

                {
                        "type": "function",
                        "function": {
                            "name": "create_project_file",
                            "description": (
                                "Create a new text file inside an existing project. "
                                "Only use this when the user explicitly asks to create "
                                "a new file. This tool cannot overwrite existing files."
                                ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "project_name": {
                                        "type": "string",
                                        "description": "The project containing the new file."
                                        },
                                    "file_path": {
                                        "type": "string",
                                        "description": (
                                            "The path of the new file relative to "
                                            "the project root."
                                            )
                                        },
                                    "content": {
                                        "type": "string",
                                        "description": "The complete contents of the new file."
                                        }
                                    },
                                "required": [
                                    "project_name",
                                    "file_path",
                                    "content",
                                    ],
                                },
                            },
                        },
                {
                    "type": "function",
                    "function": {
                        "name": "propose_project_file_update",
                        "description": (
                            "Prepare a proposed change to an existing project file "
                            "without modifying the file. Use this when the user asks "
                            "to change existing project code or text."
                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "project_name": {
                                    "type": "string",
                                    "description": "The project containing the file."
                                },
                                "file_path": {
                                    "type": "string",
                                    "description": (
                                        "The path to the file relative to "
                                        "the project root."
                                    )
                                },
                                "old_text": {
                                    "type": "string",
                                    "description": (
                                        "The exact existing text to replace."
                                    )
                                },
                                "new_text": {
                                    "type": "string",
                                    "description": (
                                        "The replacement text."
                                    )
                                }
                            },
                            "required": [
                                "project_name",
                                "file_path",
                                "old_text",
                                "new_text",
                            ],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "apply_project_file_update",
                        "description": (
                            "Apply a previously proposed project file edit. "
                            "Only use this after the user explicitly approves "
                            "the proposed change."
                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "edit_id": {
                                    "type": "string",
                                    "description": (
                                        "The edit ID returned by "
                                        "propose_project_file_update."
                                    )
                                }
                            },
                            "required": ["edit_id"],
                        },
                    },
                },
            {
                    "type": "function",
                    "function": {
                        "name": "get_system_status",
                        "description": (
                            "Get a current overview of the laptop including "
                            "CPU usage, memory usage, battery status, uptime, "
                            "and system load."
                            ),
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            },
                        },
                    },
            {
                    "type": "function",
                    "function": {
                        "name": "get_network_status",
                        "description": (
                            "Inspect the laptop's current network interfaces, "
                            "connection state, hostname, and IP addresses."
                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {},
                        },
                    },
                },
            {
                "type": "function",
                "function": {
                    "name": "get_process_status",
                    "description": (
                        "Inspect currently running processes. "
                        "Can search for a specific application or return "
                        "the processes using the most CPU or memory."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "process_name": {
                                "type": "string",
                                "description": (
                                    "Optional process or application name "
                                    "to search for."
                                ),
                            },
                            "limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 20,
                                "description": (
                                    "Maximum number of processes to return."
                                ),
                            },
                            "sort_by": {
                                "type": "string",
                                "enum": [
                                    "cpu",
                                    "memory",
                                ],
                                "description": (
                                    "Sort processes by CPU or memory usage."
                                ),
                            },
                        },
                    },
                },
            },
            ]
    def update_status(self, message: str) -> None:
        if self.status_callback:
            self.status_callback(message)

    def respond(self, message: str) -> str:

        self.messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

        max_iterations = 10

        for _ in range(max_iterations):

            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto",
            )

            assistant_message = response.choices[0].message

            # No tool request = final answer
            if not assistant_message.tool_calls:

                reply = assistant_message.content or ""

                self.messages.append(
                    {
                        "role": "assistant",
                        "content": reply,
                    }
                )

                return reply

            # Preserve the assistant's actual tool-call message
            self.messages.append(
                    cast(
                        ChatCompletionMessageParam,
                        assistant_message.model_dump(exclude_none=True)
                        )
                    )

            for tool_call in assistant_message.tool_calls:

                tool_name = tool_call.function.name

                print(f"\n[Using tool: {tool_name}]")

                self.update_status(
                        f"Using tool: {tool_name}"
                        )

                function = self.available_tools.get(tool_name)

                if function is None:

                    tool_result = {
                        "success": False,
                        "message": f"Tool '{tool_name}' was not found.",
                    }

                else:

                    try:
                        arguments = json.loads(
                            tool_call.function.arguments or "{}"
                        )

                        tool_result = function(**arguments)

                    except Exception as error:

                        tool_result = {
                            "success": False,
                            "message": f"Tool failed: {error}",
                        }

                self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result),
                        }
                    )

        return "I reached the maximum number of tool calls without completing the request."
