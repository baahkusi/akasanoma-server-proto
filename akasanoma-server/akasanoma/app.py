import falcon
import json
from .actions import actions
from .utils import handle_requests
from .db import PeeweeConnectionMiddleware
from .middlewares import SetUserMiddleware, CORSComponent


class Action():

    def __init__(self, actions):

        self.actions = actions

    def on_post(self, req, resp):
        payload = json.loads(req.stream.read(req.content_length or 0))
        
        resp.body = json.dumps(self.prepare_response(req, payload))

    def prepare_response(self, req, payload):
        return handle_requests(self.actions, req, payload)


api = application = falcon.API(
    middleware=[
        CORSComponent(),
        PeeweeConnectionMiddleware(),
        SetUserMiddleware(),
    ]
)

api.add_route('/action', Action(actions))
