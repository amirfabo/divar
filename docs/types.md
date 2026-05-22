# Models

## Account

Represents an authorized Divar account.

### Attributes

| Name | Type | Description |
|---|---|---|
| `user_id` | `str` | Unique user identifier. |
| `phone_number` | `str` | Account phone number. |

---

## City

Represents a Divar city or province.

### Attributes

| Name | Type | Description |
|---|---|---|
| `id` | `int` | Unique place identifier. |
| `name` | `str` | Place name. |
| `slug` | `str` | Place slug. |
| `parent_id` | `int` | Parent place identifier. |
| `is_province` | `bool` | Indicates whether the place is a province. |

---

## Category

Represents a Divar category.

### Attributes

| Name | Type | Description |
|---|---|---|
| `title` | `str` | Category title. |
| `slug` | `str` | Category slug. |
| `path` | `str \| None` | Category path. |

---

## Image

Represents a post image or video.

### Attributes

| Name | Type | Description |
|---|---|---|
| `url` | `str` | Direct image or video URL. |
| `thumbnail_url` | `str` | Thumbnail image URL. |
| `is_video` | `bool` | Indicates whether the media is a video. |

---

## MetaData

Represents post metadata.

### Attributes

| Name | Type | Description |
|---|---|---|
| `title` | `str` | Metadata title. |
| `value` | `str` | Metadata value. |

---

## Contact

Represents post contact information.

### Attributes

| Name | Type | Description |
|---|---|---|
| `type` | `ContactType` | Contact method type. |
| `phone_number` | `str \| None` | Contact phone number. |

---

## Post

Represents a Divar post preview object.

### Attributes

| Name | Type | Description |
|---|---|---|
| `token` | `str` | Unique post token. |
| `title` | `str` | Post title. |
| `description` | `list` | Post description lines. |
| `city` | `City` | Related city. |
| `district` | `str` | Related district. |
| `image_count` | `int` | Total image count. |
| `thumbnail_url` | `str` | Thumbnail image URL. |
| `has_chat` | `bool` | Indicates whether chat is available. |
| `is_shop` | `bool` | Indicates whether the advertiser is a shop. |
| `is_pelle` | `bool` | Indicates whether the post is promoted. |
| `is_nardeban` | `bool` | Indicates whether the post is pinned. |
| `url` | `str` | Public Divar post URL. |

### Bound Methods

#### full()

Retrieve full information of the current post.

Equivalent to:

```python
client.get_post(token=post.token)
```

#### Returns

| Type |
|---|
| `PostFull` |

#### Example

```python
post = next(client.get_posts())
full_post = post.full()
print(full_post.description)
```

---

## PostFull

Represents a complete Divar post object.

### Attributes

| Name | Type | Description |
|---|---|---|
| `token` | `str` | Unique post token. |
| `categories` | `list[Category]` | Related categories. |
| `title` | `str` | Post title. |
| `publish_date` | `datetime` | Publish datetime. |
| `city` | `City` | Related city. |
| `district` | `str` | Related district. |
| `data` | `list[MetaData]` | Additional metadata list. |
| `description` | `str` | Full post description. |
| `image_count` | `int` | Total image count. |
| `images` | `list[Image]` | Post images/videos. |
| `url` | `str` | Public Divar post URL. |

### Bound Methods

#### contact()

Retrieve contact information of the current post.

Equivalent to:

```python
client.get_post_contact(post=post)
```

#### Returns

| Type |
|---|
| `Contact` |

#### Example

```python
post = client.get_post(token="TOKEN")
contact = post.contact()
print(contact.phone_number)
```

---

#### bookmark()

Bookmark the current post.

Equivalent to:

```python
client.bookmark_post(token=post.token)
```

#### Returns

| Type |
|---|
| `bool` |

#### Example

```python
post = client.get_post(token="TOKEN")
post.bookmark()
```