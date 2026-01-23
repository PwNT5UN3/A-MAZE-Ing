*This project has been created as part of the 42 curriculum by mnestere and mawelsch.* 

---

# A-MAZE-Ing

An advanced maze generation and visualization tool built using Python, featuring multiple generation algorithms, interactive terminal UI with customizable colors, and automated pathfinding capabilities.

## Description

**A-MAZE-Ing** is a maze generation project that combines algorithmic maze creation with an interactive visualization system.

### Project Goals

- **Generate perfect and imperfect mazes**
- **Visualize maze generation and pathfinding**
- **Provide interactive controls**
- **Support reproducible results**
- **Output structured maze data**

### Key Features

- **Interactive Terminal UI** with real-time rendering and color customization
- **Multiple Generation Algorithms**: Wilson's Algorithm and Depth-First Search
- **Automated Pathfinding** using Breadth-First Search (BFS)
- **Reproducible Results** via Mersenne Twister PRNG with configurable seeds
- **42 Pattern Integration** - automatically embeds the iconic "42" pattern in generated mazes
- **Flexible Configuration** through a config file
- **Output Validation** with direction sequences

---
## Instructions

### Requirements

- Python 3.11 or higher
- pip (Python package manager)
- uv (Python package and project manager)

### Installation
<!-- 
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd A-MAZE-Ing
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

   Or manually install required packages:
   ```bash
   pip install pandas requests matplotlib termcolor readchar numpy
   ``` -->

###  Usage

#### Basic Usage

Run the maze generator with a configuration file:

```bash
python a_maze_ing.py config.txt
```

#### Interactive Controls

Once the program starts, you'll see:

- **[SPACE]** - Generate/Regenerate maze with animated pathfinding
- **[P]** - Toggle path visibility
- **[C]** - Open color customization menu
- **[Q]** - Quit the application

#### Color Customization Menu

In the color menu, you can customize:
1. **Wall Color** - Color of maze walls
2. **42 Pattern Color** - Color of the "42" pattern cells
3. **Path Color** - Color of the solution path
4. **Background Color** - Terminal background color
5. **Preview** - To see the changes immediately

### Configuration File Structure

Create a `config.txt` file with the following structure:

```ini
# Mandatory Configuration Keys

# Dimensions (integers > 0)
width = 20
height = 20

# Entry and exit points (x, y coordinates)
# Must be within maze bounds: 0 <= x < width, 0 <= y < height
entry = 0,0
exit = 19, 19

# Optional Configuration Keys

# Perfect maze flag (true/false)
# true: Perfect maze (no loops, single path between any two points)
# false: May contain loops and multiple paths
perfect = false

# Output file path
output_file = output.txt

# Random seed (integer: 0 to 2,147,483,647)
# Omit or set to -1 for random seed
seed = 42

# Algorithm selection (dfs/wilson)
# dfs: Depth-First Search (faster, creates long corridors)
# wilson: Wilson's Algorithm (uniform distribution, slower)
algorithm = dfs
```
### Output

The program generates an `output.txt` (or custom filename) containing:

```
<encoded_maze>

<entry_y> <entry_x>
<exit_y> <exit_x>
<DIRECTION_SEQUENCE>
```

**Direction Format:**
- `N` - North (up)
- `S` - South (down)
- `E` - East (right)
- `W` - West (left)

---

## Maze Generation Algorithms

### 1. **Depth-First Search (DFS)** 

**Why We Chose DFS:**

- **Simplicity and reliability** - straightforward iterative/stack-based implementation

- **Perfect maze guarantee** - always produces spanning trees without loops

**How It Works:**

1. Start from a random cell
2. Mark current cell as visited
3. While unvisited neighbors exist:
   - Choose random unvisited neighbor
   - Remove wall between current and chosen cell
   - Iteratively visit chosen cell
4. Backtrack when no unvisited neighbors remain

**Implementation Details:**
- Uses iterative approach with explicit stack to avoid recursion depth limits
- Mersenne Twister PRNG ensures high-quality randomization
- Automatically avoids the "42" pattern cells

### 2. **Wilson's Algorithm** 

**Alternative Algorithm:**

Wilson's Algorithm generates **uniformly distributed** mazes, meaning every possible maze has an equal probability of being generated.

**How It Works:**

1. Choose random cell and add to maze
2. For each unvisited cell:
   - Generate a random path and attach it to the maze.
   If encountering a loop in the walk, remove the entire loop
   - Add the walk path to the maze
