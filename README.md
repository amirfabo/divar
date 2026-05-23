## Divar API

<p align="center">
    <a href="https://github.com/amirfabo/divar">
        <img src=".github/images/logo.jpg" alt="divar" width="356">
    </a>
    <br>
The <i><b>fast</b></i> and <i><b>free</b></i> means for interacting with <a href="https://divar.ir">divar.
ir</a>
</p>

### Features

+ **Ready**
+ **Easy**
+ **Fast**
+ **Type-hinted**

### Installation

```bash
pip install git+https://github.com/amirfabo/divar.git
```

### Quick Start

```python
from divar import Client

client = Client("myapp")

# Get the last 100 posts from Mashhad
for post in client.get_posts(place_ids=3, limit=100):
    print(post)

# Get contact info of a post (auth needed)
client.authorize()
post = client.get_post(token="TOKEN")
contact = post.contact()
print(contact)
```

### Documentation

Use the links below to read usage with examples:
- [Methods](https://github.com/amirfabo/divar/tree/main/docs/methods.md)
- [Types](https://github.com/amirfabo/divar/tree/main/docs/types.md)

### Support

Your support helps us continue the development and maintenance of this project ❤️

TON or USDT (*TON*): `UQDH6BLtvJheNdQNbrVyI3_4dbsDaoYsyiOHyYVL_ndJ3D7u`<br>USDT (*TRC20*): `TMXg6DL2y8EC9RfXRzonDYrRrviZMrVzaL`

### Contact

Telegram: [@ItsFaBo](https://t.me/ItsFaBo)