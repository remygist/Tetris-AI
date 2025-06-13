# NeuroBlocks

**NeuroBlocks** is a Tetris game with built-in AI opponents that play in real-time against the human player. It supports multiple AI strategies including a Genetic Algorithm (GA) and Deep Q-Learning (DQN). Developed in Python using Pygame and PyTorch, it offers a full UI, statistics tracking, and customizable difficulty levels.

---

## Features

- Real-time Tetris gameplay: Player vs. AI
- Difficulty selection: Easy, Medium, Hard
- Heuristic AI (GA) and DQN AI trained via reinforcement learning
- Stats screen with per-game and average analytics
- Modular codebase with clean UI and gameplay separation

---

## AI Agents

### Genetic Algorithm (GA)
Scores each valid move using evolved weights over 8 board features.

### Deep Q-Network (DQN)
Trained using experience replay, PyTorch, and a target network. Uses same 8 features as GA.

---

## Installation

### Prerequisites
- Python 3.10+
- PyTorch
- Pygame
- Numpy

### Install dependencies
1. **Clone the repository**
2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the application**
   ```sh
   python main.py
   ```
4. **Run training (optional)**
    ```sh
    python dqn/train_dqn.py
    ```

---

## File structure
```
neuroblocks/
├── assets/                 # Fonts and background images
├── dqn/
|   └── pretrain_dqn.py     # Pretraining script for GA weights
│   └── replay_memory.py    # Experience replay buffer
│   └── train_dqn.py        # Training script for DQN agent
│   └── train_utils.py      # Training step logic
├── ga/
│   └── fitness_history/    # Graphs of GA training
│   └── saved_weights/      # GA-trained heuristic weights (JSON)
│   └── benchmark.py        # Benchmark script to find best weights
│   └── ga.py               # GA training script
├── game/                   # Core Tetris logic
│   └── game.py             # Main Game and Tetromino classes
│   └── timer.py            # Timer for controlling input rate
│   └── bag_generator.py    # Script for generating 7-random-bags
├── interface/              # UI components (menus, buttons, stats screens)
├── models/                 
│   └── dqn_model.py        # DQN model definition and model loader
│   └── easy/               # Contains easy difficulty model
│   └── medium/             # Contains medium difficulty model
│   └── hard/               # Contains hard difficulty model
│   └── dqn_pretrained.py   # Pretrained dqn model
├── tests/                  # Test files
├── .gitignore              # Ignore sensitive files in git
├── ai_controller.py        # Heuristic evaluation and move picking
├── main.py                 # Main game loop and state machine
└── README.md               # Project documentation
├── settings.py             # Global constants (board size, colors, etc.)
├── stats.json              # Persistent game statistics
```
---

## Game Workflow
1. **Start Menu** - Choose to play or quit.
2. **Difficulty Select** – Easy, Medium, Hard (loads corresponding AI model).
3. **Gameplay** – Player plays with arrow keys; AI plays on delay.
4. **Game Over** – View scores and stats.
5. **Statistics Screen** – View per-game and average stats for both player and AI.

---

## AI Board Features
The AI (both GA and DQN) uses the following 8 features to evaluate a Tetris board:
- Number of Holes
- Lines Cleared
- Bumpiness (column height difference)
- Total Column Height
- Max Column Height
- Wells
- Row Transitions
- Column Transitions

---

## Statistics Tracking
All games are logged to ```stats.json```. The following metrics are tracked for both the player and AI:
- Score
- Lines Cleared
- Total moves
- Number of holes
- Number of tetrises
- Average per-game breakdown

---

## Training the DQN Agent
- Uses epsilon-greedy strategy with GA fallback for exploration
- Rewards based on lines cleared and penalized for height
- Saves model every 50 episodes

---

## AI Strategy Details
- **GA Agent**: Selects the best action by evaluating the board score using pre-evolved weights.
- **DQN Agent**: Predicts Q-values for all valid placements based on board state features and selects the highest.

---

## Sources
- [License](https://choosealicense.com/licenses/mit/)
- [Tetris clone tutorial](https://www.youtube.com/watch?v=ROElF_BlUJI&list=PL4cUxeGkcC9iurLoO9Mu7GqsKlxEXcf8m)
- [Tetris guidelines](https://tetris.fandom.com/wiki/Tetris_Guideline)
- [Python](https://www.python.org/)
- [PyGame](https://www.pygame.org/news)
- [PyTorch](https://pytorch.org/)
- [Deep Q-learning](https://www.geeksforgeeks.org/deep-q-learning/)
- [Reinforcement learning](https://www.geeksforgeeks.org/what-is-reinforcement-learning/)
- [Genetic Algorithms](https://www.geeksforgeeks.org/genetic-algorithms/)
- [ChatGPT - coding along & debugging](https://chatgpt.com/share/684c1132-e14c-8007-b14c-5c6129885f22)



