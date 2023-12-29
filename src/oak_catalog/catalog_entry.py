"""Define the CatalogEntry class, which represents a single entry in the catalog."""

from datetime import date
from typing import List, Literal, Union

from pydantic import BaseModel, Field


class CatalogEntry(BaseModel):
    """
    Class to represent a single entry in the catalog.

    Attributes
    ----------
    entry_id : str
        The ID of the entry.
    entry_type : Literal["article", "audiobook", "book"]
        The type of the entry.
    isbn : str, optional
        The ISBN of the entry.
    asin : str, optional
        The ASIN of the entry.
    url : str, optional
        The URL of the entry.
    title : str
        The title of the entry.
    author : List[str]
        The author(s) of the entry.
    subtitle : str, optional
        The subtitle of the entry.
    full_title : str, optional
        The full title of the entry.
    narrator : List[str], optional
        The narrator(s) of the entry.
    description : str, optional
        The description of the entry.
    format : str, optional
        The format of the entry.
    length : str, optional
        The length of the entry.
    language : List[str], optional
        The language(s) of the entry.
    publisher : str, optional
        The publisher of the entry.
    publishing_date : date, optional
        The publishing date of the entry.
    theme : str, optional
        The theme of the entry.
    topics : List[str], optional
        The topics of the entry.
    tags : List[str], optional
        The tags of the entry.
    location : str, optional
        The location of the entry.
    purchase_date : date, optional
        The purchase date of the entry.
    entry_creation_date : date, optional
        The creation date of the entry.
    cover_filename : str, optional
        The filename of the cover image of the entry.
    markdown_filename : str, optional
        The filename of the markdown file of the entry.
    site_url : str, optional
        The URL of the entry in the site.
    """

    entry_id: str = Field(min_length=1)
    entry_type: Union[Literal['article'], Literal['audiobook'], Literal['book']]

    isbn: str = None
    asin: str = None
    url: str = None

    title: str = Field(min_length=1)
    author: List[str] = Field(min_length=1)
    subtitle: str = None
    full_title: str = None
    narrator: List[str] = None
    description: str = None
    format: str = None
    length: str = None
    language: List[str] = Field(default_factory=lambda: ['English'])
    publisher: str = None
    publishing_date: date = None

    theme: str = None
    topics: List[str] = None
    tags: List[str] = None
    location: str = 'New York'
    purchase_date: date = None

    entry_creation_date: date = Field(default_factory=date.today)

    cover_filename: str = None
    markdown_filename: str = None
    site_url: str = None
