import llm
from llm.default_plugins.openai_models import Chat
from llm.utils import remove_dict_none_values
from pathlib import Path
import json
import time
import httpx
from rich.console import Console
from rich.style import Style

def get_moonshot_models():
    return fetch_cached_json(
        url="https://api.moonshot.ai/v1/models",
        path=llm.user_dir() / "moonshot_models.json",
        cache_timeout=3600,
    ).get("data", [])

class MoonshotChat(Chat):
    needs_key = "moonshot"
    key_env_var = "MOONSHOT_KEY"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.reasoning_style = Style(
            color="cyan",
            dim=True,
            italic=True
        )

    def __str__(self):
        return f"Moonshot: {self.model_id}"

    def _display_reasoning_content(self, reasoning_content):
        """Display reasoning content with special formatting"""
        if reasoning_content and reasoning_content.strip():
            self.console.print("\n[Reasoning]\n\n", style=self.reasoning_style, end="")
            self.console.print(reasoning_content, style=self.reasoning_style)
            self.console.print("\n[Response]\n\n", style="bold green", end="")

    def execute(self, prompt, stream, response, conversation=None, **kwargs):
        client = self.get_client(key=key)
        messages = self.build_messages(prompt, conversation)
        kwargs = remove_dict_none_values(prompt.options.dict())

        # Check if this model supports reasoning_content
        supports_reasoning = "thinking" in self.model_name.lower()

        if stream:
            try:
                yield from self._stream_completion(client, messages, kwargs, supports_reasoning)
                return
            except httpx.HTTPError:
                # Some Moonshot endpoints occasionally drop the streaming connection.
                # Fall back to a non-streaming request so the user still gets a response.
                self.console.print("\n[connection dropped - retrying without streaming]\n", style="yellow")

        yield from self._non_stream_completion(client, messages, kwargs, response, supports_reasoning)

    def _stream_completion(self, client, messages, kwargs, supports_reasoning):
        completion_stream = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True,
            **kwargs,
        )
        reasoning_started = False

        for chunk in completion_stream:
            delta = chunk.choices[0].delta

            # Handle reasoning_content in streaming
            if supports_reasoning and hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                if not reasoning_started:
                    self.console.print("\n[Reasoning]\n\n", style=self.reasoning_style, end="")
                    reasoning_started = True
                self.console.print(delta.reasoning_content, style=self.reasoning_style, end="")

            # Handle regular content
            if delta.content:
                if reasoning_started:
                    self.console.print("\n[Response]\n\n", style="bold green", end="")
                    reasoning_started = False
                yield delta.content

    def _non_stream_completion(self, client, messages, kwargs, response, supports_reasoning):
        completion = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=False,
            **kwargs,
        )
        response.response_json = completion.model_dump()
        if completion.usage:
            self.set_usage(response, completion.usage.model_dump())

        message = completion.choices[0].message

        # Handle reasoning_content in non-streaming
        if supports_reasoning and hasattr(message, 'reasoning_content') and message.reasoning_content:
            self._display_reasoning_content(message.reasoning_content)

        # Handle regular content
        content = message.content
        if content:
            yield content

@llm.hookimpl
def register_models(register):
    key = llm.get_key("", "moonshot", "MOONSHOT_KEY")
    if not key:
        return

    models = get_moonshot_models()
    for model_def in models:
        register(
            MoonshotChat(
                model_id=f"moonshot/{model_def['id']}",
                model_name=model_def["id"],
                api_base="https://api.moonshot.ai/v1/",
            )
        )

def fetch_cached_json(url, path, cache_timeout):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.is_file() and (time.time() - path.stat().st_mtime) < cache_timeout:
        with open(path, "r") as f:
            return json.load(f)

    key = llm.get_key("", "moonshot", "MOONSHOT_KEY")
    if not key:
        return {"data": []}

    headers = {"Authorization": f"Bearer {key}"}

    try:
        response = httpx.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()
        data = response.json()
        with open(path, "w") as f:
            json.dump(data, f)
        return data
    except httpx.HTTPError:
        if path.is_file():
            with open(path, "r") as f:
                return json.load(f)
        raise
