# Confiant Assignment Search API

_by Tural Mahmudov <nima.bavari@gmail.com>_

Time taken: 4 hours

## Scripts

Run

```sh
chmod +x ./lint.sh
./lint.sh
```

to lint and format the code in this project.

Run `docker-compose up search_api` to start the REST API.

Run `docker-compose up test` to run the tests.

## Example Use

Once you spin up the app, navigate to `/search` with query parameters, e.g. `GET /search?language=HTML&keyword=advertisement`.

Order of the query parameters don't matter.
