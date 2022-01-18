from flask_restful import Resource
from http import HTTPStatus


class LivenessResource(Resource):
    def get(self):

        return {"live": "true"}, HTTPStatus.OK
