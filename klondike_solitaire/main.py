from game_logic import GameState, Card, Deck, Pile, TableauPile, FoundationPile, StockPile, WastePile # Importing all for now, will reduce later if possible

def display_game(game_state: GameState):
    """
    Prints a user-friendly representation of the current board state.
    """
    print("\n" + "="*30)
    print("   KLONDIKE SOLITAIRE")
    print("="*30)

    # Foundations
    foundation_strs = []
    for i, pile in enumerate(game_state.foundation_piles):
        foundation_strs.append(f"F{i+1}: {str(pile):<3}") # Pad to ensure alignment
    print("Foundations: " + " | ".join(foundation_strs))

    # Stock and Waste
    stock_status = f"Stock: {len(game_state.stock_pile.cards)} cards" if not game_state.stock_pile.is_empty() else "Stock: Empty"
    waste_status = f"Waste: {str(game_state.waste_pile):<3}" if not game_state.waste_pile.is_empty() else "Waste: Empty"
    print(f"{stock_status:<18} | {waste_status}")
    print("-"*30)

    # Tableau Piles
    print("Tableau Piles:")
    headers = [f"T{i+1:<2}" for i in range(len(game_state.tableau_piles))] # T1, T2 etc.
    
    max_cards = 0
    for pile in game_state.tableau_piles:
        if len(pile.cards) > max_cards:
            max_cards = len(pile.cards)

    # Print tableau headers (T1, T2, ...)
    header_str = "  ".join(headers)
    print(f"   {header_str}")
    print(f"   {'-- ' * len(game_state.tableau_piles)}")


    for i in range(max_cards):
        line = []
        for pile in game_state.tableau_piles:
            if i < len(pile.cards):
                line.append(f"{str(pile.cards[i]):<3}") # Pad card string
            else:
                line.append("   ") # Empty space for alignment
        print(f"{i+1:>2} | {'  '.join(line)}")
    print("="*30 + "\n")

def get_help():
    """Returns a string containing the help message for game commands."""
    return """
Available Commands:
  draw (d)                     : Draw a card from the stock pile.
  move (m) src dest [args...]  : Move card(s).
    Sources (src):
      w, waste                 : Waste pile
      t, tableau <idx>         : Tableau pile (e.g., t1, t2)
      f, foundation <idx>      : Foundation pile (e.g., f1, f2) - usually for display, not source.
    
    Destinations (dest):
      f, foundation <idx>      : Foundation pile (e.g., f1, f2)
      t, tableau <idx>         : Tableau pile (e.g., t1, t2)

    Examples:
      m w f1                   : Move from Waste to Foundation 1.
      m w t3                   : Move from Waste to Tableau 3.
      m t2 f1                  : Move from Tableau 2 to Foundation 1.
      m t1 t5                  : Move top card from Tableau 1 to Tableau 5.
      m t1 t5 3                : Move 3 cards from Tableau 1 to Tableau 5.
  
  reset                        : Reset stock from waste (if stock is empty and you prefer manual).
                                 Note: 'draw' automatically handles this.
  help (h)                     : Display this help message.
  quit (q)                     : Exit the game.

Pile numbers are 1-indexed (e.g., f1, t3).
"""

def parse_command(command_str: str) -> tuple | None:
    """
    Parses a raw string input from the user into a command and its arguments.
    Returns a tuple like ('command_name', [args]) or None if invalid.
    """
    parts = command_str.lower().strip().split()
    if not parts:
        return None

    cmd = parts[0]

    if cmd in ["draw", "d"]:
        return ("draw", [])
    elif cmd in ["quit", "q"]:
        return ("quit", [])
    elif cmd in ["help", "h"]:
        return ("help", [])
    elif cmd in ["reset"]: # Added for completeness, though draw handles it
        return ("reset", [])
    elif cmd in ["move", "m"]:
        if len(parts) < 3:
            print("Invalid move command: Not enough arguments. Use 'help' for syntax.")
            return None
        
        source_type = parts[1]
        
        # m w f <f_idx>
        if source_type in ["w", "waste"]:
            if len(parts) != 4:
                print("Invalid 'move waste' command format. Expected: m w <dest_type> <dest_idx>")
                return None
            dest_type = parts[2]
            try:
                dest_idx = int(parts[3])
            except ValueError:
                print(f"Invalid index '{parts[3]}'. Must be a number.")
                return None

            if dest_type in ["f", "foundation"]:
                return ("move_waste_to_foundation", [dest_idx])
            elif dest_type in ["t", "tableau"]:
                return ("move_waste_to_tableau", [dest_idx])
            else:
                print(f"Invalid destination type '{dest_type}' for moving from waste.")
                return None

        # m t <t_src_idx> f <f_idx>
        # m t <t_src_idx> t <t_dest_idx> [num_cards]
        elif source_type in ["t", "tableau"]:
            if len(parts) < 5: # m t src_idx dest_type dest_idx
                print("Invalid 'move tableau' command format. Not enough arguments.")
                return None
            try:
                src_idx = int(parts[2])
            except ValueError:
                print(f"Invalid source tableau index '{parts[2]}'. Must be a number.")
                return None
            
            dest_type = parts[3]
            try:
                dest_idx = int(parts[4])
            except ValueError:
                print(f"Invalid destination index '{parts[4]}'. Must be a number.")
                return None

            if dest_type in ["f", "foundation"]:
                if len(parts) == 5:
                    return ("move_tableau_to_foundation", [src_idx, dest_idx])
                else:
                    print("Invalid 'move tableau to foundation' command. Expected: m t <src_idx> f <dest_idx>")
                    return None
            elif dest_type in ["t", "tableau"]:
                num_cards = 1
                if len(parts) == 6: # m t src_idx t dest_idx num_cards
                    try:
                        num_cards = int(parts[5])
                        if num_cards < 1:
                             print("Number of cards to move must be at least 1.")
                             return None
                    except ValueError:
                        print(f"Invalid number of cards '{parts[5]}'. Must be a number.")
                        return None
                elif len(parts) > 6:
                    print("Too many arguments for 'move tableau to tableau'.")
                    return None
                return ("move_tableau_to_tableau", [src_idx, dest_idx, num_cards])
            else:
                print(f"Invalid destination type '{dest_type}' for moving from tableau.")
                return None
        else:
            print(f"Invalid source type '{source_type}'. Use 'w' for waste or 't' for tableau.")
            return None
    else:
        print(f"Unknown command: '{cmd}'. Type 'help' for available commands.")
        return None

