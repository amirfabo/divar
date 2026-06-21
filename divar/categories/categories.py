import json
from importlib.resources import files

from ..models import Category

path = files("divar.categories").joinpath("categories.json")
CATEGORIES = json.loads(path.read_text(encoding='utf-8'))

def get_category_by_name(title: str) -> list[Category]:
    """Get category (or categories) by title.

    Parameters:
        title (str):
            The specific category title.

    Return:
        A list of Category objects.
    """

    result = []
    for category in CATEGORIES:
        if title in category['title']:
            result.append(
                Category(
                    title=category['title'],
                    slug=category['slug'],
                    path=category['path']
                )
            )

    return result

def get_all_categories() -> list[Category]:
    """Get available categories.

    Return:
        A list of Category objects.
    """

    return [
        Category(
            title=category['title'],
            slug=category['slug'],
            path=category['path']
        ) for category in CATEGORIES
    ]
