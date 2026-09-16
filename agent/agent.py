from groq import Groq
from groq.types.chat import ChatCompletionMessageParam
from groq.types.chat.chat_completion_tool_param import ChatCompletionToolParam

from agent.prompts import SYSTEM_PROMPT
from tools.system_tools import get_system_info, get_disk_usage
from tools.project_tools import list_projects
from tools.application_tools import launch_application

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
                        "description": "List the project folders inside the user's Projects directory.",
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
                        "description": "Launch an approved application on the user's ubuntu laptop.",
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
            ]

    def respond(self, message: str) -> str:

        self.messages.append(
                {
                    "role": "user",
                    "content": message
                    }
                )

        response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                )

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            self.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": [
                            {
                                "id": call.id,
                                "type": "function",
                                "function": {
                                    "name": call.function.name,
                                    "arguments": call.function.arguments,
                                    },
                                }
                            for call in assistant_message.tool_calls
                            ],
                        }
                    )


            for tool_call in assistant_message.tool_calls:

                tool_name = tool_call.function.name

                print(f"\n[Using tool: {tool_name}]")

                function = self.available_tools.get(tool_name)

                if function is None:
                    tool_result = "Tool not found."
                else:
                    arguments = json.loads(
                            tool_call.function.arguments or "{}"
                            )
                    tool_result = function(**arguments)

                self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result),
                            }
                        )

            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
            )

            reply = final_response.choices[0].message.content or ""

            self.messages.append(
                    {
                        "role": "assistant",
                        "content": reply,
                        }
                    )
            return reply

        reply = response.choices[0].message.content or ""

        self.messages.append(
                {
                    "role": "assistant",
                    "content": reply
                    }
                )

        return reply
