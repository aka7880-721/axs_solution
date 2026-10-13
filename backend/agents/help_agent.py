from agents.example_questions import flat_examples

HELP_ANSWER = (
    "This is the AXS Solutions live demo for Natural Language Analytics.\n\n"
    "It turns specific English questions into SQL, runs them on a sample business database, "
    "and summarizes the results.\n\n"
    "It knows about four tables: customers, employees, products, and sales. "
    "Ask about lists, filters, totals, counts, joins, or dates (this year, last year, quarters).\n\n"
    "Use the AXS website menu (Home, About, Solutions, Contact) or try an example question below."
)


def unsupported_hint() -> str:
    examples = flat_examples()[:14]
    return (
        "I did not recognize that question. This app uses fixed patterns, not open chat.\n\n"
        "Examples that work:\n"
        + "\n".join(f"  - {q}" for q in examples)
    )


def match_help_question(question: str) -> bool:
    q = question.lower().strip()
    if q in ("hi", "hello", "hey"):
        return True
    phrases = (
        "tell me about it",
        "tell me about this",
        "what is this",
        "what's this",
        "how does this work",
        "how do i use",
        "help me",
        "help",
        "what can you do",
        "what can i ask",
        "about this app",
        "about this system",
        "about the project",
        "explain this",
    )
    return any(p in q for p in phrases)
