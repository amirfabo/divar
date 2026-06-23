import re
import json
import requests
import time
import base64
import random

from importlib.resources import files
from typing import Generator
from persiantools.jdatetime import JalaliDateTime
from persiantools.digits import fa_to_en

from .models import (
    City,
    Category,
    Post,
    PostFull,
    MetaData,
    Image,
    Contact,
    ContactType,
    Account,
)

from .session import FileSession, MemorySession
from . import errors
from .places import get_place_by_name

from user_agent import generate_user_agent

class Client:
    """Divar Client, a Python client for interacting with Divar.

    Parameters:
        session (str | None):
            The file name of the session file (may be a full path), 
            If it's None the session will not be saved.
            Default to None.

        timeout (int):
            Set the maximum time for waiting to server response.
            Default to 5 seconds.

        retries (int):
            Set the maximum retries for any request.
            Default to 3 attempts.
    """

    def __init__(
        self,
        session: str | None = None,
        timeout: int = 5,
        retries: int = 3,
    ) -> None:

        if session is None:
            self.storage = MemorySession()

        else:
            self.storage = FileSession(session_name=session)

        self.retries = retries
        self.timeout = timeout
        self.is_authorized = False

        self._user_agent = generate_user_agent(device_type="smartphone")
        self._req_session = requests.Session()
        self._req_session.headers.update(
            {   
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
                'origin': 'https://divar.ir',
                'referer': 'https://divar.ir/',
                'user-agent': self._user_agent,
                'x-screen-size': random.choice(
                    [
                        '390x844', '430x932',
                        '360x780', '384x854',
                        '412x915'
                    ]
                )
            }
        )

    def _ensure_response(self, response: requests.Response, key: str) -> dict:  
        try:
            data = response.json()

        except ValueError:
            raise errors.InvalidResponse("Response is not valid JSON")

        if key not in data:
            raise errors.InvalidResponse(
                f"Missing required key: {key!r}",
                response=data
            )

        return data

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault('timeout', self.timeout)
        method = method.upper()
        for _ in range(self.retries):
            while True:
                try:
                    if method == "GET":
                        response = self._req_session.get(url=url, **kwargs)

                    elif method == "POST":
                        response = self._req_session.post(url=url, **kwargs)

                    if response.status_code == 403 \
                        and response.text.lower() == "jwt is expired":

                        self.__revive_session()
                        continue

                    if response.status_code == 429:
                        raise errors.HttpError(
                            status_code=429, message="Too many requests.")

                    return response

                except requests.RequestException:
                    break

        raise errors.MaxRetriesError()

    def __revive_session(self) -> bool:
        ref_response = self.__refresh_session()

        headers = ref_response.headers
        new_cookies = ref_response.cookies

        for name, value in new_cookies.items():
            self._req_session.cookies.set(
                name=name,
                value=value,
                domain=".divar.ir",
                path="/"
            )

        s_front_token = headers.get('Front-Token')
        if not s_front_token:
            s_access_token = self._req_session.cookies.get(
                name="sAccessToken",
                domain=".divar.ir",
                path="/"    
            )
            s_front_token = s_access_token.split(".")[1]

        self._req_session.cookies.set(
            name="sFrontToken",
            value=s_front_token,
            domain=".divar.ir",
            path="/"
        )

        if self.__verify_session():
            self.storage.save(self._req_session.cookies.get_dict())
            return True

        raise errors.SessionExpired("Session is expired, Delete the session file and try again.")

    def __refresh_session(self) -> requests.Response:
        url = "https://api.divar.ir/v8/authenticate/session/refresh"
        response = self._req_session.post(url=url, data=b"{}")
        return response

    def __verify_session(self) -> bool:
        url = "https://api.divar.ir/v8/user-profile/user-nationality"
        response = self._request("GET", url=url)
        return (response.status_code == 200)

    def __send_code(self, phone_number: str) -> requests.Response:
        url = "https://api.divar.ir/v8/authenticate/signinup/code"
        return self._request(
            "POST",
            url=url,
            headers={
                **self._req_session.headers,
                'content-type': 'application/json',
                'rid': 'passwordless',
                'st-auth-mode': 'cookie',
            },
            json={"phoneNumber": phone_number}
        )

    def __consume_authorize(self, code: str, data: dict) -> requests.Response:
        url = "https://api.divar.ir/v8/authenticate/signinup/code/consume"
        response = self._request(
            "POST",
            url=url,
            headers={
                **self._req_session.headers,
                'content-type': 'application/json',
                'rid': 'passwordless',
                'st-auth-mode': 'cookie',
            },
            json={
                "deviceId": data['deviceId'],
                "preAuthSessionId": data['preAuthSessionId'],
                "userInputCode": code,
            }
        )

        return response

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
            client=self,
            token=data['token'],
            title=data['title'],
            description=[
                data.get(f"{prefix}_description_text", None)
                for prefix in ('top', 'middle', 'bottom') 
            ],
            district=web_info.get('district_persian'),
            city=get_place_by_name(
                name=web_info.get('city_persian'),
                include_province=False    
            ),
            image_count=data.get('image_count', 0),
            thumbnail_url=data.get('image_url', None),
            has_chat=data.get('has_chat', False),
            is_shop="فروشگاه" in data.get("red_text", ""),
            is_pelle="پله شده" in data.get("red_text", ""),
            is_nardeban="نردبان شده" in data.get("red_text", ""),
        )

    def _ensure_authorize(self) -> bool:
        if not self.is_authorized:
            raise errors.AuthorizeRequired("Client is not authorized")

        return True

    def authorize(self) -> bool:
        """Authenticate the client session.

        For new sessions, this method automatically handles the
        authorization process using an interactive prompt.

        Returns:
            bool: True if the authorization was successful.
        """

        if self.is_authorized:
            raise errors.AuthorizationError("Client is already authorized") 

        if self.storage.exists():
            cookies = self.storage.load()
            self._req_session.cookies.clear()

            for name, value in cookies.items():
                self._req_session.cookies.set(
                    name=name,
                    value=value,
                    domain=".divar.ir",
                    path="/"
                )

            if self.__verify_session():
                self.is_authorized = True
                return True

            self.__revive_session()
            self.is_authorized = True
            return True

        phone_number = input("Enter phone number (e.g. 09123456789): ")
        if not re.fullmatch(r"^09\d{9}$", phone_number):
            raise ValueError("Invalid phone number format.")

        # Fetch Mainpage
        self._request("GET", "https://divar.ir/")
        time.sleep(0.25)

        code_response = self.__send_code(phone_number='+98' + phone_number.lstrip('0'))
        if code_response.status_code != 200:
            raise errors.AuthorizationError("Failed to send verification code.")

        code_response_data = code_response.json()
        for _ in range(3):
            code = input("Enter verification code: ")
            consume_response = self.__consume_authorize(code=code, data=code_response_data)
            consume_data = consume_response.json()
            if not (consume_response.status_code == 200 and consume_data['status'] == "OK"):
                print("Verification code is invalid!\n")
                continue

            headers = consume_response.headers
            cookies = self._req_session.cookies

            s_front_token = headers.get('Front-Token')
            if not s_front_token:
                s_access_token = cookies.get(
                    name='sAccessToken',
                    domain='.divar.ir',
                    path=''
                )
                s_front_token = s_access_token.split('.')[1]

            cookies.set(
                name="sFrontToken", 
                value=s_front_token, 
                domain=".divar.ir", 
                path="/"
            )

            self.storage.save(cookies.get_dict())
            self.is_authorized = True
            print("You are authorized successfully.")
            return True

        raise errors.AuthorizationError()

    def get_me(self) -> Account:
        """Get own account info.

        Return:
            An Account object.
        """

        # This method require authorized session
        self._ensure_authorize()

        s_front_token = self._req_session.cookies.get('sFrontToken')
        b64token = s_front_token + ("=" * (len(s_front_token) % 4))
        data = json.loads(base64.urlsafe_b64decode(b64token))

        return Account(
            uid=data.get('uid') or data['up']['sub'],
            phone=data['up']['phoneNumber']
        )

    def bookmark_post(self, token: str) -> bool:
        """Bookmark a post.

        Parameters:
            token (str):
                Unique token of the target post.

        Return:
            bool: True if bookmarked successfully.
        """

        # This method require authorized session
        self._ensure_authorize()

        url = "https://api.divar.ir/v8/yaad-v2/bookmark"
        response = self._request(
            "POST",
            url=url,
            json={'token': token}
        )

        return (response.status_code == 200)

    def get_bookmarks(self) -> list[Post]:
        """Get bookmarked posts.

        Return:
            A list of Post objects.
        """

        # This method require authorized session
        self._ensure_authorize()

        url = "https://api.divar.ir/v8/yaad-v2/bookmarks-tab/widgets"
        response = self._request("GET", url=url)

        data = self._ensure_response(response=response, key="widget_list")
        widgets = data['widget_list']

        posts = []
        for widget in widgets:
            if widget['widget_type'] != "POST_ROW":
                    continue

            posts.append(self._post_widget_normalize(widget=widget))

        return posts

    def get_posts(
        self,
        place_ids: int | list = 1,
        category: str = "ROOT",
        limit: int = 200
    ) -> Generator[Post, None, None]:
        """Retrieve all posts.

            Parameters:
                place_ids (int | list): 
                    Place id or the list of place ids, Default is Tehran.
                
                category (str):
                    Category slug, Default is main page.
                
                limit (int):
                    Maximum count of posts.

            Return:
                A generator yielding Post objects.
        """

        if isinstance(place_ids, list):
            place_ids = [str(place_id) for place_id in place_ids]

        else:
            place_ids = [str(place_ids)]

        pagination_data = None
        post_tokens = []
        post_count = 0
        while post_count < limit:

            data_raw = self._data_raw_generator(
                city_ids=place_ids, category=category)

            if pagination_data:
                data_raw['pagination_data'] = pagination_data

            response = self._request(
                "POST", 
                url="https://api.divar.ir/v8/postlist/w/search",
                json=data_raw
            )
            json_data = self._ensure_response(response, "list_widgets")
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

    def get_post(self, token: str) -> PostFull:
        """Retrieve full post information.

        Parameters:
            token (str):
                Unique token of post.

        Return:
            A PostFull object.
        """

        response = self._request(
            "GET",
            url=f"https://api.divar.ir/v8/posts-v2/web/{token}",
            headers={
                **self._req_session.headers,
                'accept': 'application/json-filled',
            }
        )

        try:
            data = self._ensure_response(response, "sections")
    
        except errors.InvalidResponse as e:
            r_data = e.response
            if r_data and r_data.get("message") == "آگهی یافت نشد":
                raise errors.PostNotFound() from e

            raise

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
                                MetaData(
                                    title=item['title'],
                                    value=item['value']
                                )
                            )

                    elif widget_type == "UNEXPANDABLE_ROW":
                        data_list.append(
                            MetaData(
                                title=widget['data']['title'],
                                value=widget['data']['value']
                            )
                        )
    
                    elif widget_type == "SCORE_ROW":
                        data_list.append(
                            MetaData(
                                title=widget['data']['title'],
                                value=widget['data']['descriptive_score']
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
            client=self,
            token=web_engage['token'],
            categories=categories,
            title=web_info['title'],
            publish_date=JalaliDateTime.strptime(publish_text, "%d %B %Y، %H:%M", locale="fa").to_gregorian(),
            city=get_place_by_name(
                name=web_info['city_persian'],
                include_province=False    
            ),
            district=web_info['district_persian'],
            data=data_list,
            description=description,
            image_count=web_engage['image_count'],
            images=images,
        )
        postfull.set_contact_uuid(data['contact']['contact_uuid'])
        return postfull

    def get_post_contact(self, post: PostFull) -> Contact:
        """Retrieve the post contact info.

        Parameters:
            post (models.PostFull):
                A PostFull object.

        Return:
            A Contact object.
        """

        # This method require authorized session
        self._ensure_authorize()

        url = f"https://api.divar.ir/v8/postcontact/web/contact_info_v2/{post.token}"
        response = self._request(
            "POST",
            url=url,
            json={"contact_uuid": post._contact_uuid}
        )

        try:
            data = self._ensure_response(response, 'widget_list')

        except errors.InvalidResponse as e:
            r_data = e.response
            if r_data and r_data.get("hip_action"):
                raise errors.CaptchaRequired() from e

            raise

        widget_list = data['widget_list']
        widget = widget_list[0]
        widget_data = widget['data']
        info =  widget['action_log']['server_side_info']['info']
        contact_method = info['contact_method']

        mapping = {
            "CALL": ContactType.CALL,
            "SECURE_CALL": ContactType.SECURE_CALL,
            "CHAT": ContactType.CHAT,
        }

        return Contact(
            type=mapping.get(contact_method, ContactType.UNKNOWN),
            phone_number=fa_to_en(widget_data['value']) if contact_method == "CALL" else None
        )