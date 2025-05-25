import random

class Card:
    """Represents a playing card."""
    def __init__(self, suit: str, rank: str, is_face_up: bool = False):
        """
        Initializes a Card object.

        Args:
            suit: The suit of the card (e.g., "Hearts", "Diamonds", "Clubs", "Spades").
            rank: The rank of the card (e.g., "A", "2", ..., "10", "J", "Q", "K").
            is_face_up: Whether the card is face up or face down. Defaults to False.
        """
        self.suit = suit
        self.rank = rank
        self.is_face_up = is_face_up

        if rank.isdigit():
            self.value = int(rank)
        elif rank == "A":
            self.value = 1
        elif rank == "J":
            self.value = 11
        elif rank == "Q":
            self.value = 12
        elif rank == "K":
            self.value = 13
        else:
            raise ValueError(f"Invalid rank: {rank}")

        if suit in ["Hearts", "Diamonds"]:
            self.color = "Red"
        elif suit in ["Clubs", "Spades"]:
            self.color = "Black"
        else:
            raise ValueError(f"Invalid suit: {suit}")

    def __str__(self) -> str:
        """Returns the string representation of the card."""
        if self.is_face_up:
            return f"{self.rank}{self.suit[0]}"
        else:
            return "[ ]" # Changed from "[XX]" to "[ ]" for consistency

class Deck:
    """Represents a deck of playing cards."""
    SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
    RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    def __init__(self):
        """Initializes a standard 52-card deck and shuffles it."""
        self.cards = [Card(suit, rank) for suit in self.SUITS for rank in self.RANKS]
        self.shuffle()

    def shuffle(self):
        """Randomizes the order of cards in the deck."""
        random.shuffle(self.cards)

    def deal(self) -> Card | None:
        """
        Removes and returns the top card from the deck.

        Returns:
            The top card, or None if the deck is empty.
        """
        if self.cards:
            return self.cards.pop()
        else:
            return None

    def __len__(self) -> int:
        """Returns the number of cards remaining in the deck."""
        return len(self.cards)

class Pile:
    """Base class for a pile of cards."""
    def __init__(self):
        """Initializes an empty pile."""
        self.cards: list[Card] = []

    def add_card(self, card: Card, face_up: bool = True):
        """
        Adds a card to the top of the pile.

        Args:
            card: The Card object to add.
            face_up: Whether the card should be face up.
        """
        if not isinstance(card, Card):
            raise TypeError("Only Card objects can be added to a pile.")
        card.is_face_up = face_up
        self.cards.append(card)

    def remove_card(self) -> Card | None:
        """
        Removes and returns the top card from the pile.

        Returns:
            The top card, or None if the pile is empty.
        """
        if self.cards:
            return self.cards.pop()
        return None

    def view_top_card(self) -> Card | None:
        """
        Returns the top card without removing it.

        Returns:
            The top card, or None if the pile is empty.
        """
        if self.cards:
            return self.cards[-1]
        return None

    def is_empty(self) -> bool:
        """Returns True if the pile has no cards."""
        return len(self.cards) == 0

    def __str__(self) -> str:
        """Returns a simple string representation of the pile."""
        if self.is_empty():
            return "[ ]"
        return f"Pile with {len(self.cards)} cards. Top: {self.view_top_card()}"

