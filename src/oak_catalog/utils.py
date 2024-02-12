"""Utility functions for the Oak Catalog."""

import datetime
import re
from functools import reduce


def special_cases_for_author(value):
    """
    Handle special cases for author values.

    Parameters
    ----------
    value : str
        The author value.

    Returns
    -------
    str
        The modified author value.
    """
    # Unique bogus values from Omnivore
    if value == 'Frank Herbert, Dune':
        return None
    if value == 'Sasha ArchibaldPublishedJan 4, 2024':
        return 'Sasha Archibald'
    if value == 'An interview with Cory Doctorow':
        return None
    if value == 'Rachel Grove 1 ,':
        return 'Rachel Grove'
    if value == 'Tippy Kintanar View all posts':
        return 'Tippy Kintanar'
    # variations of "by"
    if ' by ' in value:
        return value.split(' by ')[1]
    if value.startswith('Posted by: '):
        return value.split('Posted by: ')[1]
    # email addresses
    if '<' in value:
        return str(re.sub(r'<[\w.-]+@[\w.-]+>', '', value))
    return value


def remove_special_characters(value):
    """
    Remove special characters from a string.

    Parameters
    ----------
    value : str
        The string to remove special characters from.

    Returns
    -------
    str
        The string with special characters removed.
    """
    value = value.replace('\u200b', '')
    return value


def validate_author(value):
    """
    Validate the author value.

    Parameters
    ----------
    value : str | List[str]
        The author value.

    Returns
    -------
    List[str]
        The list of authors.
    """

    if value in ('', 'undefined', 'null', 'None', None):
        return []
    if isinstance(value, str):
        value = remove_special_characters(value)
        value = special_cases_for_author(value)

        if value is None:
            return validate_author(value)
        if ' and ' in value:
            return validate_author(value.replace(' and ', ', '))
        if ', ' in value:
            return validate_author(value.split(', '))
        if value and not re.match(r"^[\w -.']+$", value):
            return [f'failed regex: {value}']
        return [value]
    if isinstance(value, list):
        return reduce(lambda a, b: a + b, [validate_author(v) for v in value])
    raise ValueError(f'Invalid author: {value}')


def validate_date(value):
    """
    Make a date from a string, datetime or date.

    Parameters
    ----------
    value : str | date | datetime | None
        The date value.

    Returns
    -------
    datetime.date
        The date.
    """
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        return datetime.datetime.strptime(value, '%Y-%m-%d').date()

    raise ValueError(f'Invalid date: {value}')
