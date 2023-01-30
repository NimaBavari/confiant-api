import requests
from flask import Flask, request
from flask_caching import Cache
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from sqlalchemy.sql import func

API_URL_TEMPLATE = "https://api.github.com/search/code?q=%s+in:file+language:%s+repo:microsoft/vscode"
HEADERS = {"Accept": "application/vnd.github.v3+json"}
DATABASE_URI = "sqlite:///confiant.db"
CACHE_TYPE = "RedisCache"
CACHE_REDIS_URL = "redis://redis:6379/0"
CACHE_DEFAULT_TIMEOUT = 500

app = Flask(__name__)
app_config_dict = {"DATABASE_URI": DATABASE_URI, "DEBUG": True}
app.config.from_mapping(app_config_dict)
cache = Cache(
    app,
    config={
        "CACHE_TYPE": CACHE_TYPE,
        "CACHE_REDIS_URL": CACHE_REDIS_URL,
        "CACHE_DEFAULT_TIMEOUT": CACHE_DEFAULT_TIMEOUT,
    },
)

Base = declarative_base()


class Search(Base):
    __tablename__ = "searches"

    id = Column(Integer, primary_key=True)
    client_ip = Column(String(15), nullable=False)
    search_language = Column(String, nullable=False)
    search_keyword = Column(String, nullable=False)
    exact_datetime = Column(DateTime(timezone=True), server_default=func.now())


engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(bind=engine))
sess = Session()


@app.teardown_appcontext
def teardown_db(resp_or_exc):
    Session.remove()


@app.route("/search", methods=["GET"])
@cache.cached(query_string=True)
def search():
    """Search service.

    Front-end app requests here with the searched keyword and the name of the language tab,
    e.g. `GET /search?language=HTML&keyword=advertisement`.

    Note that the order of the query params doesn't matter.
    """
    if "language" not in request.args or "keyword" not in request.args:
        return {"message": "Bad request: missing args."}, 400

    language = request.args["language"]
    keyword = request.args["keyword"]
    if len(request.args) > 2:
        return {"message": "Bad request: too many args."}, 400

    languages = ["javascript", "css", "html"]
    if language.lower() not in languages:
        return {"message": "Forbidden."}, 401

    client_ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)  # in case of proxy usage

    new_search = Search(client_ip=client_ip, search_language=language, search_keyword=keyword)
    sess.add(new_search)
    sess.commit()

    resp = requests.get(API_URL_TEMPLATE % (keyword, language), headers=HEADERS)
    return resp.json(), resp.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
