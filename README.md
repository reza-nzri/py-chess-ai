# py-chess-ai

A **Python-based chess game** with increasing levels of artificial intelligence,
from **Human vs Human** to **Human vs Computer using MiniMax**.

## 🎯 Features & Scoring

- **Human vs Human**
- **Human vs Computer (Random AI)**
  - Random piece selection
  - Random valid move
- **Human vs Computer (MiniMax AI)**

## 🧰 Tech Stack

- Python 3.11+
- Object-Oriented Design
- Modular and package-based architecture
- UI via `pygame` or CLI
- Dependency management with `uv`

<details>
<summary><h2>✅ Prerequisites</h2></summary>

- Python 3.11 or newer
- [`uv`](https://github.com/astral-sh/uv)

</details>

<details>
<summary><h2>⚙️ Setup</h2></summary>

Install dependencies using the lockfile:

```bash
uv sync
````

</details>
<details>
<summary><h2>▶️ Running the Application</h2></summary>

Always run the project through `uv` to ensure the correct environment.

```bash
# Run with F5 in vs code for debuging

# Human vs Human
uv run python src/__main__.py --mode manual

# Human vs Computer
uv run python src/__main__.py --mode ai

# Test / evaluation mode
uv run python src/__main__.py --mode test
```

</details>
<details>
<summary><h2>🧪 Running Tests</h2></summary>

### Unit Tests

```bash
uv run python -m unittest
```

### Pytest (recommended)

```bash
uv run pytest
```

All tests **must pass** during evaluation.
</details>

## 🤝 Team Workflow

- Incremental weekly progress
- Git-based collaboration
- Code reviews before merging
