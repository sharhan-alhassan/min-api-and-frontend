INTENTS = {
    "greeting": {
        "keywords": ["hi", "hello", "hey"],
        "response": "Hello! How can I help you today?",
    },
    "help": {
        "keywords": ["help", "assist", "support"],
        "response": "Sure! Tell me what you need help with.",
    },
    "python": {
        "keywords": ["python", "code", "programming"],
        "response": "Python is a beginner-friendly programming language.",
    },
    "unknown": {
        "response": "I'm not sure I understand. Can you rephrase?",
    },
}

# Order matters: the first matching intent wins.
INTENT_ORDER = ["greeting", "help", "python", "unknown"]

