"""

    scripts.update.py
    ~~~~~~~~~~~~~~~~~
    Script to download updated data files and update the README.

    @author: mazz3rr

"""
import sys

from mtgscrap.scryfall import download_scryfall_bulk_data, download_scryfall_set_data
from mtgscrap.mtgwiki import download_page as download_wiki_page


def _update():
    download_wiki_page()
    download_scryfall_bulk_data()
    download_scryfall_set_data()


if __name__ == '__main__':
    sys.exit(_update())
