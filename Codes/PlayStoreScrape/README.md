# google-play-api

Turns [google-play-scraper](https://github.com/facundoolano/google-play-scraper/) into a RESTful API.

To run locally:

```
npm install
npm start
```

## Example requests

The parameters for each endpoint are taken directly from google-play-scraper. For a full reference check its [documentation](https://github.com/facundoolano/google-play-scraper/#usage).

Get an app's reviews

```http
GET /api/apps/org.wikipedia/reviews/
```