class TableauPile(Pile):
    """Represents a tableau pile in Klondike Solitaire."""
    def __init__(self):
        super().__init__()

    def can_add_card(self, card: Card) -> bool:
        """
        Checks if a card can be added to this tableau pile.
        A card can be added if the pile is empty and the card is a King.
        Or, if the pile is not empty, the card being added must be of the
        opposite color and one rank lower than the current top card (which must be face-up).
        """
        if not isinstance(card, Card):
            return False
        if self.is_empty():
            return card.rank == "K"
        else:
            top_card = self.view_top_card()
            if top_card and top_card.is_face_up:
                return card.color != top_card.color and card.value == top_card.value - 1
            return False

    def add_card(self, card: Card, face_up: bool = True) -> bool: # Modified to accept face_up and return bool
        """
        Adds a card to the tableau pile if the move is valid.
        The card will be face-up if added.

        Args:
            card: The Card object to add.
            face_up: Whether the card should be added face up. (Usually True for tableau)

        Returns:
            True if the card was added, False otherwise.
        """
        if self.can_add_card(card):
            card.is_face_up = face_up # Set face_up status
            super().add_card(card, face_up=card.is_face_up)
            return True
        return False

    def reveal_top_card(self):
        """If the top card is face-down, turns it face-up."""
        top_card = self.view_top_card()
        if top_card and not top_card.is_face_up:
            top_card.is_face_up = True

    def __str__(self) -> str:
        """
        Returns a string representation of the tableau pile.
        Example: "[ ] [ ] QH JH TH"
        """
        if self.is_empty():
            return "[ ]"
        
        return " ".join([str(card) for card in self.cards])


class FoundationPile(Pile):
    """Represents a foundation pile in Klondike Solitaire."""
    def __init__(self, suit: str):
        """
        Initializes an empty foundation pile for a specific suit.

        Args:
            suit: The suit this foundation pile accepts (e.g., "Hearts").
        """
        super().__init__()
        if suit not in Deck.SUITS:
            raise ValueError(f"Invalid suit for foundation pile: {suit}")
        self.suit = suit

    def can_add_card(self, card: Card) -> bool:
        """
        Checks if a card can be added to this foundation pile.
        A card can be added if it's an Ace of the correct suit and the pile is empty.
        Or, if the pile is not empty, the card must be of the same suit and one
        rank higher than the current top card.
        """
        if not isinstance(card, Card) or card.suit != self.suit:
            return False
        
        if self.is_empty():
            return card.rank == "A"
        else:
            top_card = self.view_top_card()
            if top_card: 
                return card.value == top_card.value + 1
            return False 

    def add_card(self, card: Card) -> bool: # Modified to return bool
        """
        Adds a card to the foundation pile if the move is valid.
        Cards in a foundation pile are always face-up.

        Args:
            card: The Card object to add.

        Returns:
            True if the card was added, False otherwise.
        """
        if self.can_add_card(card):
            super().add_card(card, face_up=True) # All cards in foundation are face-up
            return True
        return False

    def __str__(self) -> str:
        """
        Returns a string representation of the foundation pile.
        Displays the top card or "[ ]" if empty. E.g., "KH" or "[ ]".
        """
        top_card = self.view_top_card()
        if top_card:
            return str(top_card)
        return f"[{self.suit[0]}]" # Display empty foundation with suit hint

class StockPile(Pile):
    """Represents the stock pile in Klondike Solitaire."""
    def __init__(self):
        super().__init__()

    def add_card(self, card: Card, face_up: bool = False):
        """
        Adds a card to the stock pile, typically face-down.
        """
        super().add_card(card, face_up=face_up)

    def deal_to_waste(self, waste_pile: 'WastePile', number_of_cards: int = 1):
        """
        Moves a specified number of cards from stock to the waste pile.
        Cards moved to the waste pile become face-up.

        Args:
            waste_pile: The WastePile object to deal cards to.
            number_of_cards: The number of cards to deal.
        """
        if not isinstance(waste_pile, WastePile):
            raise TypeError("Can only deal to a WastePile.")
        for _ in range(number_of_cards):
            if self.is_empty():
                break 
            card = self.remove_card()
            if card: 
                waste_pile.add_card(card, face_up=True)


class WastePile(Pile):
    """Represents the waste pile in Klondike Solitaire."""
    def __init__(self):
        super().__init__()

    def add_card(self, card: Card, face_up: bool = True):
        """
        Adds a card to the waste pile. Cards in the waste pile are always face-up.
        """
        if not isinstance(card, Card):
            raise TypeError("Only Card objects can be added to a pile.")
        super().add_card(card, face_up=True)


    def __str__(self) -> str:
        """
        Returns a string representation of the waste pile.
        Displays the top card or "[ ]" if empty.
        """
        top_card = self.view_top_card()
        if top_card:
            return str(top_card) 
        return "[ ]"

