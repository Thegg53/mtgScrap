"""mtgscrap.deck - Deck scraping and export utilities."""
from mtgscrap.deck.goldfish import MinimalDeck, scrape_meta
from mtgscrap.deck.export import export_decks_to_csv

__all__ = ["MinimalDeck", "scrape_meta", "export_decks_to_csv"]
