import json
from datetime import datetime

class View:
    @staticmethod
    def default(obj):
        if isinstance(obj, datetime):
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
                if val is not None
            )
        )

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
        with open('data/places.json', 'r', encoding='utf-8') as file:
            for place in json.load(file):
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
    def __init__(self, title, value):
        self.title = title
        self.value = value

class PostFull(View):
    def __init__(
        self,
        token: str,
        categories: list[Category],
        title: int,
        publish_date: datetime,
        city: City,
        district: str,
        data: list[MetaData],
        description: str,
        image_count: int,
        images: list[Image]
    ):
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
        # self.contact = contact

    @property
    def url(self) -> str:
        return f"https://divar.ir/v/{self.token}"

class Post(View):
    def __init__(
        self,
        token: str,
        title: int,
        description: list,
        city: City,
        district: str,
        image_count: int,
        thumbnail_url: str,
    ):
        self.token = token
        self.title = title
        self.description = description
        self.city = city
        self.district = district
        self.image_count = image_count
        self.thumbnail_url = thumbnail_url

    @property
    def url(self) -> str:
        return f"https://divar.ir/v/{self.token}"