class GameState:
    """Manages the overall state of the Klondike Solitaire game."""
    def __init__(self):
        """Initializes the game with a shuffled deck and sets up all piles."""
        self.deck = Deck()
        self.tableau_piles: list[TableauPile] = [TableauPile() for _ in range(7)]
        self.foundation_piles: list[FoundationPile] = [FoundationPile(suit) for suit in Deck.SUITS]
        self.stock_pile = StockPile()
        self.waste_pile = WastePile()
        self.deal_initial_cards()

    def deal_initial_cards(self):
        """Deals cards from the deck to the tableau and stock piles."""
        # Deal to tableau piles
        for i in range(7):
            for j in range(i + 1):
                card = self.deck.deal()
                if card:
                    # Last card in each tableau pile is face up, others face down
                    is_face_up = (j == i)
                    # TableauPile.add_card expects a Card, and will set its face_up status based on its own logic
                    # We need to set it on the card first, then use the base Pile.add_card
                    card.is_face_up = is_face_up
                    self.tableau_piles[i].cards.append(card) # Directly add, bypassing TableauPile.add_card logic for setup
                else:
                    # Should not happen with a standard 52 card deck
                    raise Exception("Deck ran out of cards prematurely during initial deal.")

        # Remaining cards go to stock pile, face down
        while not self.deck.is_empty():
            card = self.deck.deal()
            if card:
                self.stock_pile.add_card(card, face_up=False)
            else: # Should not happen
                break

    def draw_from_stock(self, number_of_cards: int = 1):
        """
        Moves card(s) from StockPile to WastePile.
        If StockPile is empty, resets it from WastePile.
        """
        if self.stock_pile.is_empty():
            self.reset_stock_from_waste()
        else:
            self.stock_pile.deal_to_waste(self.waste_pile, number_of_cards)

    def reset_stock_from_waste(self):
        """
        Moves all cards from WastePile back to StockPile, face-down.
        Cards are transferred one by one from top of waste to top of stock.
        """
        while not self.waste_pile.is_empty():
            card = self.waste_pile.remove_card()
            if card:
                self.stock_pile.add_card(card, face_up=False)
        # The original order is reversed, to match standard Klondike rules where stock is recycled in order.
        # If we want top of waste to become top of stock, and preserve order, stock should be treated as a stack.
        # Current implementation: top of waste -> top of stock (which is a stack, so effectively reversed when dealt again)
        # To preserve order for dealing:
        # temp_cards = []
        # while not self.waste_pile.is_empty():
        #    card = self.waste_pile.remove_card()
        #    if card:
        #        temp_cards.append(card)
        # for card in reversed(temp_cards): # Add back in original order, top of waste is top of new stock
        #    self.stock_pile.add_card(card, face_up=False)


    def move_waste_to_foundation(self, foundation_idx: int) -> bool:
        """
        Tries to move the top card from WastePile to a FoundationPile.
        Returns True on success, False otherwise.
        """
        if not (0 <= foundation_idx < len(self.foundation_piles)):
            # print(f"Error: Invalid foundation index {foundation_idx}")
            return False
        
        waste_card = self.waste_pile.view_top_card()
        if not waste_card:
            # print("Error: Waste pile is empty.")
            return False
            
        foundation = self.get_foundation_pile(foundation_idx)
        if foundation.add_card(waste_card): # add_card checks rules
            self.waste_pile.remove_card() # Remove from waste if successfully added
            return True
        # print(f"Error: Cannot add {waste_card} to foundation {foundation_idx}.")
        return False

    def move_tableau_to_foundation(self, tableau_idx: int, foundation_idx: int) -> bool:
        """
        Tries to move the top card from a TableauPile to a FoundationPile.
        Reveals the new top card of the TableauPile if the move is successful.
        Returns True on success, False otherwise.
        """
        if not (0 <= tableau_idx < len(self.tableau_piles)):
            # print(f"Error: Invalid tableau index {tableau_idx}")
            return False
        if not (0 <= foundation_idx < len(self.foundation_piles)):
            # print(f"Error: Invalid foundation index {foundation_idx}")
            return False

        tableau = self.get_tableau_pile(tableau_idx)
        if tableau.is_empty():
            # print(f"Error: Tableau pile {tableau_idx} is empty.")
            return False
            
        tableau_card = tableau.view_top_card()
        if not tableau_card or not tableau_card.is_face_up: # Card must be face up
             # print(f"Error: Top card of tableau {tableau_idx} is face down or pile is empty.")
            return False

        foundation = self.get_foundation_pile(foundation_idx)
        if foundation.add_card(tableau_card):
            tableau.remove_card()
            tableau.reveal_top_card() # Reveal new top card if any
            return True
        # print(f"Error: Cannot add {tableau_card} from tableau {tableau_idx} to foundation {foundation_idx}.")
        return False

    def move_waste_to_tableau(self, tableau_idx: int) -> bool:
        """
        Tries to move the top card from WastePile to a TableauPile.
        Returns True on success, False otherwise.
        """
        if not (0 <= tableau_idx < len(self.tableau_piles)):
            # print(f"Error: Invalid tableau index {tableau_idx}")
            return False
        
        waste_card = self.waste_pile.view_top_card()
        if not waste_card:
            # print("Error: Waste pile is empty.")
            return False

        tableau = self.get_tableau_pile(tableau_idx)
        if tableau.add_card(waste_card): # add_card checks rules and sets face_up=True
            self.waste_pile.remove_card()
            return True
        # print(f"Error: Cannot add {waste_card} to tableau {tableau_idx}.")
        return False

    def move_tableau_to_tableau(self, source_tableau_idx: int, dest_tableau_idx: int, num_cards: int = 1) -> bool:
        """
        Moves a stack of `num_cards` from one TableauPile to another.
        The cards moved must be face-up.
        Reveals the new top card of the source TableauPile if the move is successful.
        Returns True on success, False otherwise.
        """
        if not (0 <= source_tableau_idx < len(self.tableau_piles)) or \
           not (0 <= dest_tableau_idx < len(self.tableau_piles)) or \
           source_tableau_idx == dest_tableau_idx:
            # print(f"Error: Invalid source or destination tableau index.")
            return False
        if num_cards <= 0:
            # print(f"Error: Number of cards to move must be positive.")
            return False

        source_pile = self.get_tableau_pile(source_tableau_idx)
        dest_pile = self.get_tableau_pile(dest_tableau_idx)

        # Identify the stack of cards to move
        if len(source_pile.cards) < num_cards:
            # print(f"Error: Source tableau {source_tableau_idx} does not have {num_cards} cards.")
            return False

        # Cards to be moved are the last `num_cards` cards in the source pile
        moving_stack = source_pile.cards[-num_cards:]
        
        # Check if all cards in the moving stack are face-up
        for card_in_stack in moving_stack:
            if not card_in_stack.is_face_up:
                # print(f"Error: Not all cards in the moving stack from tableau {source_tableau_idx} are face-up.")
                return False
        
        # The card that will connect to the destination pile is the first card of the moving stack
        card_to_check = moving_stack[0]

        if dest_pile.can_add_card(card_to_check):
            # Temporarily remove cards from source to avoid issues if they are added back
            source_pile.cards = source_pile.cards[:-num_cards]
            
            # Add cards to destination pile
            for card_in_stack in moving_stack:
                # We use super().add_card here for TableauPile, because TableauPile's add_card only adds one card
                # and checks can_add_card based on that single card. Here, we've already validated the whole stack.
                # The cards are already correctly face_up.
                dest_pile.cards.append(card_in_stack)

            source_pile.reveal_top_card() # Reveal new top card of source
            return True
        
        # print(f"Error: Cannot move stack from tableau {source_tableau_idx} to tableau {dest_tableau_idx}.")
        return False

    def check_win_condition(self) -> bool:
        """Returns True if all 52 cards are in the FoundationPiles."""
        total_foundation_cards = sum(len(fp.cards) for fp in self.foundation_piles)
        return total_foundation_cards == 52

    def get_tableau_pile(self, idx: int) -> TableauPile:
        """Returns the TableauPile at the given index."""
        if 0 <= idx < len(self.tableau_piles):
            return self.tableau_piles[idx]
        raise IndexError(f"Tableau pile index {idx} out of range.")

    def get_foundation_pile(self, idx: int) -> FoundationPile:
        """Returns the FoundationPile at the given index."""
        if 0 <= idx < len(self.foundation_piles):
            return self.foundation_piles[idx]
        raise IndexError(f"Foundation pile index {idx} out of range.")

    def display_board(self) -> str:
        """Returns a string representation of the game board."""
        # Foundations
        found_str = "Foundations: " + " ".join([str(fp) for fp in self.foundation_piles])
        
        # Stock and Waste
        stock_str = f"Stock: {len(self.stock_pile.cards)} cards"
        waste_str = f"Waste: {self.waste_pile}"
        
        # Tableaus
        tableau_strs = ["Tableau:"]
        max_lines = 0
        tableau_card_cols = [] # list of lists of strings

        for i, tp in enumerate(self.tableau_piles):
            col_cards = [str(card) for card in tp.cards]
            tableau_card_cols.append(col_cards)
            if len(col_cards) > max_lines:
                max_lines = len(col_cards)
        
        # Header for tableau columns
        header = "  ".join([f"{i+1:^3}" for i in range(len(self.tableau_piles))]) # Centered, 3 chars wide
        tableau_strs.append(header)
        tableau_strs.append("-" * len(header))


        for line_idx in range(max_lines):
            line_parts = []
            for col_idx in range(len(self.tableau_piles)):
                if line_idx < len(tableau_card_cols[col_idx]):
                    line_parts.append(f"{tableau_card_cols[col_idx][line_idx]:^3}") # Centered, 3 chars wide
                else:
                    line_parts.append("   ") # Empty space, 3 chars wide
            tableau_strs.append("  ".join(line_parts))
            
        return f"{found_str}\n{stock_str}   {waste_str}\n\n" + "\n".join(tableau_strs)

    def __str__(self) -> str:
        """Provides a string representation of the game state, primarily for debugging."""
        return self.display_board()

