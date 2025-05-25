# Klondike Solitaire

## Description
This is a text-based implementation of the classic Klondike Solitaire card game. The game logic and user interface are built using Python.

## Features
*   **Standard Klondike Rules**: Implements the common rules for moving cards, building foundations, and drawing from the stock.
*   **Text-Based Interface**: Play the game entirely within your command line terminal.
*   **Move Validation**: The game checks if your attempted moves are valid according to Klondike rules.
*   **Win Detection**: The game automatically detects when you have successfully moved all cards to the foundation piles.
*   **Interactive Command Loop**: Input commands to interact with the game.

## Requirements
*   Python 3.x

## How to Run
1.  Ensure you have Python 3 installed on your system.
2.  Navigate to the root directory of this project (the directory containing the `klondike_solitaire` folder).
3.  Run the game using the following command:
    ```bash
    python klondike_solitaire/main.py
    ```

## How to Play

### Objective
The goal of Klondike Solitaire is to move all 52 cards to the four Foundation piles. Each Foundation pile is built up by suit, starting from Ace, then 2, 3, and so on, up to the King.

### Basic Commands
The game is controlled by typing commands into the prompt. Here are the main commands:

*   **`draw`** (or **`d`**)
    *   Draws a card (or cards, depending on game settings, typically 1 or 3) from the Stock pile to the Waste pile.
    *   If the Stock pile is empty, this command will typically move all cards from the Waste pile back to the Stock pile, face-down.

*   **`move <source> <destination> [args...]`** (or **`m <src> <dest> [args...]`**)
    *   Moves card(s) between different piles. Pile indices for Tableau and Foundation are 1-indexed.
    *   **Sources (`src`):**
        *   `w` or `waste`: The Waste pile.
        *   `t <idx>` or `tableau <idx>`: A Tableau pile (e.g., `t1`, `tableau2`).
    *   **Destinations (`dest`):**
        *   `f <idx>` or `foundation <idx>`: A Foundation pile (e.g., `f1`, `foundation3`).
        *   `t <idx>` or `tableau <idx>`: A Tableau pile.
    *   **Examples:**
        *   `m w f1` or `move waste foundation 1`: Move the top card from the Waste pile to Foundation pile 1.
        *   `m w t3` or `move waste tableau 3`: Move the top card from the Waste pile to Tableau pile 3.
        *   `m t2 f4` or `move tableau 2 foundation 4`: Move the top card from Tableau pile 2 to Foundation pile 4.
        *   `m t1 t5` or `move tableau 1 tableau 5`: Move the top face-up card from Tableau pile 1 to Tableau pile 5.
        *   `m t1 t5 3` or `move tableau 1 tableau 5 3`: Move the top 3 face-up cards from Tableau pile 1 to Tableau pile 5.

*   **`reset`**
    *   If the Stock pile is empty and the Waste pile is not, this command moves all cards from the Waste pile back to the Stock pile (face-down).
    *   Note: The `draw` command typically handles this automatically when the stock is empty.

*   **`help`** (or **`h`**)
    *   Displays a detailed help message with all available commands and their syntax.

*   **`quit`** (or **`q`**)
    *   Exits the game.

Good luck, and enjoy the game!
