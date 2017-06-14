from ..app import oauth
from ..util.config import config

oauth42 = oauth.remote_app('42',
	base_url = 'https://api.intra.42.fr',
	authorize_url='https://api.intra.42.fr/oauth/authorize',
	access_token_url="https://api.intra.42.fr/oauth/token",
	consumer_key = config.oauth.key,
	consumer_secret = config.oauth.secret
)
