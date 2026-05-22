import json
from importlib.resources import files
from datetime import datetime
from enum import Enum

class View:
    @staticmethod
    def default(obj):
        if isinstance(obj, (datetime, Enum)):
            return str(obj)

        return {
            "@type": obj.__class__.__name__,
            **{
                attr: getattr(obj, attr)
                for attr in filter(lambda x: not x.startswith("_"), obj.__dict__)
                if getattr(obj, attr) is not None
            }
        }

    def __str__(self) -> str:
        return json.dumps(
            self,
            indent=4,
            ensure_ascii=False,
            default=View.default
        )

    def __repr__(self) -> str:
        return "{}({})".format(
            self.__class__.__name__,
            ', '.join(
                f'{attr}={val!r}' 
                for attr, val in self.__dict__.items() 
                if not attr.startswith("_") and val is not None
            )
        )

class Account(View):
    def __init__(self, uid: str, phone: str):
        self.user_id = uid
        self.phone_number = phone

class City(View):
    def __init__(
        self,
        id: int,
        name: str,
        slug: str,
        parent_id: int,
        is_province: bool = False,
    ):
        self.id = id
        self.name = name
        self.slug = slug
        self.parent_id = parent_id
        self.is_province = is_province

    @classmethod
    def constructor(cls, name: str):
        path = files("divar.data").joinpath("places.json")
        places_data = json.loads(path.read_text(encoding="utf-8"))
        for place in places_data:
            if place['name'] == name and place['parent'] != 715:
                return cls(
                    id=place['id'],
                    name=place['name'],
                    slug=place['slug'],
                    parent_id=place['parent'],
                    is_province=False
                )

class Category(View):
    def __init__(
        self,
        title: str,
        slug: str,
        path: str = None    
    ):
        self.title = title
        self.slug = slug
        self.path = path

class Image(View):
    def __init__(
        self,
        url: str,
        thumbnail_url: str,
        is_video: bool = False
    ):
        self.url = url
        self.thumbnail_url = thumbnail_url
        self.is_video = is_video

class MetaData(View):
    def __init__(self, title: str, value: str):
        self.title = title
        self.value = value

class ContactType(Enum):
    CALL = 1
    SECURE_CALL = 2
    CHAT = 3
    UNKNOWN = 4

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

    def __str__(self):
        return f"{self.__class__.__name__}.{self.name}"

class Contact(View):
    def __init__(self, type: ContactType, phone_number: str = None):
        self.type = type
        self.phone_number = phone_number

class PostFull(View):
    def __init__(
        self,
        client,
        token: str,
        categories: list[Category],
        title: int,
        publish_date: datetime,
        city: City,
        district: str,
        data: list[MetaData],
        description: str,
        image_count: int,
        images: list[Image],
    ):
        self._client = client
        self._contact_uuid = None

        self.token = token
        self.categories = categories
        self.title = title
        self.publish_date = publish_date
        self.city = city
        self.district = district
        self.data = data
        self.description = description
        self.image_count = image_count
        self.images = images

    @property
    def url(self) -> str:
        return f"https://divar.ir/v/{self.token}"

    def set_contact_uuid(self, contact_uuid: str) -> None:
        self._contact_uuid = contact_uuid

    def contact(self) -> Contact:
        '''Bound method to retrieve contact info.

        Use as shortcut for *app.get_post_contact(post=post)*

        Return:
            A Contact object.
        '''

        return self._client.get_post_contact(post=self)

    def bookmark(self) -> bool:
        '''Bound method to bookmark a post.

        Use as shortcut for *app.bookmark_post(token='ABCDEF')*

        Return:
            True if bookmarked successfully.
        '''

        return self._client.bookmark_post(token=self.token)

class Post(View):
    def __init__(
        self,
        client,
        token: str,
        title: int,
        description: list,
        city: City,
        district: str,
        image_count: int,
        thumbnail_url: str,
        has_chat: bool,
        is_shop: bool,
        is_pelle: bool,
        is_nardeban: bool,
    ):
        self._client = client
        self.token = token
        self.title = title
        self.description = description
        self.city = city
        self.district = district
        self.image_count = image_count
        self.thumbnail_url = thumbnail_url
        self.has_chat = has_chat
        self.is_shop = is_shop
        self.is_pelle = is_pelle
        self.is_nardeban = is_nardeban

    @property
    def url(self) -> str:
        return f"https://divar.ir/v/{self.token}"

    def full(self):
        '''Bound method to retrieve full post information.

        Use as shortcut for *app.get_post(token='ABCDEF')*

        Return:
            A PostFull object.
        '''

        return self._client.get_post(token=self.token)