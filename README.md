## Divar API

<p align="center">
    <a href="https://github.com/amirfabo/divar">
        <img src=".github/images/logo.jpg" alt="divar" width="256">
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

### Setup

Clone files:
```
git clone https://github.com/amirfabo/divar.git
```

After fetch files, you must install requirements:
```
pip install -r requirements.txt 
```

### Usage

```py
from divar import Client

app = Client()

# Get the last 100 posts from Mashhad
for post in app.get_posts(place_ids=3, limit=100):
    print(post)

# Get only cars posts from Tehran and Mashhad
for post in app.get_posts(place_ids=[1, 3], category="cars", limit=25):
    print(post)

# Get full post information
post = app.get_post(token='ABCDEF'):
print(post)
```

### Contact

Telegram: [@ItsFaBo](https://t.me/ItsFaBo)