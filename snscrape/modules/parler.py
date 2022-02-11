__all__ = []

import collections
import dataclasses
import snscrape.base
import typing
import logging

_logger = logging.getLogger(__name__)

@dataclasses.dataclass
class Post(snscrape.base.Item):
    '''An object representing one post.

    Most fields can be None if not known.
    '''

    V2LINKLONG: str
    # FIXME: audio_data missing because I don't know what it does
    url: str
    badges: 'Badges'
    body: str
    # disgusting. snake_case mixed with camelCase
    commentCount = int
    # FIXME: add commented
    date_created: str # FIXME: maybe make this a datetime?
    detected_language: str # what is this for?
    domain_name: str
    echoCount: int # ???
    # FIXME: Add echoed, echoedWithCommentId, echoedWithoutCommentId
    edited: bool
    # FIXME: add embed_data
    full_body: str
    has_audio: bool
    has_embed: bool
    has_image: bool
    has_video: bool
    id: int
    image: str
    image_data: str
    image_nsfw: bool
    is_echo: bool #?
    link: list # represented as a str, though, so we'll have to parse that
    long_link: str
    name: str
    profile_photo: str
    sensitive: bool
    time_ago: str
    title: str
    trolling: bool # don't even ask bc i don't know
    upvoted: bool # presumably a bool if you're logged in, but snscrape doesn't do that
    username: str
    userv4uuid: str
    uuid: str
    v4uuid: str
    # FIXME: add video, video_data
    # video and video_data might be the same as image and image_data
    voteCount: int

@dataclasses.dataclass
class Badges(snscrape.base.Item):
    gold: bool
    rss: bool
    private: bool
    early: bool
    parler_official: bool
    verified: bool
    parler_emp: bool

@dataclasses.dataclass
class Badge:
    '''Meant for use in allBadges
    '''

    name: str
    icon: str
    title: str
    description: str

class _ParlerAPIScraper(snscrape.base.Scraper):
    '''Base class for all other Parler scraper classes.'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._apiHeaders = {
                'Accept-Language': 'en-US,en;q=0.9',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.420 Safari/537.69',
        }

    def _check_api_response(self, r):
        if r.status_code != 200:
            return False, "non-200 status code"
        return True, None

    def _get_api_data(self, endpoint, data):
        r = self._post(endpoint, data = data, headers = self._apiHeaders, responseOkCallback = self._check_api_response)
        try:
            obj = r.json()
        except json.JSONDecodeError as e:
            raise snscrape.base.ScraperException('Received invalid JSON from Parler') from e
        return obj

class ParlerProfileScraper(_ParlerAPIScraper):
    '''Scraper class, designed to scrape a Parler user.'''

    name = 'parler-user'

    def __init__(self, username, **kwargs):
        '''
        Args:
            username: Username of user to scrape. This is NOT their display name.

        Raises:
            ValueError: When username is invalid.
        '''

        self._is_valid_username
        super().__init__(**kwargs)
        self._username = username
        self._apiHeaders['user'] = self._username

    def _is_valid_username(self):
        if not self._username.strip():
            raise ValueError('empty query')
        # FIXME: add more checks for invalid username

    def get_items(self) -> typing.Iterator[Post]:
        '''Get posts according to the specifications given when instantiating this scraper.

        Raises:
            ValueError, if the username is invalid
        Yields:
            Individual post.
        Returns:
            An iterator of posts.

        Note:
            This method is a generator. The number of tweets is not known beforehand.
            Please keep in mind that the scraping results can potentially be a lot of posts.
        '''

        self._is_valid_username()
        previous_page = 0
        current_page = 1
        page = 1
        data = {}
        data['user'] = (self._username)
        while True:
            data['page'] = (page)
            if data['page'] == 1:
                del data['page']
            #current_page = requests.post("https://parler.com/open-api/profile-feed.php", files=data).text
            current_page = self._get_api_data("https://parler.com/open-api/profile-feed.php", data)
            if previous_page == current_page:
                break
            previous_page = current_page
            page += 1
            yield current_page
