import unittest
from klondike_solitaire.game_logic import Card, Pile, TableauPile, FoundationPile, StockPile, WastePile, Deck

class TestPiles(unittest.TestCase):

    def test_pile_base_class(self):
        """Test basic Pile class functionality."""
        pile = Pile()
        self.assertTrue(pile.is_empty(), "New pile should be empty")
        self.assertEqual(len(pile.cards), 0)
        self.assertIsNone(pile.view_top_card(), "Viewing top card of empty pile should be None")
        self.assertIsNone(pile.remove_card(), "Removing card from empty pile should be None")

        card1 = Card("Hearts", "A")
        pile.add_card(card1)
        self.assertFalse(pile.is_empty(), "Pile should not be empty after adding a card")
        self.assertEqual(len(pile.cards), 1)
        self.assertIs(pile.view_top_card(), card1, "Top card should be card1")
        self.assertTrue(card1.is_face_up, "Card added to generic pile should be face up by default")

        card2 = Card("Spades", "K", is_face_up=False)
        pile.add_card(card2, face_up=False) # Explicitly add face down
        self.assertEqual(len(pile.cards), 2)
        self.assertIs(pile.view_top_card(), card2, "Top card should be card2")
        self.assertFalse(card2.is_face_up, "Card2 should be face down")
        
        removed_card = pile.remove_card()
        self.assertIs(removed_card, card2, "Removed card should be card2")
        self.assertEqual(len(pile.cards), 1)
        self.assertIs(pile.view_top_card(), card1, "Top card should now be card1")

        removed_card = pile.remove_card()
        self.assertIs(removed_card, card1, "Removed card should be card1")
        self.assertTrue(pile.is_empty(), "Pile should be empty after removing all cards")
        
        with self.assertRaises(TypeError, msg="Adding non-Card object should raise TypeError"):
            pile.add_card("not a card")

    def test_tableau_pile(self):
        """Test TableauPile specific logic."""
        tp = TableauPile()
        king_h = Card("Hearts", "K")
        queen_s = Card("Spades", "Q")
        queen_h = Card("Hearts", "Q")
        jack_d = Card("Diamonds", "J")
        jack_c = Card("Clubs", "J") # Same rank, diff color from jack_d
        ten_s = Card("Spades", "10")

        # Test adding King to empty tableau
        self.assertTrue(tp.can_add_card(king_h), "Should be able to add King to empty tableau")
        self.assertTrue(tp.add_card(king_h), "Adding King to empty tableau should succeed")
        self.assertTrue(king_h.is_face_up, "King added to tableau should be face up")
        self.assertEqual(str(tp), "KH", "Tableau with King of Hearts")

        # Test adding Queen of Spades (opposite color, rank-1)
        self.assertTrue(tp.can_add_card(queen_s), "Should be able to add QS to KH")
        self.assertTrue(tp.add_card(queen_s), "Adding QS to KH should succeed")
        self.assertTrue(queen_s.is_face_up, "QS added to tableau should be face up")
        self.assertEqual(str(tp), "KH QS", "Tableau string representation")

        # Test invalid: Queen of Hearts (same color)
        self.assertFalse(tp.can_add_card(queen_h), "Should not add QH (same color) to QS")
        self.assertFalse(tp.add_card(queen_h), "Adding QH to QS should fail")

        # Test valid: Jack of Diamonds (opposite color, rank-1)
        self.assertTrue(tp.can_add_card(jack_d), "Should be able to add JD to QS")
        self.assertTrue(tp.add_card(jack_d), "Adding JD to QS should succeed")
        self.assertEqual(str(tp), "KH QS JD")

        # Test invalid: Jack of Clubs (same rank as JD)
        self.assertFalse(tp.can_add_card(jack_c), "Should not add JC (same rank) to JD")
        
        # Test invalid: Ten of Spades (same color as JD, but rank is ok for JD)
        # This is tricky: JD is red. TS is black. This should be valid.
        self.assertTrue(tp.can_add_card(ten_s), "Should be able to add 10S to JD")
        self.assertTrue(tp.add_card(ten_s), "Adding 10S to JD should succeed")
        self.assertEqual(str(tp), "KH QS JD 10S")

        # Test reveal_top_card
        tp.cards = [] # Reset
        card_down = Card("Clubs", "5", is_face_up=False)
        card_up = Card("Hearts", "4", is_face_up=True)
        tp.cards.append(card_down)
        tp.cards.append(card_up) # Manually add to test reveal
        
        tp.remove_card() # Remove card_up
        self.assertTrue(card_down.is_face_up, "Removing top card should reveal (turn face-up) the new top card if it was face-down")
        
        # Test adding to empty tableau with non-king
        tp2 = TableauPile()
        self.assertFalse(tp2.can_add_card(queen_s), "Cannot add non-King to empty tableau")
        self.assertFalse(tp2.add_card(queen_s), "Adding non-King to empty tableau should fail")

        # Test __str__ with face down cards
        tp3 = TableauPile()
        tp3.add_card(Card("Spades", "K")) # KS
        # Manually add face-down cards to simulate initial deal for __str__
        # Note: GameState.deal_initial_cards sets this up, TableauPile.add_card always makes cards face up
        # So we add directly to cards list for this specific string test
        tp3.cards = []
        tp3.cards.append(Card("Diamonds", "2", is_face_up=False))
        tp3.cards.append(Card("Clubs", "3", is_face_up=False))
        tp3.cards.append(Card("Hearts", "4", is_face_up=True))
        # Expected: "[ ] [ ] 4H" based on GameState.display_board logic for individual piles
        # The current TableauPile.__str__ is " [ ] [ ] 4H" based on card string reps.
        # Let's align with how Card.__str__ for face down is "[ ]"
        self.assertEqual(str(tp3), "[ ] [ ] 4H", "Tableau string with leading face-down cards")
        
        tp4 = TableauPile()
        tp4.cards.append(Card("Diamonds", "2", is_face_up=False))
        self.assertEqual(str(tp4), "[ ]")

    def test_foundation_pile(self):
        """Test FoundationPile specific logic."""
        fp_h = FoundationPile("Hearts")
        ace_h = Card("Hearts", "A")
        two_h = Card("Hearts", "2")
        three_h = Card("Hearts", "3")
        ace_s = Card("Spades", "A")
        two_s = Card("Spades", "2")

        self.assertEqual(fp_h.suit, "Hearts")
        self.assertEqual(str(fp_h), "[H]", "Empty Hearts foundation string")

        # Test adding Ace to empty foundation
        self.assertTrue(fp_h.can_add_card(ace_h), "Should be able to add Ace of Hearts to empty Hearts foundation")
        self.assertTrue(fp_h.add_card(ace_h), "Adding Ace of Hearts should succeed")
        self.assertTrue(ace_h.is_face_up, "Card in foundation should be face up")
        self.assertEqual(str(fp_h), "AH", "Foundation with Ace of Hearts")

        # Test invalid: Ace of Spades (wrong suit)
        self.assertFalse(fp_h.can_add_card(ace_s), "Should not add Ace of Spades to Hearts foundation")
        self.assertFalse(fp_h.add_card(ace_s), "Adding Ace of Spades should fail")

        # Test adding Two of Hearts (correct suit, rank+1)
        self.assertTrue(fp_h.can_add_card(two_h), "Should be able to add 2H to AH")
        self.assertTrue(fp_h.add_card(two_h), "Adding 2H to AH should succeed")
        self.assertEqual(str(fp_h), "2H")

        # Test invalid: Two of Spades (wrong suit)
        self.assertFalse(fp_h.can_add_card(two_s), "Should not add 2S to Hearts foundation")

        # Test invalid: Ace of Hearts again (wrong rank - not +1)
        self.assertFalse(fp_h.can_add_card(ace_h), "Should not add AH again to 2H")

        # Test adding Three of Hearts
        self.assertTrue(fp_h.can_add_card(three_h), "Should be able to add 3H to 2H")
        self.assertTrue(fp_h.add_card(three_h), "Adding 3H to 2H should succeed")
        self.assertEqual(str(fp_h), "3H")

        # Test adding to empty foundation with non-Ace
        fp_s = FoundationPile("Spades")
        self.assertFalse(fp_s.can_add_card(two_s), "Cannot add non-Ace to empty foundation")
        self.assertFalse(fp_s.add_card(two_s), "Adding non-Ace to empty foundation should fail")
        
        with self.assertRaises(ValueError, msg="Invalid suit for foundation should raise ValueError"):
            FoundationPile("InvalidSuit")

    def test_stock_pile_and_waste_pile(self):
        """Test StockPile and WastePile interactions."""
        stock = StockPile()
        waste = WastePile()

        card1 = Card("Clubs", "10")
        card2 = Card("Diamonds", "J")
        card3 = Card("Spades", "Q")

        # Add cards to stock (should be face-down by default in StockPile.add_card)
        stock.add_card(card1) # Default face_down=False but StockPile.add_card forces it
        stock.add_card(card2)
        stock.add_card(card3)
        
        self.assertFalse(card1.is_face_up, "Card1 in stock should be face down")
        self.assertFalse(card2.is_face_up, "Card2 in stock should be face down")
        self.assertFalse(card3.is_face_up, "Card3 in stock should be face down")
        self.assertEqual(len(stock.cards), 3)

        # Test deal_to_waste
        stock.deal_to_waste(waste, 1)
        self.assertEqual(len(stock.cards), 2, "Stock should have 2 cards after dealing 1 to waste")
        self.assertEqual(len(waste.cards), 1, "Waste should have 1 card")
        self.assertIs(waste.view_top_card(), card3, "Card3 should be on top of waste")
        self.assertTrue(card3.is_face_up, "Card moved from stock to waste should become face-up")
        self.assertEqual(str(waste), "QS")

        stock.deal_to_waste(waste, 1)
        self.assertEqual(len(stock.cards), 1)
        self.assertEqual(len(waste.cards), 2)
        self.assertIs(waste.view_top_card(), card2)
        self.assertTrue(card2.is_face_up)
        self.assertEqual(str(waste), "JD") # Waste shows its top card

        # Test WastePile adding ensures face-up
        card_for_waste = Card("Hearts", "A", is_face_up=False)
        waste.add_card(card_for_waste)
        self.assertTrue(card_for_waste.is_face_up, "Card added to waste directly should be face-up")
        self.assertEqual(str(waste), "AH")
        
        # Test dealing more cards than available from stock
        stock.deal_to_waste(waste, 5) # Stock has 1 card (card1)
        self.assertTrue(stock.is_empty(), "Stock should be empty after trying to deal more cards than available")
        self.assertEqual(len(waste.cards), 4) # card3, card2, card_for_waste, card1
        self.assertIs(waste.view_top_card(), card1, "Card1 should now be on top of waste")
        self.assertTrue(card1.is_face_up)
        
        # Test dealing from empty stock
        stock.deal_to_waste(waste, 1) # Stock is empty
        self.assertEqual(len(waste.cards), 4, "Dealing from empty stock should not change waste pile")

        # Test __str__ for empty waste
        empty_waste = WastePile()
        self.assertEqual(str(empty_waste), "[ ]")

if __name__ == '__main__':
    unittest.main()
