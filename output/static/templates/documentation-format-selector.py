#!/usr/bin/env python3
"""Choose a documentation format from the reader's immediate need."""

from __future__ import annotations

import argparse

FORMATS = {
    "learn": {
        "format": "Tutorial",
        "reader_state": "The reader is building capability and can follow a guided path.",
        "success": "They complete a working result and can adapt a nearby variation.",
        "include": "Starting state, ordered path, expected checkpoints, and one meaningful failure.",
    },
    "task": {
        "format": "How-to guide",
        "reader_state": "The reader knows the system and needs to change one known state.",
        "success": "They complete the specific task safely from the stated starting condition.",
        "include": "Prerequisites, focused procedure, success state, and recovery boundary.",
    },
    "lookup": {
        "format": "Reference",
        "reader_state": "The reader has a precise question and needs an exact answer quickly.",
        "success": "They find the name, type, default, constraint, or exception without inference.",
        "include": "Stable names, signatures, types, defaults, constraints, and examples where ambiguity remains.",
    },
    "understand": {
        "format": "Explanation",
        "reader_state": "The reader needs a mental model before they can make a sound decision.",
        "success": "They can explain the mechanism, tradeoff, and boundary in their own context.",
        "include": "Plain model, mechanism, example, tradeoff, and links to the task pages it informs.",
    },
}


def choose_format(need: str) -> dict[str, str]:
    """Return the documentation contract for a supported reader need."""
    return FORMATS[need]


def render(need: str) -> str:
    choice = choose_format(need)
    return "\n".join(
        [
            f"Format: {choice['format']}",
            f"Reader state: {choice['reader_state']}",
            f"Completion: {choice['success']}",
            f"Include: {choice['include']}",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Choose a documentation format from the reader's immediate need."
    )
    parser.add_argument("--need", choices=sorted(FORMATS), required=True)
    args = parser.parse_args()
    print(render(args.need))


if __name__ == "__main__":
    main()
