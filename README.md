# DeepSeek MLX Local Server

Run DeepSeek R1 distilled models locally on Apple Silicon using [MLX](https://github.com/ml-explore/mlx) and serve them via an OpenAI-compatible API — ready to use with [Continue](https://continue.dev/) or any client that speaks the OpenAI protocol.

## Available Models

| # | Model | Size |
|---|-------|------|
| 1 | DeepSeek-R1-Distill-Qwen-32B 4-bit | ~20 GB |
| 2 | DeepSeek-R1-Distill-Qwen-14B 8-bit | ~16 GB |

You can install one or both models. The installer tracks installed models in `models.json` so they can coexist.

## Quick Start

```bash
# Install a model (you'll be prompted to choose)
python install.py

# Start the server
python run_server.py

# Clean up everything (venv, models, generated files)
python install.py --clean
```

## What `install.py` Does

1. **Creates a virtual environment** at `deepseek-mlx-env/.venv` with `mlx-lm` and its dependencies.
2. **Prompts you to choose a model**, then downloads it from Hugging Face via `huggingface_hub`.
3. **Generates project files:**
   - `run_server.py` — launcher for the MLX inference server.
   - `example_config.yaml` — a ready-made [Continue](https://continue.dev/) configuration pointing at the local server.
   - `models.json` — registry of installed models (supports multiple).
4. **Optionally sets up Continue** by writing (or overwriting) `~/.continue/config.yaml` with the example config.

Run `install.py` again to add a second model — existing models are preserved.

## What `run_server.py` Does

Starts an OpenAI-compatible HTTP server powered by `mlx_lm`:

```
POST http://localhost:8080/v1/chat/completions
POST http://localhost:8080/v1/completions
```

If multiple models are installed it will ask which one to start. Use `--port` to override the default port:

```bash
python run_server.py --port 9000
```

## Continue Integration

After installation, `example_config.yaml` contains a config block you can use directly with [Continue](https://continue.dev/). The installer can also write it to `~/.continue/config.yaml` for you.

The config registers the model for **chat**, **edit**, **apply**, and **autocomplete** roles — no API key required.

## Requirements

- **macOS** on Apple Silicon (M1/M2/M3/M4)
- **Python 3.10+**