def main_game_loop():
    """Main loop for the Klondike Solitaire game."""
    game = GameState()
    print("Welcome to Klondike Solitaire!")

    while True:
        display_game(game)

        if game.check_win_condition():
            print("********************************************")
            print("* Congratulations! You've won the game! *")
            print("********************************************")
            break

        try:
            user_input = input("Enter command (or 'help'): ").strip()
            if not user_input:
                continue
        except EOFError: # Handle Ctrl+D or other EOF
            print("\nQuitting game. Goodbye!")
            break


        parsed_command = parse_command(user_input)

        if parsed_command is None:
            # Error message already printed by parse_command
            continue

        command, args = parsed_command
        action_taken = False
        success = False

        if command == "quit":
            print("Quitting game. Goodbye!")
            break
        elif command == "help":
            print(get_help())
            action_taken = True # Not a game move, but action handled
            success = True # No failure state for help
        elif command == "draw":
            game.draw_from_stock() # Assumes draw_from_stock handles empty stock/reset logic
            print("Drew from stock.")
            action_taken = True
            success = True # Draw itself is always "successful" in terms of execution
        elif command == "reset": # Manual reset, if draw doesn't auto-reset or user prefers
            if game.stock_pile.is_empty() and not game.waste_pile.is_empty():
                game.reset_stock_from_waste()
                print("Stock reset from waste.")
                success = True
            elif not game.stock_pile.is_empty():
                print("Stock is not empty. Cannot reset from waste yet.")
                success = False
            else: # Waste is empty
                print("Waste pile is empty. Nothing to reset stock with.")
                success = False
            action_taken = True
        elif command == "move_waste_to_foundation":
            f_idx = args[0]
            if 1 <= f_idx <= 4:
                success = game.move_waste_to_foundation(f_idx - 1)
                print(f"Move from Waste to Foundation {f_idx}: {'Success' if success else 'Failed'}")
            else:
                print(f"Invalid foundation index: {f_idx}. Must be 1-4.")
                success = False
            action_taken = True
        elif command == "move_waste_to_tableau":
            t_idx = args[0]
            if 1 <= t_idx <= 7:
                success = game.move_waste_to_tableau(t_idx - 1)
                print(f"Move from Waste to Tableau {t_idx}: {'Success' if success else 'Failed'}")
            else:
                print(f"Invalid tableau index: {t_idx}. Must be 1-7.")
                success = False
            action_taken = True
        elif command == "move_tableau_to_foundation":
            t_src_idx, f_idx = args[0], args[1]
            if not (1 <= t_src_idx <= 7):
                print(f"Invalid source tableau index: {t_src_idx}. Must be 1-7.")
                success = False
            elif not (1 <= f_idx <= 4):
                print(f"Invalid foundation index: {f_idx}. Must be 1-4.")
                success = False
            else:
                success = game.move_tableau_to_foundation(t_src_idx - 1, f_idx - 1)
                print(f"Move from Tableau {t_src_idx} to Foundation {f_idx}: {'Success' if success else 'Failed'}")
            action_taken = True
        elif command == "move_tableau_to_tableau":
            t_src_idx, t_dest_idx, num_cards = args[0], args[1], args[2]
            if not (1 <= t_src_idx <= 7):
                print(f"Invalid source tableau index: {t_src_idx}. Must be 1-7.")
                success = False
            elif not (1 <= t_dest_idx <= 7):
                print(f"Invalid destination tableau index: {t_dest_idx}. Must be 1-7.")
                success = False
            elif t_src_idx == t_dest_idx:
                print(f"Source and destination tableau cannot be the same (T{t_src_idx}).")
                success = False
            else:
                success = game.move_tableau_to_tableau(t_src_idx - 1, t_dest_idx - 1, num_cards)
                print(f"Move {num_cards} card(s) from Tableau {t_src_idx} to Tableau {t_dest_idx}: {'Success' if success else 'Failed'}")
            action_taken = True
        
        if action_taken and not success and command not in ["help", "quit"]: # Help and quit don't have "failure"
             print("Invalid move. Please check the rules or card states.")
        
        # Small delay for readability if an action was taken
        # if action_taken:
        #     time.sleep(0.5) # Consider adding import time

if __name__ == "__main__":
    main_game_loop()
