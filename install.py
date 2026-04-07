#!/usr/bin/env python3
"""
Script to set up a Python environment with mlx-lm and
download the DeepSeek-R1-Distill-Qwen-32B-MLX model.

Usage:
    python install.py            # Install everything
The    python install.py --clean    # Remove all generated files
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
PROJECT_DIR = SCRIPT_PATH.parent
ENV_DIR = PROJECT_DIR / "deepseek-mlx-env"
VENV_DIR = ENV_DIR / ".venv"
MODELS = {
    "1": {
        "label": "DeepSeek-R1-Distill-Qwen-32B 4-bit (~20 GB)",
        "id": "mlx-community/DeepSeek-R1-Distill-Qwen-32B-MLX",
        "variant": "DeepSeek-R1-Distill-Qwen-32B-4bit",
        "name": "DeepSeek-R1-32B-MLX",
    },
    "2": {
        "label": "DeepSeek-R1-Distill-Qwen-14B 8-bit (~16 GB)",
        "id": "mlx-community/DeepSeek-R1-Distill-Qwen-14B-MLX",
        "variant": "DeepSeek-R1-Distill-Qwen-14B-8bit",
        "name": "DeepSeek-R1-14B-MLX",
    },
}

EXAMPLE_CONFIG = PROJECT_DIR / "example_config.yaml"
RUN_SERVER = PROJECT_DIR / "run_server.py"
MODELS_JSON = PROJECT_DIR / "models.json"
README = PROJECT_DIR / "README.md"
CONTINUE_DIR = Path.home() / ".continue"
CONTINUE_CONFIG = CONTINUE_DIR / "config.yaml"

DEFAULT_PORT = 8080

CONFIG_YAML = """\
name: {model_name}
version: 1.0.0
schema: v1
models:
  - name: {model_name} (local)
    provider: openai
    model: {model_path}
    apiBase: http://localhost:{port}/v1
    apiKey: not-needed
    requestOptions:
      timeout: 0
    roles:
      - chat
      - edit
      - apply
  - name: {model_name} autocomplete
    provider: openai
    model: {model_path}
    apiBase: http://localhost:{port}/v1
    apiKey: not-needed
    requestOptions:
      timeout: 0
    roles:
      - autocomplete
"""

RUN_SERVER_PY = '''\
#!/usr/bin/env python3
"""
Start the mlx_lm OpenAI-compatible server.

Usage:
    python run_server.py                  # Start on default port {port}
    python run_server.py --port 9000      # Start on custom port
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

VENV_DIR = Path(__file__).parent / "deepseek-mlx-env" / ".venv"
MODELS_JSON = Path(__file__).parent / "models.json"
EXAMPLE_CONFIG = Path(__file__).parent / "example_config.yaml"
DEFAULT_PORT = {port}


def port_from_config():
    """Extract the port from apiBase in example_config.yaml, if present."""
    if EXAMPLE_CONFIG.exists():
        match = re.search(r"apiBase:\\s*https?://[^:/]+:(\\d+)", EXAMPLE_CONFIG.read_text())
        if match:
            return int(match.group(1))
    return DEFAULT_PORT


def discover_models():
    """Return a list of (name, path) for models that exist on disk."""
    if not MODELS_JSON.exists():
        print("Error: models.json not found. Run install.py first.", file=sys.stderr)
        sys.exit(1)
    with open(MODELS_JSON) as f:
        all_models = json.load(f)
    available = [(m["name"], m["path"]) for m in all_models if Path(m["path"]).exists()]
    if not available:
        print("Error: No installed models found on disk.", file=sys.stderr)
        print("Run install.py to download a model.", file=sys.stderr)
        sys.exit(1)
    return available


