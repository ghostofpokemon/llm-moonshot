# llm-moonshot
LLM plugin for Moonshot AI’s models

[![PyPI](https://img.shields.io/pypi/v/llm-moonshot.svg)](https://pypi.org/project/llm-moonshot/0.3.0/)
[![Changelog](https://img.shields.io/github/v/release/ghostofpokemon/llm-moonshot?include_prereleases&label=changelog)](https://github.com/ghostofpokemon/llm-moonshot/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ghostofpokemon/llm-moonshot/blob/main/LICENSE)

[LLM](https://llm.datasette.io/) plugin for models hosted by [Moonshot AI](https://platform.moonshot.ai/).

## Installation

First, [install the LLM command-line utility](https://llm.datasette.io/en/stable/setup.html).

Now install this plugin in the same environment as LLM:
```bash
llm install llm-moonshot
```

## Configuration

You’ll need an API key from Moonshot. Grab one at [platform.moonshot.cn](https://platform.moonshot.cn).

Set secret key:
```bash
llm keys set moonshot
```
```
Enter key: <paste key here>
```

## Usage

List what’s on the menu:
```bash
llm models list
```
You’ll see something like:
```
Moonshot: moonshot/kimi-latest
Moonshot: moonshot/moonshot-v1-auto
Moonshot: moonshot/moonshot-v1-128k-vision-preview
Moonshot: moonshot/kimi-k2-0711-preview
Moonshot: moonshot/moonshot-v1-128k
Moonshot: moonshot/moonshot-v1-32k-vision-preview
Moonshot: moonshot/moonshot-v1-8k-vision-preview
Moonshot: moonshot/moonshot-v1-8k
Moonshot: moonshot/kimi-thinking-preview
Moonshot: moonshot/moonshot-v1-32k
...
```

Fire up a chat:
```bash
llm chat -m moonshot/kimi-k2-0711-preview
```
```
Chatting with  moonshot/kimi-k2-0711-preview
Type 'exit' or 'quit' to exit
Type '!multi' to enter multiple lines, then '!end' to finish
> yo moonie
yo! what’s up, moonie?
>
```

Need raw completion?
```bash
llm -m moonshot/moonshot-v1-8k "Finish this haiku: Neon city rain"
```
```
Neon city rain,
Glistening streets, a symphony,
Echoes of the night.
```

## Reasoning Content Support

This plugin now supports **reasoning content** for Moonshot's thinking models (models with "thinking" in the name). When using thinking models, you'll see the model's reasoning process displayed in real-time before the final response:

```bash
llm chat -m moonshot/kimi-k2-thinking
```
```
[Reasoning] (shown in cyan dim)

The user is asking me to solve a complex problem. Let me think through this step by step...
First, I need to understand the core requirements...
Then I'll analyze the available options...

[Response] (shown in bold green)

Here's my well-reasoned answer to your question...
```

### Available Thinking Models
- `moonshot/kimi-k2-thinking` - Latest reasoning model
- `moonshot/kimi-thinking-preview` - Preview reasoning model

The reasoning content helps you understand:
- **Decision-making process** - See how the model analyzes problems
- **Multi-step reasoning** - Follow complex thought chains
- **Error detection** - Catch logical gaps or misunderstandings early

## Aliases

Save your wrists:
```bash
llm aliases set kimi moonshot/kimi-latest
```
Now:
```bash
llm -m kimi "write a haiku about the AI chatbot Sidney is misbehaving"
```

## Development

Clone, venv, deps—same dance:
```bash
git clone https://github.com/ghostofpokemon/llm-moonshot.git
cd llm-moonshot
python3 -m venv venv
source venv/bin/activate
pip install -e .
