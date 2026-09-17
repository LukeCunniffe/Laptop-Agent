from groq import Groq
from groq.types.chat import ChatCompletionMessageParam
from groq.types.chat.chat_completion_tool_param import ChatCompletionToolParam

from agent.prompts import SYSTEM_PROMPT
from tools.system_tools import get_system_info, get_disk_usage
from tools.project_tools import (
        list_projects, 
        open_project,
        get_project_files,
        read_project_file,
        get_recent_project_files,
        )

from tools.application_tools import launch_application
from tools.git_tools import get_git_status, get_recent_commits
from typing import cast

import json

class LaptopAgent:

    def __init__(self):
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

            ]
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
