from social.backends.open_id import OpenIdAuth


class HpiOpenIdAuth(OpenIdAuth):
    name = 'hpi-openid'
    URL = 'https://openid.hpi.uni-potsdam.de/'
