import json
from importlib.resources import files

from ..models import City

path = files("divar.places").joinpath("places.json")
PLACES = json.loads(path.read_text(encoding='utf-8'))

def get_place_by_id(place_id: int) -> City | None:
    """Get place by id.

    Parameters:
        place_id (int):
            The specific place identifier.

    Return:
        A City object if place id is valid, otherwise None.
    """

    for place in PLACES:
        if place['id'] == place_id:
            return City(
                id=place['id'],
                name=place['name'],
                slug=place['slug'],
                parent_id=place['parent'],
                is_province=place['parent'] == 715,
            )

    return None

def get_place_by_name(name: str, include_province: bool = True) -> City | None:
    """Get place by name.

    Parameters:
        name (str):
            The specific place name.

    Return:
        A City object if place exists, otherwise None.
    """

    for place in PLACES:
        is_province = place['parent'] == 715
        if is_province and not include_province:
            continue

        if place['name'] == name:
            return City(
                id=place['id'],
                name=place['name'],
                slug=place['slug'],
                parent_id=place['parent'],
                is_province=is_province,
            )

def get_all_places() -> list[City]:
    """Get available places.

    Return:
        A list of City objects.
    """

    return [
        City(
            id=place['id'],
            name=place['name'],
            slug=place['slug'],
            parent_id=place['parent'],
            is_province=place['parent'] == 715,
        ) for place in PLACES
    ]
