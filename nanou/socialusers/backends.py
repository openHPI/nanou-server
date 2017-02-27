from social_core.backends.oauth import BaseOAuth2


class OpenHPIOAuth2(BaseOAuth2):
    name = 'openhpi'
    AUTHORIZATION_URL = 'https://open.hpi.de/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://open.hpi.de/oauth/access_token'
    DEFAULT_SCOPE = ['profile']
    SCOPE_SEPARATOR = ','