3. Repeat until all cells are part of the maze

**Trade-offs:**
- **Uniform distribution** - unbiased maze generation
- **Interesting patterns** - less corridor bias than DFS
- **Drastically slower** - especially on large mazes
- **Complex implementation** - requires loop detection

---

### Code Architecture

```
A-MAZE-Ing/
├── mazegen/              # Maze generation package
│   ├── __init__.py      # Public API exports
│   └── maze_gen.py      # Core algorithms & data structures
├── a_maze_ing.py        # Main entry point
├── bfs.py               # Pathfinding implementation
├── render.py            # Terminal UI & visualization
├── config_reader.py     # Configuration parser
├── output_file_generation.py  # Output formatter
├── output_validator.py  # Validation utilities
└── config.txt           # Example configuration
```

---

## Team & Project Management

### Team Roles

**mnestere** (Developer)
- BFS pathfinding system
- Terminal UI & rendering engine
- Code architecture & large-scale refactoring
- Documentation & testing - README


**mawelsch** (Developer)
- Core maze generation — DFS, Wilson's Algorithm
- Configuration system design
- Build, automation & deployment - Makefile, packaging
- Output generation & validation - format encoder
- Documentation & testing - README

### Planning Evolution

Intensive Sprint — All core work delivered in one week

- Focused sprint: implemented DFS, Wilson's Algorithm, BFS, core data structures,
config system and initial TUI integration

- Day‑by‑day improvements during the same week: TUI usability, output format, basic tests and bug fixes
- Delivered an integrated, working prototype by the end of the week
Follow‑up (post‑sprint)

- Polishing and hardening: color customization, validator, CI/type fixes
- Performance tuning and caching
- Documentation, examples and README improvements 

### What Worked Well

- **Modular design** using OOP and Design Patterns
- **Interactive UI** 

### What Could Be Improved

- **Better separation** of rendering and game logic
- **Additional algorithms** (A*, Dijkstra, Kruskal)
- **Scalability of the TUI** using PyGame, MLX, TKinter
### Tools Used

- **Development:**
  - VS Code with auto-formatting 
  - mypy for static type checking
  - flake8 for linting
  - Git for version control

- **Testing:**
  - Manual testing with various configurations
  - Output validator for correctness verification

- **Libraries:**
  - NumPy for efficient random number generation
  - termcolor for colored terminal output
  - readchar for keyboard input handling
  - dataclasses for clean data structures

---

## Resources

### Classic References

**Maze Generation:**
- [Maze Generation Algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm) - Wikipedia overview

**Pathfinding:**
- [Breadth-First Search](https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/) - BFS algorithm explanation
- [Breadth-First Search](https://www.youtube.com/watch?v=D14YK-0MtcQ) - BFS algorithm explanation for mazes
- [Depth-First Search](https://www.youtube.com/watch?v=Hr5cWUld4vU) - DFS alghorithm for better global understanding

**Python & Design:**
- [ABC Module](https://www.geeksforgeeks.org/python/abstract-base-class-abc-in-python/) - GFG page for abstract base classes
- [Dataclasses](https://www.youtube.com/watch?v=vBH6GRJ1REM) - Modern Python data structures

### 🥶 AI Usage

**AI was used for:**

1. **Code Refactoring & Type Safety**
   - Converting code to strict mypy compliance
   - Fixing type hint errors and inconsistencies

2. **Bug Fixing**
   - Fixing tuple construction issues
   - Code: Throughout codebase

3. **Documentation & README**
   - Docstrings for the Classes & Functions

4. **Code Review & Best Practices** 
   - Suggesting more Pythonic approaches
   - Identifying potential performance improvements

---

## Advanced Features

### Interactive Color Customization

- **Color options** for walls, paths, patterns, and backgrounds
- **Live preview** of color changes
- **Persistent settings** during session
- **Optimized rendering** with color caching

### Animated Pathfinding

- **Step-by-step visualization** of BFS pathfinding

### 🥶 42 Pattern Integration

- **Automatic detection** of maze size
- **Smart placement** centered in maze
- **Collision avoidance** prevents entry/exit overlap
- **Visual distinction** with custom coloring

### Flexible Configuration

- **Comprehensive validation** with helpful error messages
- **Optional parameters** with sensible defaults
- **Seed control** for reproducible results


**Made with 🔥 at 🔥42 Heilbronn🔥**

