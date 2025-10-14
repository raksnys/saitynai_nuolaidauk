from drf_spectacular.extensions import OpenApiAuthenticationExtension

class JWTCookieAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = 'users.helpers.JWTAuthentication.JWTAuthentication'
    name = 'jwtCookieAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'jwt',
        }
