"""
    mtgscrap.deck.export
    ~~~~~~~~~~~~~~~~~~~~
    Export deck data to CSV format.

    @author: mazz3rr

"""
from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

from mtgscrap import OUTPUT_DIR, PathLike

_log = logging.getLogger(__name__)


def export_decks_to_csv(
        decks: list, filepath: PathLike, format_filter: str = "") -> None:
    """Export a list of Deck objects to a CSV file.

    Args:
        decks: list of Deck objects to export
        filepath: destination CSV file path
        format_filter: optionally, filter to only decks matching this format (e.g., "legacy", "modern")
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = ["date", "deck_name", "format", "archetype", "author", "url", "maindeck_cards", "sideboard_cards"]
    
    filtered_decks = [d for d in decks if not format_filter or d.format.lower() == format_filter.lower()] if format_filter else decks
    
    _log.info(f"Exporting {len(filtered_decks)} decks to CSV: '{filepath}'...")
    
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for deck in filtered_decks:
            # Extract data directly from deck
            metadata = deck.metadata
            date = metadata.get("date")
            if date:
                date = date.strftime("%Y-%m-%d") if hasattr(date, "strftime") else str(date)
            
            url = metadata.get("url") or metadata.get("video_url") or ""
            
            # Format maindeck data
            maindeck_data = metadata.get("maindeck", [])
            maindeck_str = json.dumps(maindeck_data) if maindeck_data else ""
            
            # Format sideboard data
            sideboard_data = metadata.get("sideboard", [])
            sideboard_str = json.dumps(sideboard_data) if sideboard_data else ""
            
            # Handle both Archetype enum and string
            if deck.archetype:
                archetype_str = deck.archetype.name if hasattr(deck.archetype, 'name') else str(deck.archetype)
            else:
                archetype_str = ""
            
            row = {
                "date": date or "",
                "deck_name": deck.name or "",
                "format": deck.format or "",
                "archetype": archetype_str,
                "author": metadata.get("author") or deck.source or "",
                "url": url,
                "maindeck_cards": maindeck_str,
                "sideboard_cards": sideboard_str,
            }
            writer.writerow(row)
