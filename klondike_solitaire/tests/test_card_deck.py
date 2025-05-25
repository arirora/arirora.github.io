import unittest
from klondike_solitaire.game_logic import Card, Deck

class TestCardDeck(unittest.TestCase):

    def test_card_creation(self):
        """Test basic card properties."""
        card1 = Card("Hearts", "A", is_face_up=True)
        self.assertEqual(card1.suit, "Hearts")
        self.assertEqual(card1.rank, "A")
        self.assertEqual(card1.value, 1, "Ace value should be 1")
        self.assertEqual(card1.color, "Red")
        self.assertTrue(card1.is_face_up)
        self.assertEqual(str(card1), "AH", "Face-up Ace of Hearts string rep")

        card2 = Card("Spades", "K")
        self.assertEqual(card2.suit, "Spades")
        self.assertEqual(card2.rank, "K")
        self.assertEqual(card2.value, 13, "King value should be 13")
        self.assertEqual(card2.color, "Black")
        self.assertFalse(card2.is_face_up, "Card should be face-down by default")
        self.assertEqual(str(card2), "[ ]", "Face-down card string rep")

        card3 = Card("Diamonds", "7", is_face_up=True)
        self.assertEqual(card3.value, 7, "7 of Diamonds value should be 7")
        self.assertEqual(card3.color, "Red")
        self.assertEqual(str(card3), "7D")
        
        card4 = Card("Clubs", "10")
        self.assertEqual(card4.value, 10)
        self.assertEqual(card4.color, "Black")
        self.assertEqual(str(card4), "[ ]")

        with self.assertRaises(ValueError, msg="Invalid suit should raise ValueError"):
            Card("Stars", "5")
        with self.assertRaises(ValueError, msg="Invalid rank should raise ValueError"):
            Card("Hearts", "11")

    def test_deck_creation_and_dealing(self):
        """Test deck initialization, card count, and dealing."""
        deck = Deck()
        self.assertEqual(len(deck.cards), 52, "Deck should have 52 cards upon creation")

        dealt_cards = []
        for _ in range(52):
            card = deck.deal()
            self.assertIsNotNone(card, "Dealing from a non-empty deck should return a Card")
            self.assertIsInstance(card, Card)
            dealt_cards.append(str(card)) # Use string representation for uniqueness check

        self.assertEqual(len(dealt_cards), 52, "Should have dealt 52 cards")
        self.assertEqual(len(set(dealt_cards)), 52, "All 52 dealt cards should be unique")
        self.assertTrue(deck.is_empty(), "Deck should be empty after dealing all cards")
        self.assertEqual(len(deck.cards), 0, "Deck.cards list should be empty")

        self.assertIsNone(deck.deal(), "Dealing from an empty deck should return None")

    def test_deck_shuffling(self):
        """Test that the deck is shuffled."""
        deck1 = Deck()
        deck1_card_order = [str(card) for card in deck1.cards] # Relies on current Deck implementation

        # Create a representation of an ordered deck (before shuffle)
        # This is a bit tricky because Deck auto-shuffles.
        # So, we'll create our own ordered list of what card strings should be in a deck.
        ordered_card_strings = []
        for suit in Deck.SUITS:
            for rank in Deck.RANKS:
                # Card created for string representation doesn't need to be face up for this test
                ordered_card_strings.append(str(Card(suit, rank, is_face_up=True))) 
                                            # Using True for face_up to get "RankSuit" string

        # Get cards from a newly created (and thus auto-shuffled) deck
        deck2 = Deck()
        deck2_cards_dealt_strings = []
        # Deal all cards and record their string representations
        # We need to make them face-up to compare with ordered_card_strings
        for _ in range(52):
            card = deck2.deal()
            if card:
                card.is_face_up = True # Ensure consistent string format for comparison
                deck2_cards_dealt_strings.append(str(card))
        
        # Check that all unique cards are present
        self.assertEqual(len(deck2_cards_dealt_strings), 52, "Shuffled deck must deal 52 cards.")
        self.assertEqual(len(set(deck2_cards_dealt_strings)), 52, "Shuffled deck must contain 52 unique cards.")
        
        # Check that the order is different from a known ordered sequence
        # This has a very small chance of failing if shuffle results in original order.
        # A more robust test might check if a certain percentage of cards are out of place.
        if set(deck2_cards_dealt_strings) == set(ordered_card_strings): # Ensure sets are comparable
             self.assertNotEqual(deck2_cards_dealt_strings, ordered_card_strings,
                                "Shuffled deck order should be different from a non-shuffled deck.")
        else:
            self.fail("Shuffled deck and reference ordered deck do not contain the same set of cards for comparison.")


        # Test that two different Deck instances are likely shuffled differently.
        deck3 = Deck()
        deck3_card_order = [str(card) for card in deck3.cards] # Cards are initially face-down in deck.cards

        # This test has a probabilistic chance of failure if two shuffles produce the same order.
        # For a 52-card deck, this is astronomically unlikely.
        # Comparing deck1.cards and deck3.cards (which are still in the deck, not dealt)
        self.assertNotEqual(deck1_card_order, deck3_card_order,
                            "Two separate deck instances should have different shuffles (highly probable).")
        
        # Ensure all cards are still present and unique in deck1 after getting its order
        self.assertEqual(len(set(str(c) for c in deck1.cards)), 52, "Deck1 must still contain 52 unique cards.")


if __name__ == '__main__':
    unittest.main()
