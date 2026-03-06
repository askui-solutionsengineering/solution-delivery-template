from askui.models.shared.tools import Tool
from typing import Optional

class GreetingTool(Tool):
    """Creates personalized greeting messages with time-based customization."""

    def __init__(self):
        super().__init__(
            name="greeting_tool",
            description="Creates a personalized greeting message based on time of day and user preferences",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the person to greet",
                        "minLength": 1
                    },
                    "time_of_day": {
                        "type": "string",
                        "description": "Time of day: morning, afternoon, or evening",
                        "enum": ["morning", "afternoon", "evening"]
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for the greeting (optional). Default is english.",
                        "enum": ["english", "spanish", "french"],
                        "default": "english"
                    }
                },
                "required": ["name", "time_of_day"]
            }
        )

    def __call__(self, name: str, time_of_day: str, language: Optional[str] = "english") -> str:
            if not name or not name.strip():
                raise ValueError("Name cannot be empty")

            if time_of_day not in ["morning", "afternoon", "evening"]:
                raise ValueError(f"Time of day must be 'morning', 'afternoon', or 'evening', got '{time_of_day}'")

            greetings = {
                "english": {
                    "morning": "Good morning",
                    "afternoon": "Good afternoon",
                    "evening": "Good evening"
                },
                "spanish": {
                    "morning": "Buenos días",
                    "afternoon": "Buenas tardes",
                    "evening": "Buenas noches"
                },
                "french": {
                    "morning": "Bonjour",
                    "afternoon": "Bon après-midi",
                    "evening": "Bonsoir"
                }
            }

            base_greeting = greetings.get(language, greetings["english"])[time_of_day]
            return f"{base_greeting}, {name}! How are you today?"
