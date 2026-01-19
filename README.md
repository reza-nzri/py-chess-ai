# py-chess-ai

A **Python-based chess game** with increasing levels of artificial intelligence,
from **Human vs Human** to **Human vs Computer using MiniMax**.

## 🎯 Features & Scoring

- **Human vs Human**
- **Human vs Computer (Random AI)**
  - Random piece selection
  - Random valid move
- **Human vs Computer (MiniMax AI)**

### 🤖 MiniMax AI

The MiniMax AI uses a depth-limited search to evaluate future game states.
Moves are scored using a material-based evaluation, extended with simple heuristics
such as mobility, capture potential, and center control.

## 🧰 Tech Stack

- Python 3.13+
- Object-Oriented Design
- Modular and package-based architecture
- UI via `pygame` or CLI
- Dependency management with `uv`

<details>
  <summary><h2>🎓 University Evaluation Criteria</h2></summary>

This project fulfills the official requirements of the course *Schach KI*:

- Human vs Human chess game (up to 70 points)
- Human vs Computer (Random valid moves) (up to 10 points)
- Human vs Computer using MiniMax (up to 30 points)

**Test Mode:**  
All functionalities can be demonstrated by running the project in test mode.
</details>

<details>
<summary><h2>✅ Prerequisites</h2></summary>

- Python 3.11 or newer
- [`uv`](https://github.com/astral-sh/uv)

### ⚙️ Setup

Install dependencies using the lockfile: `uv sync`

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

<details>
<summary><h2>🧠 Enable MiniMax AI - (Real AI) instead of Random AI</h2></summary>

By default, running `--mode ai` uses **Random AI** (random valid moves).
To enable the **MiniMax AI**, change **one line** in the UI code:

### Step 1 — Open the `src/ui.py` file

### Step 2 — Change the AI move function (lines 183–184)

Find this block inside `nextMove = suggest`:

```python
if nextMove is None and not manual:
    # nextMove = suggest_move(board)
    nextMove = suggest_random_move(board)
```

Replace it with:

```python
if nextMove is None and not manual:
    nextMove = suggest_move(board)          # MiniMax (AI)
    # nextMove = suggest_random_move(board) # Random AI
```

✅ Done. Now `--mode ai` will use **MiniMax AI**.

### Step 3 — Run the game

```bash
uv run python src/__main__.py --mode ai
```

### Switch back to Random AI

Undo the change (use `suggest_random_move(board)` again).
</details>

</details>

## 🤝 Team Workflow

- Incremental weekly progress
- Git-based collaboration
- Code reviews before merging
