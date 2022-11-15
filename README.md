# Link Cleaner
This is a simple Flask service that will take a link and attempt to "clean" it. That means it will follow redirects to its eventual end, try and remove known tracker query parameters, amd maybe more.

## Running
```shell
pip install -r requirements.txt
cd app
python -c "from db import CleanedLink, db; db.create_tables([CleanedLink])"
flask run
```

## Using
Just browse/send a GET request to `/clean/<url you want to clean>` and it'll return a clean link after a few seconds. Alternatively, send an `Accept: application/json` header and it will return a JSON dict with one key named `cleaned_url` containing the cleaned URL.

You can also browse to `/stats` to see a beautifully designed stats page.

This is running on Render at https://link-cleaner.onrender.com/, so it can be used like https://link-cleaner.onrender.com/clean/https://www.google.com for instance.