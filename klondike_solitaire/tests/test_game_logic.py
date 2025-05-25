import unittest
from klondike_solitaire.game_logic import GameState, Card, Deck, TableauPile, FoundationPile, WastePile, StockPile

class TestGameState(unittest.TestCase):

    def setUp(self):
        """Setup for each test method."""
        self.game = GameState()

    def test_initialization(self):
        """Test the game state is initialized correctly."""
        self.assertEqual(len(self.game.tableau_piles), 7, "Should have 7 tableau piles")
        self.assertEqual(len(self.game.foundation_piles), 4, "Should have 4 foundation piles")
        self.assertIsInstance(self.game.stock_pile, StockPile, "Stock pile should be a StockPile instance")
        self.assertIsInstance(self.game.waste_pile, WastePile, "Waste pile should be a WastePile instance")
        self.assertIsInstance(self.game.deck, Deck, "Deck should be a Deck instance (though it's emptied into stock)")

        # Check tableau pile setup
        for i, pile in enumerate(self.game.tableau_piles):
            self.assertEqual(len(pile.cards), i + 1, f"Tableau pile {i+1} should have {i+1} cards")
            self.assertTrue(pile.cards[-1].is_face_up, f"Top card of tableau pile {i+1} should be face up")
            for j in range(i): # Cards below the top card
                 self.assertFalse(pile.cards[j].is_face_up, f"Card {j+1} of tableau pile {i+1} should be face down")
        
        # Check stock pile count (52 total cards - 28 in tableau = 24 in stock)
        self.assertEqual(len(self.game.stock_pile.cards), 24, "Stock should have 24 cards after initial deal")
        if self.game.stock_pile.cards: # If stock is not empty
            for card in self.game.stock_pile.cards:
                self.assertFalse(card.is_face_up, "Cards in stock should be face down")
        
        # Check foundation piles are empty and have correct suits
        expected_suits = sorted(Deck.SUITS)
        found_suits = sorted([fp.suit for fp in self.game.foundation_piles])
        self.assertEqual(found_suits, expected_suits, "Foundation piles should have one for each suit")
        for fp in self.game.foundation_piles:
            self.assertTrue(fp.is_empty(), f"Foundation pile for {fp.suit} should be empty initially")

        # Check waste pile is empty
        self.assertTrue(self.game.waste_pile.is_empty(), "Waste pile should be empty initially")

    def test_draw_from_stock(self):
        """Test drawing cards from stock to waste, and resetting stock."""
        initial_stock_size = len(self.game.stock_pile.cards)
        
        # Draw one card
        if initial_stock_size > 0:
            self.game.draw_from_stock()
            self.assertEqual(len(self.game.stock_pile.cards), initial_stock_size - 1, "Stock size should decrease by 1")
            self.assertEqual(len(self.game.waste_pile.cards), 1, "Waste size should increase to 1")
            self.assertTrue(self.game.waste_pile.view_top_card().is_face_up, "Card in waste should be face up")
        else:
            # Stock starts empty - this shouldn't happen with standard deal
            self.game.draw_from_stock() # Should try to reset if waste has cards
            self.assertEqual(len(self.game.waste_pile.cards), 0)


        # Draw all cards from stock
        num_stock_cards = len(self.game.stock_pile.cards) # after one draw
        for _ in range(num_stock_cards):
            self.game.draw_from_stock()
        
        self.assertTrue(self.game.stock_pile.is_empty(), "Stock should be empty after drawing all cards")
        self.assertEqual(len(self.game.waste_pile.cards), initial_stock_size, 
                         f"Waste should have {initial_stock_size} cards after drawing all from stock")

        # Test reset stock from waste
        # Now stock is empty, waste has initial_stock_size cards.
        # Top card of waste before reset (for order check)
        waste_cards_before_reset = [c for c in self.game.waste_pile.cards]
        
        self.game.draw_from_stock() # Should trigger reset
        
        self.assertEqual(len(self.game.stock_pile.cards), initial_stock_size, 
                         f"Stock should have {initial_stock_size} cards after reset")
        self.assertTrue(self.game.waste_pile.is_empty(), "Waste should be empty after reset")
        for card in self.game.stock_pile.cards:
            self.assertFalse(card.is_face_up, "Cards in stock after reset should be face down")
        
        # Check order after reset (should be reversed from waste pile's order)
        # Stock is a stack (LIFO), waste is also effectively a stack.
        # When resetting, cards are popped from waste and added to stock.
        # So, top of waste becomes bottom of stock. When stock is dealt again, it's reversed.
        # The game_logic.GameState.reset_stock_from_waste() implements this.
        # The `GameState.reset_stock_from_waste` moves cards one by one from waste.pop() to stock.add_card().
        # So the order of cards in stock.cards will be the reverse of waste_cards_before_reset.
        if initial_stock_size > 0 and waste_cards_before_reset:
             # Compare string representations as Card objects will be different instances
            stock_after_reset_strs = [str(c) for c in self.game.stock_pile.cards]
            expected_stock_strs = [str(c) for c in reversed(waste_cards_before_reset)]
            self.assertEqual(stock_after_reset_strs, expected_stock_strs, "Cards in stock should be in reversed order from waste after reset")

    def test_move_waste_to_foundation(self):
        """Test moving cards from waste to foundation."""
        # Setup: Put an Ace of Hearts on the waste pile
        ace_h = Card("Hearts", "A")
        self.game.waste_pile.add_card(ace_h) # WastePile.add_card makes it face up
        
        hearts_foundation_idx = -1
        for i, fp in enumerate(self.game.foundation_piles):
            if fp.suit == "Hearts":
                hearts_foundation_idx = i
                break
        self.assertNotEqual(hearts_foundation_idx, -1, "Hearts foundation pile not found")

        # Valid move
        self.assertTrue(self.game.move_waste_to_foundation(hearts_foundation_idx), "Valid move Ace from waste to empty Hearts foundation")
        self.assertTrue(self.game.foundation_piles[hearts_foundation_idx].view_top_card() is ace_h)
        self.assertTrue(self.game.waste_pile.is_empty())

        # Invalid move: Wrong suit
        ace_s = Card("Spades", "A")
        self.game.waste_pile.add_card(ace_s)
        self.assertFalse(self.game.move_waste_to_foundation(hearts_foundation_idx), "Invalid move: Ace of Spades to Hearts foundation")
        self.assertTrue(self.game.waste_pile.view_top_card() is ace_s, "Ace of Spades should remain on waste")

        # Invalid move: Waste is empty
        self.assertFalse(self.game.move_waste_to_foundation(hearts_foundation_idx), "Invalid move: Waste is empty")

        # Invalid move: Foundation rule (e.g. trying to put 3H on AH)
        # Foundation already has AH. Now try to move 3H from waste.
        three_h = Card("Hearts", "3")
        self.game.waste_pile.add_card(three_h)
        self.assertFalse(self.game.move_waste_to_foundation(hearts_foundation_idx), "Invalid move: 3H cannot go on AH")

    def test_move_tableau_to_foundation(self):
        """Test moving cards from tableau to foundation."""
        # Setup: Place Ace of Spades on top of a tableau pile
        ace_s = Card("Spades", "A", is_face_up=True)
        # Ensure tableau pile 0 is empty then add Ace S
        self.game.tableau_piles[0].cards = [] 
        self.game.tableau_piles[0].add_card(ace_s) # This add_card for TableauPile makes it face up.
                                                 # But TableauPile.add_card has rules, so direct add for test setup.
        self.game.tableau_piles[0].cards = [ace_s] # Simplest way to put it there for test
        ace_s.is_face_up = True


        # Find Spades foundation
        spades_foundation_idx = -1
        for i, fp in enumerate(self.game.foundation_piles):
            if fp.suit == "Spades":
                spades_foundation_idx = i
                break
        self.assertNotEqual(spades_foundation_idx, -1)

        # Valid move
        self.assertTrue(self.game.move_tableau_to_foundation(0, spades_foundation_idx), "Valid move: Ace of Spades from T0 to Spades Foundation")
        self.assertTrue(self.game.foundation_piles[spades_foundation_idx].view_top_card() is ace_s)
        self.assertTrue(self.game.tableau_piles[0].is_empty(), "Tableau pile 0 should be empty")

        # Setup for reveal card test: T1 has [KH(down), QH(up)]
        king_h_down = Card("Hearts", "K", is_face_up=False)
        queen_h_up = Card("Hearts", "Q", is_face_up=True) # This cannot go on KH for foundation
        self.game.tableau_piles[1].cards = [king_h_down, queen_h_up]
        
        # Invalid move: QH cannot go to empty Hearts foundation (needs Ace)
        hearts_foundation_idx = [i for i, fp in enumerate(self.game.foundation_piles) if fp.suit == "Hearts"][0]
        self.assertFalse(self.game.move_tableau_to_foundation(1, hearts_foundation_idx), "Invalid move: QH from T1 cannot go to empty Hearts Foundation")
        self.assertFalse(king_h_down.is_face_up, "Underlying card should not be revealed on failed move")
        
        # Valid move that reveals a card
        # Setup: T0: [2S(down), AS(up)], T1: [KS(down)]
        # Goal: move AS from T0 to Foundation, 2S on T0 should become face up.
        two_s_down = Card("Spades", "2", is_face_up=False)
        ace_s_up = Card("Spades", "A", is_face_up=True)
        self.game.tableau_piles[0].cards = [two_s_down, ace_s_up]
        # Ensure foundation for Spades is empty
        self.game.foundation_piles[spades_foundation_idx].cards = []

        self.assertTrue(self.game.move_tableau_to_foundation(0, spades_foundation_idx), "Move AS from T0 to Foundation")
        self.assertTrue(two_s_down.is_face_up, "Card 2S on T0 should now be face up")
        self.assertIs(self.game.tableau_piles[0].view_top_card(), two_s_down)


    def test_move_waste_to_tableau(self):
        """Test moving cards from waste to tableau."""
        # Setup: Waste has Queen of Spades. Tableau 0 has King of Hearts.
        queen_s = Card("Spades", "Q")
        self.game.waste_pile.add_card(queen_s) # Becomes face up
        
        king_h = Card("Hearts", "K", is_face_up=True)
        self.game.tableau_piles[0].cards = [king_h] # Setup T0 with KH

        # Valid move
        self.assertTrue(self.game.move_waste_to_tableau(0), "Valid: QS from waste to KH on T0")
        self.assertEqual(len(self.game.tableau_piles[0].cards), 2)
        self.assertIs(self.game.tableau_piles[0].view_top_card(), queen_s)
        self.assertTrue(queen_s.is_face_up) # Should be face up
        self.assertTrue(self.game.waste_pile.is_empty())

        # Invalid move: Waste has 10H, T0 has KH QS. 10H cannot go on QS.
        ten_h = Card("Hearts", "10")
        self.game.waste_pile.add_card(ten_h)
        self.assertFalse(self.game.move_waste_to_tableau(0), "Invalid: 10H from waste cannot go on QS on T0")
        self.assertIs(self.game.waste_pile.view_top_card(), ten_h) # 10H remains on waste

        # Invalid move: Tableau is empty, waste card is not King
        self.game.tableau_piles[1].cards = [] # T1 is empty
        jack_c = Card("Clubs", "J")
        self.game.waste_pile.cards = [jack_c] # Clear waste and add JC
        jack_c.is_face_up = True
        self.assertFalse(self.game.move_waste_to_tableau(1), "Invalid: JC from waste cannot go on empty T1")


    def test_move_tableau_to_tableau(self):
        """Test moving cards between tableau piles."""
        # Setup:
        # T0: [KH(up), QS(up)]
        # T1: [empty]
        # T2: [JD(up)]
        # T3: [AS(down), 2S(up)]
        king_h = Card("Hearts", "K", is_face_up=True)
        queen_s = Card("Spades", "Q", is_face_up=True)
        self.game.tableau_piles[0].cards = [king_h, queen_s]

        self.game.tableau_piles[1].cards = [] # Empty

        jack_d = Card("Diamonds", "J", is_face_up=True)
        self.game.tableau_piles[2].cards = [jack_d]
        
        ace_s_down = Card("Spades", "A", is_face_up=False)
        two_s_up = Card("Spades", "2", is_face_up=True)
        self.game.tableau_piles[3].cards = [ace_s_down, two_s_up]

        # Valid: Move QS from T0 to empty T1 (needs King, this is wrong for Tableau logic)
        # Corrected: Move QS from T0 to JD on T2 (QS is black, JD is red; Q > J) - This is also wrong, Q value is 12, J is 11.
        # Let's set up a valid one: T0: [KH], T1: [empty], T2: [QS]. Move KH from T0 to T1.
        self.game.tableau_piles[0].cards = [king_h]
        self.game.tableau_piles[1].cards = []
        self.game.tableau_piles[2].cards = [queen_s] # QS is black

        # Valid: Move King from T0 to empty T1
        self.assertTrue(self.game.move_tableau_to_tableau(0, 1, 1), "Valid: KH from T0 to empty T1")
        self.assertIs(self.game.tableau_piles[1].view_top_card(), king_h)
        self.assertTrue(self.game.tableau_piles[0].is_empty())

        # Reset: T0: [KH], T1: [empty]
        self.game.tableau_piles[0].cards = [king_h]
        self.game.tableau_piles[1].cards = []
        
        # Setup T2: [JD(up)]. T0: [KH(up)]. Goal: Move JD from T2 to KH on T0. (JD is red, KH is red - invalid)
        # Setup T2: [JS(up)] (Jack of Spades, black). T0: [QD(up)] (Queen of Diamonds, red). Valid.
        jack_s = Card("Spades", "J", is_face_up=True)
        queen_d = Card("Diamonds", "Q", is_face_up=True)
        self.game.tableau_piles[0].cards = [queen_d]
        self.game.tableau_piles[2].cards = [jack_s]
        
        self.assertTrue(self.game.move_tableau_to_tableau(2, 0, 1), "Valid: JS from T2 to QD on T0")
        self.assertEqual(len(self.game.tableau_piles[0].cards), 2) # QD, JS
        self.assertIs(self.game.tableau_piles[0].cards[-1], jack_s)
        self.assertTrue(self.game.tableau_piles[2].is_empty())

        # Test moving multiple cards & reveal
        # T3: [AS(down), 2S(up), AH(up)] (AH is red, 2S is black - valid stack)
        # T4: [3C(up)] (3 of Clubs, black)
        # Move [2S, AH] from T3 to T4 (2S is black, 3C is black - invalid)
        # Change T4 to [3D(up)] (3 of Diamonds, red) - then 2S on 3D is valid.
        ace_s_down = Card("Spades", "A", is_face_up=False)
        two_s_up = Card("Spades", "2", is_face_up=True)
        ace_h_up = Card("Hearts", "A", is_face_up=True) # This cannot stack on 2S.
                                                       # Stack should be: 2S (black), AR (red, value 1)
        # Valid stack: 3S(up, black), 2D(up, red), AC(up, black)
        three_s_up = Card("Spades", "3", is_face_up=True)
        two_d_up = Card("Diamonds", "2", is_face_up=True)
        ace_c_up = Card("Clubs", "A", is_face_up=True)
        
        self.game.tableau_piles[3].cards = [ace_s_down, three_s_up, two_d_up, ace_c_up]
        
        # T4: [4H(up)] (4 of Hearts, red)
        four_h_up = Card("Hearts", "4", is_face_up=True)
        self.game.tableau_piles[4].cards = [four_h_up]

        # Try to move [3S, 2D, AC] from T3 to T4 (3S on 4H)
        self.assertTrue(self.game.move_tableau_to_tableau(3, 4, 3), "Valid: Move 3 cards (3S,2D,AC) from T3 to T4 (on 4H)")
        self.assertEqual(len(self.game.tableau_piles[4].cards), 4) # 4H, 3S, 2D, AC
        self.assertIs(self.game.tableau_piles[4].cards[-1], ace_c_up)
        self.assertEqual(len(self.game.tableau_piles[3].cards), 1) # AS(down) remains
        self.assertIs(self.game.tableau_piles[3].view_top_card(), ace_s_down)
        self.assertTrue(ace_s_down.is_face_up, "AS on T3 should be revealed")

        # Invalid: Try to move face-down card (AS from T3, which is now face-up)
        # Let's make AS face-down again for this test.
        ace_s_down.is_face_up = False
        self.game.tableau_piles[3].cards = [ace_s_down] # T3 has only AS(down)
        self.game.tableau_piles[0].cards = [king_h] # T0 has KH (for a valid destination if AS was King)
        
        # Need a card that *could* go on KH if AS was King
        # This test is more about moving a stack that *contains* a face-down card.
        # T3: [KC(down), QD(up)] -> T0: [empty]
        king_c_down = Card("Clubs", "K", is_face_up=False)
        queen_d_up = Card("Diamonds", "Q", is_face_up=True)
        self.game.tableau_piles[3].cards = [king_c_down, queen_d_up]
        self.game.tableau_piles[0].cards = [] # Empty
        # Try moving 2 cards (KC, QD) where KC is face down.
        self.assertFalse(self.game.move_tableau_to_tableau(3,0,2), "Invalid: Cannot move stack starting with face-down card")


    def test_check_win_condition(self):
        """Test the win condition logic."""
        self.assertFalse(self.game.check_win_condition(), "Game should not be won at start")

        # Simulate a nearly won game - move all but one card to foundations
        # Empty all piles first for a clean slate
        self.game.stock_pile.cards = []
        self.game.waste_pile.cards = []
        for tp in self.game.tableau_piles:
            tp.cards = []
        for fp in self.game.foundation_piles:
            fp.cards = []
            
        # Populate foundations almost completely
        # Put 51 cards into foundations
        # Keep one card (e.g., King of Spades) out
        card_count = 0
        king_spades = None # Hold one card back
        
        temp_deck = Deck() # Use a temporary deck to get cards
        temp_deck.shuffle() # Ensure we get varied cards

        for suit_idx, suit in enumerate(Deck.SUITS):
            foundation = self.game.foundation_piles[suit_idx] # Assuming order matches Deck.SUITS
            self.assertEqual(foundation.suit, suit)
            for rank_idx, rank in enumerate(Deck.RANKS):
                card = temp_deck.deal() # Get a card
                while not (card.suit == suit and card.rank == rank): # Find the specific card
                    # This is inefficient, better to create cards directly
                    card = temp_deck.deal()
                    if temp_deck.is_empty() and not (card.suit == suit and card.rank == rank):
                        # If deck runs out, create the specific card we need
                        # This scenario should ideally not happen if we manage cards well.
                        # For simplicity of test, we'll just create them.
                        pass # Fall through to direct creation if needed
                
                # Create the specific card needed for foundation order
                current_card = Card(suit, rank, is_face_up=True)

                if suit == "Spades" and rank == "K": # Keep King of Spades out
                    king_spades = current_card
                    continue
                
                # Foundation add_card logic is strict, so we add directly to cards list for test setup
                foundation.cards.append(current_card)
                card_count += 1
        
        self.assertEqual(card_count, 51, "Should have 51 cards in foundations for near-win state")
        self.assertIsNotNone(king_spades, "King of Spades should be held back")
        
        self.assertFalse(self.game.check_win_condition(), "Game should not be won with 51 cards in foundations")

        # Now, add the last card (King of Spades) to its foundation
        spades_foundation = None
        for fp in self.game.foundation_piles:
            if fp.suit == "Spades":
                spades_foundation = fp
                break
        self.assertIsNotNone(spades_foundation, "Spades foundation not found for win condition test")
        
        # We can use the foundation's add_card if it's the correct next card (it is: KS on QS)
        # To be safe for test, let's assume Queen of Spades is already there.
        # Remove if any card is there from previous loop, then add QS
        if spades_foundation.cards and spades_foundation.cards[-1].rank == "K": # If KS was already added
             pass # Already there
        else: # Add it
            # Ensure QS is there first
            queen_s = Card("Spades", "Q", is_face_up=True)
            if not (spades_foundation.cards and spades_foundation.cards[-1].rank == "Q"):
                 spades_foundation.cards = [c for c in spades_foundation.cards if c.value < queen_s.value] # remove K if present
                 spades_foundation.cards.append(queen_s)


            self.assertTrue(spades_foundation.add_card(king_spades), "Adding final King of Spades should succeed")
        
        self.assertTrue(self.game.check_win_condition(), "Game should be won when all 52 cards are in foundations")


if __name__ == '__main__':
    unittest.main()
