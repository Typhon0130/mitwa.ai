from functools import lru_cache

from langchain.concise.decide import decide, select, chunk, generate
from langchain.chat_models import SystemMessage, UserMessage
from langchain.chat_models.base import BaseMessage
from langchain.prompts.base import StringPromptValue
from langchain.output_parsers import (
    ListOutputParser,
    MultiAttemptRetryWithErrorOutputParser,
    ParsedItemListOutputParser,
    PydanticOutputParser,
)

from mitwa.utils import BulletListOutputParser
from mitwa.cli import cliapp
from mitwa.web import webapp


@cliapp.command()
@webapp.get("/api/v1/chose_next_speaker")
def chose_next_speaker(candidates: list[str], messages: list[str]) -> str | None:

    print(f"Candidates: {candidates}")

    # Ask each candidate if they want to speak next and rate their desire to speak
    candidate_responses = [
        get_response(
            candidate,
            [
                *messages,
                "Do you want to speak next in this dialogue? If yes, provide a rate your desire to speak from 0 (no desire) to 10 (you can't hold back any more) and justify your rating.",
            ],
        )
        for candidate in candidates
    ]
    print(f"Candidate responses: {candidate_responses}")

    # Let the AI select the next speaker from the candidates based on their responses
    response = select(
        "\n\n".join(
            f"{candidate}: {candidate_response}"
            for candidate, candidate_response in zip(candidates, candidate_responses)
        )
        + "\n\nSelect `Nobody` if you want to end the conversation.",
        query="Choose the most qualified one to speak next:",
        options=[*[candidate.split(":")[0] for candidate in candidates], "Nobody"],
    )
    print(f"Omniscent select response: {response}")
    next_speaker = None
    if "nobody" in response.lower():
        next_speaker = None
    else:
        next_speaker = response
    print(f"Next speaker: {next_speaker}")
    return next_speaker


@cliapp.command()
@webapp.get("/api/v1/get_response")
def get_response(ego: str, messages: list[str]) -> str:
    # Ask the ego to respond to the conversation
    response = generate(
        [
            SystemMessage(content=ego),
            *[UserMessage(content=messages) for messages in messages],
        ]
    ).content
    print(f"Response: {response}")
    return response


@cliapp.command()
@webapp.get("/api/v1/converse")
def converse(egos: list[str], messages: list[str] = [], limit=None) -> list[str]:

    # Loop until no speaker is chosen
    for _ in range(limit) if limit is not None else range(10_000):
        speaker = chose_next_speaker(egos, messages)
        if speaker is None:
            break
        # Have the chosen speaker respond to the conversation
        response = get_response(speaker, messages)
        # Add the response to the conversation object
        messages.append(response)

    print(f"Final conversation: {messages}")
    return messages


# Define a parser for extracting egos from text
egos_parser = MultiAttemptRetryWithErrorOutputParser(parser=BulletListOutputParser())


@cliapp.command()
@webapp.get("/api/v1/extract_ego_from_description")
def new_ego_from_description(description: str) -> str:
    new_ego = generate(
        [
            SystemMessage(
                content=f"Extract an egos that captures the personality expressed in the following content. The ego should have a name and a paragraph-length dossier. You pick and use a unique voice / writing style / etc. for the ego's paragraph. Really try to capture the egos in writing. The dossier paragraph should provide enough information to simulate the ego in a AI-driven psychodynamic simulacra. Answer in a single paragraph. Your answer should be formatted: <name>: <dossier>."
            ),
            UserMessage(content=description),
        ]
    ).content
    print(f"New ego: {new_ego}")
    return new_ego


@cliapp.command()
@webapp.get("/api/v1/grow_egos")
def grow_egos(content: str, egos: list[str] = []) -> list[str]:
    print(f"Initial egos: {egos}")
    content_type = _determine_content_type(content)
    # Chunk the content into smaller pieces
    for chk in chunk(content):
        # Have the user extract or modify egos from the chunk of content
        new_egos = generate(
            [
                SystemMessage(
                    content=f"Extract distinct egos or modify existing ones that capture my personality as expressed in my {content_type}. Give each of my egos a name and a paragraph-length dossier. You should use a unique voice / writing style / etc. for each ego's paragraph. Really try to capture the variety of egos in my inner psychosocial realm. The dossier paragraph should provide enough information to simulate the ego in a AI-driven psychodynamic simulacra. Answer in a bulleted list of paragraphs. Your answers should be formatted like\n\n- <name>: <dossier>\n<name>: <dossier>\n<name>: <dossier>\n\netc."
                ),
                UserMessage(content="Here is the {content_type}:"),
                UserMessage(content=chk),
                UserMessage(content="Here are the egos I have so far:"),
                UserMessage(
                    content="\n".join(f"{ego.name}: {ego.description}" for ego in egos)
                ),
                UserMessage(
                    content="Now, please rewrite the egos list with any new egos you have identified or modifications to existing egos. If you have no changes, just copy and paste the list."
                ),
            ],
            parser=egos_parser,
        )
        print(f"Updated egos: {new_egos}")
        egos = new_egos
    print(f"Final egos: {egos}")
    return egos


@cliapp.command()
@webapp.get("/api/v1/extract_insights_from_conversations")
def extract_insights_from_conversations(
    egos: list[str],
    messages: list[str] = [],
    name: str = "someone",
    pronoun: str = "them",
    reflexive_pronoun: str = "themself",
) -> str:
    response = generate(
        [
            SystemMessage(
                content=f"You are therapistGPT. You are examining {name}'s thoughts to help {pronoun} understand {reflexive_pronoun} better. Please identify internal conflicts, dissonence, areas for growth, areas for commendation, and other analyses from {name}'s diary. Your response should be in the form of {name}'s own stream of consciousness, using {pronoun} style of writing and voice, and first person (using \"I\"): "
            ),
            *[UserMessage(content=message) for message in messages],
            UserMessage(content="Now, please write your 1st person reflections:"),
        ],
    ).content
    print(response)
    return response


@lru_cache(maxsize=100)
def _determine_content_type(content: str) -> str:
    # Ask what type of content it is
    return generate(
        "What type of content is this? Eg, diary, essay, message, etc. One word answer: "
        + (content if len(content) < 1000 else content[:1000]),
    ).split()[0]
