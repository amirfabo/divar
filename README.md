## Divar API Interface

<p align="center">
    <a href="https://github.com/amirfabo/divar">
    <img src="https://marketing.divarcdn.com/kise/landings/brand/assets/images/different-field-logoType-img1.jpg" alt="divar" width=256>
    </a>
</p>

The fast and free means for interacting with [divar.ir](https://divar.ir)

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

# Get posts
for post in app.get_posts(limit=100):
    print(post)

# Get post information
post = app.get_post(token='ABCDEF')
print(post)
```

### Contact

Telegram: [@ItsFaBo](https://t.me/ItsFaBo)