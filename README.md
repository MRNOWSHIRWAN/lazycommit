# lazycommit

Stop writing commit messages. A small, open-weight model on your own machine
reads your staged diff and writes the message for you, in
[Conventional Commits](https://www.conventionalcommits.org/) style.

Your code never leaves your machine. No API key, no account, no subscription,
works offline. That is the whole point.

```console
$ git add -p
$ lazycommit
lazycommit: 1 staged file(s): portscan.py
lazycommit: asking qwen2.5-coder:0.5b-instruct at http://localhost:11434/v1 ...
feat: add timeout option to portscan

$ lazycommit --commit
lazycommit: committed as: feat: add timeout option to portscan
[master b8f5cf6] feat: add timeout option to portscan
```

## Why local

A commit message generator that sends your uncommitted code to a cloud API is
a strange idea: your staged diff is exactly the work you have not published
yet. lazycommit talks to a local server running an open-weight model
(default: [Qwen2.5-Coder 0.5B Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct),
about 400 MB, runs fine on a laptop CPU), so:

- **Private**: the diff stays on disk. No telemetry, no terms of service.
- **Free, forever**: set it up once, never pay per message.
- **Offline**: works on a plane, in a train, in a bunker.

## Setup

You need two things: the CLI, and any OpenAI-compatible local server.

**1. Install the CLI**

```console
$ pip install git+https://github.com/MRNOWSHIRWAN/lazycommit.git
```

**2. Run a model server** (pick one)

With [Ollama](https://ollama.com):

```console
$ ollama pull qwen2.5-coder:0.5b-instruct
$ ollama serve   # listens on http://localhost:11434/v1, the default
```

With [llama.cpp](https://github.com/ggml-org/llama.cpp):

```console
$ llama-server --model qwen2.5-coder-0.5b-instruct-q4_k_m.gguf --port 8080
$ export LAZYCOMMIT_BASE_URL=http://localhost:8080/v1
```

Any server that speaks the OpenAI chat completions API works. Bigger model =
better messages; set `LAZYCOMMIT_MODEL` to whatever you pulled.

## Usage

```console
$ lazycommit             # print a suggested message, change nothing
$ lazycommit --commit    # create the commit with the generated message
$ lazycommit --model qwen2.5-coder:1.5b-instruct
```

Configuration through environment variables:

| Variable              | Default                          | Meaning              |
| --------------------- | -------------------------------- | -------------------- |
| `LAZYCOMMIT_BASE_URL` | `http://localhost:11434/v1`      | model server URL     |
| `LAZYCOMMIT_MODEL`    | `qwen2.5-coder:0.5b-instruct`    | model name           |

## How it works

1. Reads `git diff --cached` (staged changes only).
2. Trims huge diffs so small models stay inside their context window,
   keeping every file name visible.
3. Asks the model for one Conventional Commit message, with three short
   examples (feat / docs / test) so even a 0.5B model picks the right type.
4. Cleans the output (strips quotes, fences, lead-ins) and either prints it
   or commits with it.

Honest limits: a 0.5B model is small. It gets the type and subject right far
more often than not, but read the message before you push. That is why the
default mode only prints.

## Development

Pure Python standard library, no runtime dependencies. Tests use pytest:

```console
$ python3 -m pytest tests/
15 passed
```

## License

MIT
