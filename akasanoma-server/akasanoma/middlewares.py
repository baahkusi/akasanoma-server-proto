from .db import User, Login

class SetUserMiddleware(object):
    def process_request(self, req, resp):
        """Process the request before routing it.

        Note:
            Because Falcon routes each request based on req.path, a
            request can be effectively re-routed by setting that
            attribute to a new value from within process_request().

        Args:
            req: Request object that will eventually be
                routed to an on_* responder method.
            resp: Response object that will be routed to
                the on_* responder.

        Adds: Sets req.user
        """

        token = req.get_header('Authorization')
        email = req.get_header('Account-ID')
        if token is None:
            req.user = None
        else:
            try:
                login = Login.get(token=token)
                user = User.get(email=email)
                if user.id == login.user.id:
                    req.user = user
                else:
                    req.user = None
            except Exception as e:
                print(e)
                req.user = None


class CORSComponent(object):
    def process_response(self, req, resp, resource, req_succeeded):
        resp.set_header('Access-Control-Allow-Origin', '*')

        if (req_succeeded
            and req.method == 'OPTIONS'
            and req.get_header('Access-Control-Request-Method')
        ):
            # NOTE(kgriffs): This is a CORS preflight request. Patch the
            #   response accordingly.

            allow = resp.get_header('Allow')
            resp.delete_header('Allow')

            allow_headers = req.get_header(
                'Access-Control-Request-Headers',
                default='*'
            )

            resp.set_headers((
                ('Access-Control-Allow-Methods', allow),
                ('Access-Control-Allow-Headers', allow_headers),
                ('Access-Control-Max-Age', '86400'),  # 24 hours
            ))