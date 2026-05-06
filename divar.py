import json
import requests
import time
import random

from typing import Generator
from persiantools.jdatetime import JalaliDateTime
from models import (
    City,
    Category,
    Post,
    PostFull,
    Data,
    Image,
)

from user_agent import generate_user_agent

API_URL = "https://api.divar.ir/v8/postlist/w/search"
POST_DATA_URL = "https://api.divar.ir/v8/posts-v2/web/{token}"

class DivarCli:
    """Divar Client, the standard means for interacting with Divar.

    Parameters:
        timeout (int):
            Set the maximum time for waiting to server response.
            Default to 5 seconds.

        retries (int):
            Set the maximum retries for consecutive failed requests.
            Default to 3 attempts.
    """

    def __init__(
        self,
        timeout: int = 5,
        retries: int = 3
    ) -> None:
        self.session = requests.Session()
        self.retries = retries
        self.timeout = timeout

    def _data_raw_generator(self, city_ids: list, category: str = None) -> str:
        """Generate request data raw"""

        data = dict(
            city_ids=city_ids,
            disable_recommendation=False,
        )

        if category:
            data["search_data"] = {
                    "form_data": {
                        "data": {"category": {"str": {"value": category}}}
                    }
                }
    
            data['source_view'] = "CATEGORY"

        return data

    def _post_widget_normalize(self, widget: dict) -> Post:
        """Create a Post object from widget"""

        data = widget['data']
        web_info = data['action']['payload']['web_info']

        return Post(
            token=data['token'],
            title=data['title'],
            description=[
                data.get(f"{prefix}_description_text", None)
                for prefix in ('top', 'middle', 'bottom') 
            ],
            district=web_info.get('district_persian'),
            city=City.constructor(name=web_info.get('city_persian')),
            image_count=data.get('image_count', 0),
            thumbnail_url=data.get('image_url', None)
        )

    def get_place_by_id(place_id: int) -> City | None:
        '''Get place by id.

        Parameters:
            place_id (int):
                The specific place identifier.

        Return:
            A City object if place id is valid, otherwise None.
        '''

        with open("./places.json", "r", encoding="utf-8") as file:
            places_data = json.load(file)
            for place in places_data:
                if place['id'] == place_id:
                    return City(
                        id=place['id'],
                        name=place['name'],
                        slug=place['id'],
                        parent_id=place['parent'],
                        is_province=place['parent'] == 715,
                    )

        return None

    def get_all_places(self) -> list[City]:
        '''Get available places.

        Return:
            A list of City objects.
        '''

        with open('places.json', 'r', encoding='utf-8') as file:
            return [
                City(
                    id=place['id'],
                    name=place['name'],
                    slug=place['id'],
                    parent_id=place['parent'],
                    is_province=place['parent'] == 715,
                ) for place in json.load(file)
            ]

    def get_category_by_name(title: str) -> list[Category]:
        '''Get category (or categories) by title.

        Parameters:
            title (str):
                The specific category title.

        Return:
            A list of Category objects.
        '''

        result = []
        with open("categories.json", "r", encoding="utf-8") as file:
            categories_data = json.load(file)
            for category in categories_data:
                if query in category['title']:
                    result.append(
                        Category(
                            title=category['title'],
                            slug=category['slug'],
                            path=category['path']
                        )
                    )

        return result

    def get_all_categories(self) -> list[Category]:
        '''Get available categories.

        Return:
            A list of Category objects.
        '''

        with open('categories.json', 'r', encoding='utf-8') as file:
            return [
                Category(
                    title=category['title'],
                    slug=category['slug'],
                    path=category['path']
                ) for category in json.load(file)
            ]

    def get_posts(
        self,
        place_ids: int | list = 1,
        category: str = "ROOT",
        limit: int = 200
    ) -> Generator[Post, None, None]:
        '''Retrieve all posts.

            Parameters:
                place_ids (int | list): 
                    Place id or the list of place ids, Default is Tehran.
                
                category (str):
                    Category slug, Default is main page.
                
                limit (int):
                    Maximum count of posts.

            Return:
                A generator yielding Post objects.
        '''

        if isinstance(place_ids, list):
            place_ids = [str(place_id) for place_id in place_ids]

        else:
            place_ids = [str(place_ids)]

        ua = generate_user_agent(device_type="smartphone")
        pagination_data = None

        post_tokens = []
        post_count = 0
        retries = 0
        while post_count < limit:

            data_raw = self._data_raw_generator(
                city_ids=place_ids, category=category)

            if pagination_data:
                data_raw['pagination_data'] = pagination_data

            try:
                response = self.session.post(
                    url=API_URL,
                    headers={
                        'accept': 'application/json, text/plain, */*',
                        'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
                        'content-type': 'application/json',
                        'origin': 'https://divar.ir',
                        'priority': 'u=1, i',
                        'referer': 'https://divar.ir/',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-site',
                        'x-render-type': 'CSR',
                        'x-standard-divar-error': 'true',
                        'user-agent': ua,
                    },
                    json=data_raw,
                    timeout=self.timeout,
                )

                retries = 0
                if response.status_code != 200:
                    raise Exception(f"Request failed: {response}")

                json_data = response.json()
                widgets = json_data['list_widgets']
                pagination_data = json_data['pagination']['data']

                new_posts = 0
                for widget in widgets:
                    if widget['widget_type'] != "POST_ROW":
                        continue

                    post = self._post_widget_normalize(widget=widget)
                    if post.token not in post_tokens:
                        post_tokens.append(post.token)
                        post_count += 1
                        new_posts += 1
                        yield post

                    if post_count == limit:
                        break

                if new_posts == 0:
                    break

            except requests.ReadTimeout:
                if retries == self.retries:
                    raise

                retries += 1
                continue

            finally:
                time.sleep(random.uniform(0.3, 0.5))

    def get_post(self, token: str) -> PostFull:
        '''Retrieve full post information.

        Parameters:
            token (str):
                Unique post token.

        Return:
            A PostFull object.
        '''

        response = self.session.get(
            url=POST_DATA_URL.format(token=token),
            headers={
                'accept': 'application/json-filled',
                'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
                'origin': 'https://divar.ir',
                'priority': 'u=1, i',
                'referer': 'https://divar.ir/',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'x-render-type': 'CSR',
                'user-agent': generate_user_agent(device_type='smartphone')
            },
            timeout=self.timeout,
        )

        if response.status_code != 200:
            raise Exception(f"Request failed: {response}")

        data = response.json()
        sections = data['sections']
        web_engage = data['webengage']
        seo = data['seo']
        web_info = seo['web_info']

        categories = []
        publish_text = ""
        description = ""
        data_list = []
        images = []

        for section in sections:
            section_name = section['section_name']
            widgets = section['widgets']
            if section_name == "BREADCRUMB":
                for widget in widgets:
                    if widget['widget_type'] == "BREADCRUMB":
                        for item in widget['data']['parent_items']:
                            categories.append(
                                Category(
                                    title=item['title'],
                                    slug=item['action']['payload']['search_data']['form_data']['data']['category']['str']['value']
                                )
                            )

            elif section_name == "TITLE":
                for widget in widgets:
                    if widget['widget_type'] == "EXPANDABLE_SECTION":
                        text = widget['data']['widget_list'][0]['data']['text']
                        for line in text.splitlines():
                            if line.startswith('انتشار'):
                                publish_text = line.replace('انتشار آگهی:', '').strip()
                                break

                        break

            elif section_name == "DESCRIPTION":
                for widget in widgets:
                    if widget['widget_type'] == "DESCRIPTION_ROW":
                        description = widget['data']['text']
                        break

            elif section_name == "LIST_DATA":
                for widget in widgets:
                    widget_type = widget['widget_type']
                    if widget_type == "GROUP_INFO_ROW":
                        for item in widget['data']['items']:
                            data_list.append(
                                Data(
                                    title=item['title'],
                                    value=item['value']
                                )
                            )

                    elif widget_type == "UNEXPANDABLE_ROW":
                        data_list.append(
                            Data(
                                title=widget['data']['title'],
                                value=widget['data']['value']
                            )
                        )

            elif section_name == "IMAGE":
                for widget in widgets:
                    if widget['widget_type'] == "IMAGE_CAROUSEL":
                        for img in widget['data']['items']:
                            if img['video_url']:
                                image_obj = Image(
                                    url=img['video_url'],
                                    thumbnail_url=img['image']['url'],
                                    is_video=True
                                )

                            else:
                                image_obj = Image(
                                    url=img['image']['url'],
                                    thumbnail_url=img['image']['thumbnail_url'],
                                )

                            images.append(image_obj)

        postfull = PostFull(
            token=web_engage['token'],
            categories=categories,
            title=web_info['title'],
            publish_date=JalaliDateTime.strptime(publish_text, "%d %B %Y، %H:%M", locale="fa").to_gregorian(),
            city=City.constructor(name=web_info['city_persian']),
            district=web_info['district_persian'],
            data=data_list,
            description=description,
            image_count=web_engage['image_count'],
            images=images,
        )

        return postfull