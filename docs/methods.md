# Client Methods

## authorize()

Authorize the current client session.

In case of a new session, this method automatically handles the authorization process using an interactive prompt and stores the session file locally for future usage.

### Returns

| Type |
|---|
| `bool` |

Returns `True` if authorization was successful.

### Raises

| Exception | Description |
|---|---|
| `AuthorizationError` | Client is already authorized or authorization failed. |
| `ValueError` | Phone number format is invalid. |

### Example

```python
client.authorize()
```

---

# Places

## get_place_by_id()

Retrieve a place by its identifier.

### Parameters

| Name | Type | Description |
|---|---|---|
| `place_id` | `int` | Specific place identifier. |

### Returns

| Type |
|---|
| `City \| None` |

Returns a `City` object if the place exists, otherwise `None`.

### Example

```python
city = client.get_place_by_id(place_id=1)
print(city.name)
```

---

## get_all_places()

Retrieve all available places.

### Returns

| Type |
|---|
| `list[City]` |

---

# Categories

## get_category_by_name()

Retrieve categories matching a specific title.

### Parameters

| Name | Type | Description |
|---|---|---|
| `title` | `str` | Category title to search for. |

### Returns

| Type |
|---|
| `list[Category]` |

### Example

```python
categories = client.get_category_by_name(title="خودرو")
```

---

## get_all_categories()

Retrieve all available categories.

### Returns

| Type |
|---|
| `list[Category]` |

---

# Account

## get_me()

Retrieve information about the currently authorized account.

> This method requires an authorized session.

### Returns

| Type |
|---|
| `Account` |

---

# Bookmarks

## bookmark_post()

Bookmark a post.

> This method requires an authorized session.

### Parameters

| Name | Type | Description |
|---|---|---|
| `token` | `str` | Unique post token. |

### Returns

| Type |
|---|
| `bool` |

Returns `True` if the post was bookmarked successfully.

### Example

```python
client.bookmark_post(token="TOKEN")
```

---

## get_bookmarks()

Retrieve bookmarked posts.

> This method requires an authorized session.

### Returns

| Type |
|---|
| `list[Post]` |

---

# Posts

## get_posts()

Retrieve posts from Divar.

### Parameters

| Name | Type | Description |
|---|---|---|
| `place_ids` | `int \| list` | Place identifier or list of place identifiers. Default is Tehran (`1`). |
| `category` | `str` | Category slug. Default is `"ROOT"`. |
| `limit` | `int` | Maximum number of posts to retrieve. |

### Returns

| Type |
|---|
| `Generator[Post, None, None]` |

A generator yielding `Post` objects.

### Example

```python
posts = client.get_posts(
    place_ids=1, # also [1, 2, 3]
    category="cars",
    limit=10
)

for post in posts:
    print(post.title)
```

---

## get_post()

Retrieve full information about a post.

### Parameters

| Name | Type | Description |
|---|---|---|
| `token` | `str` | Unique post token. |

### Returns

| Type |
|---|
| `PostFull` |

### Example

```python
post = client.get_post(token="TOKEN")
print(post.title)
print(post.description)
print(post.contact())
```

---

## get_post_contact()

Retrieve contact information of a post.

> This method requires an authorized session. 

### Parameters

| Name | Type | Description |
|---|---|---|
| `post` | `PostFull` | A `PostFull` object. |

### Returns

| Type |
|---|
| `Contact` |

### Raises

| Exception | Description |
|---|---|
| `CaptchaRequired` | Divar requires captcha verification before revealing contact information. |

### Example

```python
post = client.get_post(token="TOKEN")
contact = client.get_post_contact(post=post)
print(contact.phone_number)

# OR Use bound method

post = client.get_post(token="TOKEN")
print(post.contact())
```