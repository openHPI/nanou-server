from social_core.backends.oauth import BaseOAuth2


class OpenHPIOAuth2(BaseOAuth2):
    name = 'openhpi'
    AUTHORIZATION_URL = 'https://open.hpi.de/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://open.hpi.de/oauth/token'
    ACCESS_TOKEN_METHOD = 'POST'
    DEFAULT_SCOPE = ['profile']
    SCOPE_SEPARATOR = ','
    EXTRA_DATA = [
        ('user_id', 'user_id'),
        ('email', 'email'),
        ('full_name', 'fullname'),
        ('username', 'username'),
    ]

    def get_user_details(self, response):
        """Return user details from openHPI account"""
        fullname, first_name, last_name = self.get_user_names(
            response.get('full_name') or response.get('username') or ''
        )
        return {
            'username': response.get('username'),
            'fullname': fullname,
            'first_name': first_name,
            'last_name': last_name,
            'email': response.get('email', '')
        }

    def user_data(self, access_token, *args, **kwargs):
        """Grab user profile information from opneHPI"""
        return self.get_json(
            'https://open.hpi.de/oauth/api/user/',
            headers={'Authorization': 'Bearer %s' % access_token}
        )