# Example Usage (Optional - for testing)
if __name__ == '__main__':
    game = GameState()
    print(game.display_board())

    # Example moves (uncomment to test)
    # game.draw_from_stock()
    # print("\nAfter drawing from stock:")
    # print(game.display_board())

    # game.move_waste_to_tableau(0) # Try to move from waste to first tableau
    # print("\nAfter attempting to move waste to tableau 0:")
    # print(game.display_board())

    # # Test moving a King to an empty tableau spot (assuming one is available or made available)
    # # This requires finding a King in waste or another tableau and an empty tableau.
    # # Example: if waste has King and tableau 0 is empty:
    # # if game.waste_pile.view_top_card() and game.waste_pile.view_top_card().rank == "K" and game.tableau_piles[0].is_empty():
    # #    game.move_waste_to_tableau(0)
    # #    print(game.display_board())
    
    # # Test moving from tableau to foundation (e.g. an Ace)
    # # This requires an Ace to be on top of a tableau pile.
    # # Example: if tableau_piles[0].view_top_card() is an Ace of Hearts
    # # if game.tableau_piles[0].view_top_card() and game.tableau_piles[0].view_top_card().rank == "A":
    # #    target_foundation_idx = -1
    # #    for idx, fp in enumerate(game.foundation_piles):
    # #        if fp.suit == game.tableau_piles[0].view_top_card().suit:
    # #            target_foundation_idx = idx
    # #            break
    # #    if target_foundation_idx != -1:
    # #        game.move_tableau_to_foundation(0, target_foundation_idx)
    # #        print(game.display_board())

    # # Test tableau to tableau move
    # # Example: move 1 card from tableau 1 to tableau 0
    # # This requires tableau 1 to have a movable card and tableau 0 to be able to accept it
    # # game.move_tableau_to_tableau(source_tableau_idx=1, dest_tableau_idx=0, num_cards=1)
    # # print(game.display_board())
    
    # # Win condition check
    # # print(f"\nGame won? {game.check_win_condition()}")