def choose_model(models):
    """If multiple models are available, prompt the user to choose one."""
    if len(models) == 1:
        return models[0]
    print("\\nMultiple models found:\\n")
    for i, (name, path) in enumerate(models, 1):
        print(f"  {{i}}) {{name}}")
        print(f"     {{path}}")
    while True:
        choice = input(f"\\nWhich model to start? [1-{{len(models)}}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(models):
            return models[int(choice) - 1]
        print("Invalid choice.")


def main():
    config_port = port_from_config()
    parser = argparse.ArgumentParser(description="Start the mlx_lm server")
    parser.add_argument("--port", type=int, default=config_port,
                        help=f"Port to listen on (default: {{config_port}})")
    args = parser.parse_args()

    if sys.platform == "win32":
        python = VENV_DIR / "Scripts" / "python"
    else:
        python = VENV_DIR / "bin" / "python"

    if not python.exists():
        print(f"Error: Virtual environment not found at {{VENV_DIR}}", file=sys.stderr)
        print("Run install.py first to set up the environment.", file=sys.stderr)
        sys.exit(1)

    models = discover_models()
    model_name, model_path = choose_model(models)

    print(f"Model: {{model_name}}")
    print(f"Path:  {{model_path}}")
    print(f"\\nStarting mlx_lm server on http://localhost:{{args.port}}")
    print(f"  POST http://localhost:{{args.port}}/v1/chat/completions")
    print(f"  POST http://localhost:{{args.port}}/v1/completions")
    print("\\nPress Ctrl+C to stop.\\n")

    cmd = [
        str(python), "-m", "mlx_lm", "server",
        "--model", model_path,
        "--port", str(args.port),
    ]
    print(f">>> {{' '.join(cmd)}}\\n")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\\nServer stopped.")


if __name__ == "__main__":
    main()
'''


def run(cmd, **kwargs):
    print(f">>> {' '.join(cmd)}")
    subprocess.check_call(cmd, **kwargs)


def clean():
    """Remove all generated files in the project directory except install.py itself."""
    keep = {SCRIPT_PATH}
    removed = False
    for item in PROJECT_DIR.iterdir():
        if item.resolve() in keep:
            continue
        if item.is_dir():
            print(f"Removing directory {item} ...")
            shutil.rmtree(item)
            removed = True
        else:
            print(f"Removing file {item} ...")
            item.unlink()
            removed = True
    if removed:
        print("Clean complete.")
    else:
        print("Nothing to clean.")


def write_project_files(model_name="", model_path=""):
    """Write example_config.yaml, run_server.py, and update models.json."""
    EXAMPLE_CONFIG.write_text(CONFIG_YAML.format(port=DEFAULT_PORT, model_path=model_path, model_name=model_name))
    print(f"Written {EXAMPLE_CONFIG}")

    RUN_SERVER.write_text(RUN_SERVER_PY.format(port=DEFAULT_PORT))
    RUN_SERVER.chmod(RUN_SERVER.stat().st_mode | 0o755)
    print(f"Written {RUN_SERVER}")

    # Update models.json (accumulate entries across installs)
    models = []
    if MODELS_JSON.exists():
        with open(MODELS_JSON) as f:
            models = json.load(f)
    models = [m for m in models if m["name"] != model_name]
    models.append({"name": model_name, "path": model_path})
    MODELS_JSON.write_text(json.dumps(models, indent=2) + "\n")
    print(f"Written {MODELS_JSON}")


def prompt_model_choice():
    """Ask the user which model to install. Returns (model_id, model_variant, model_name)."""
    print("\nWhich model would you like to install?\n")
    for key, info in MODELS.items():
        print(f"  {key}) {info['label']}")
    while True:
        choice = input("\nEnter 1 or 2 [1]: ").strip() or "1"
        if choice in MODELS:
            selected = MODELS[choice]
            print(f"\n  \u2192 {selected['label']}")
            return selected["id"], selected["variant"], selected["name"]
        print("Invalid choice. Please enter 1 or 2.")


def install():
    # 1. Create project folder
    ENV_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Project folder: {ENV_DIR}")

    # 2. Create virtual environment
    print("\n--- Creating virtual environment ---")
    run([sys.executable, "-m", "venv", str(VENV_DIR)])

    # 3. Determine pip/python paths inside the venv
    if sys.platform == "win32":
        pip = str(VENV_DIR / "Scripts" / "pip")
        python = str(VENV_DIR / "Scripts" / "python")
    else:
        pip = str(VENV_DIR / "bin" / "pip")
        python = str(VENV_DIR / "bin" / "python")

    # 4. Upgrade pip
    print("\n--- Upgrading pip ---")
    run([pip, "install", "--upgrade", "pip"])

    # 5. Install mlx-lm (pulls in mlx, transformers, huggingface-hub, etc.)
    print("\n--- Installing mlx-lm ---")
    run([pip, "install", "mlx-lm"])

    # 6. Prompt user to choose a model, then download it.
    model_id, model_variant, model_name = prompt_model_choice()

    print(f"\n--- Downloading model: {model_id} (variant: {model_variant}) ---")
    result = subprocess.run(
        [
            python, "-c",
            (
                "import os; "
                "from huggingface_hub import snapshot_download; "
                "from mlx_lm import load; "
                f"path = snapshot_download('{model_id}', "
                f"allow_patterns='{model_variant}/*'); "
                f"model_path = os.path.join(path, '{model_variant}'); "
                "print(f'Model downloaded to: {{model_path}}'); "
                "model, tokenizer = load(model_path); "
                "print('Model loaded successfully.'); "
                "print('MODEL_PATH=' + model_path)"
            ),
        ],
        capture_output=True, text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError("Model download/load failed")

    # Extract the resolved model path from the output
    model_path = None
    for line in result.stdout.splitlines():
        if line.startswith("MODEL_PATH="):
            model_path = line[len("MODEL_PATH="):]
            break
    if not model_path:
        raise RuntimeError("Could not determine model path from download output")

    # Verify the model's config.json
    config_file = Path(model_path) / "config.json"
    if config_file.exists():
        config = json.loads(config_file.read_text())
        if "model_type" not in config:
            print(f"Warning: config.json is missing 'model_type'", file=sys.stderr)
        if "quantization" not in config:
            print(f"Warning: config.json is missing 'quantization'", file=sys.stderr)
        print(f"Model config: model_type={config.get('model_type')}, "
              f"quantization={config.get('quantization')}")
    else:
        print(f"Warning: config.json not found at {config_file}", file=sys.stderr)

    # Now (re-)generate project files with the resolved model path
    write_project_files(model_name=model_name, model_path=model_path)

    print("\n=== Setup complete ===")
    print(f"Virtual environment: {VENV_DIR}")
    print(f"Model path: {model_path}")
    print(f"\nTo activate the environment:\n  source {VENV_DIR}/bin/activate")

    # Offer to create the Continue config file
    setup_continue_config(model_name=model_name, model_path=model_path)


def setup_continue_config(model_name="", model_path=""):
    """Ask the user whether to create/overwrite the Continue config.yaml."""
    if CONTINUE_CONFIG.exists():
        answer = input(
            f"\n{CONTINUE_CONFIG} already exists. Overwrite with the example config? [y/N] "
        ).strip().lower()
        if answer != "y":
            print("Skipping Continue config setup.")
            return
    else:
        answer = input(
            f"\nCreate Continue config at {CONTINUE_CONFIG}? [Y/n] "
        ).strip().lower()
        if answer == "n":
            print("Skipping Continue config setup.")
            return

    CONTINUE_DIR.mkdir(parents=True, exist_ok=True)
    CONTINUE_CONFIG.write_text(CONFIG_YAML.format(port=DEFAULT_PORT, model_path=model_path, model_name=model_name))
    print(f"Continue config written to {CONTINUE_CONFIG}")


def main():
    parser = argparse.ArgumentParser(description="Install mlx-lm + DeepSeek-R1-Distill-Qwen-32B-MLX")
    parser.add_argument("--clean", action="store_true", help="Remove all generated files and exit")
    args = parser.parse_args()

    if args.clean:
        clean()
        return

    try:
        install()
    except Exception as exc:
        print(f"\n!!! Installation failed: {exc}", file=sys.stderr)
        print("Cleaning up ...", file=sys.stderr)
        clean()
        sys.exit(1)


if __name__ == "__main__":
    main()
