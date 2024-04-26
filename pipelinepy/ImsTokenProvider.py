import os
import requests
import time
from kafka.oauth.abstract import AbstractTokenProvider


class ImsTokenProvider(AbstractTokenProvider):
    IMS_PATH = "/ims/token/v1"
    TOKEN_TTL_MAX_TOLERANCE_MS = 300_000  # 5 minutes

    def __init__(self, **config):
        self.ims_url = os.environ['IMS_URL'] + ImsTokenProvider.IMS_PATH
        self.ims_client_id = os.environ['IMS_CLIENT_ID']
        self.ims_client_secret = os.environ['IMS_CLIENT_SECRET']
        self.ims_client_code = os.environ['IMS_CLIENT_CODE']
        self._token = {}
        super().__init__(**config)

    def token(self):
        if ImsTokenProvider._expired(self._token):
            token = self._get_token()
            now = ImsTokenProvider._now()
            self._token = {
                'access_token': token['access_token'],
                'expiration_time_ms': now + token['expires_in'] - ImsTokenProvider.TOKEN_TTL_MAX_TOLERANCE_MS
            }
        return self._token['access_token']

    def _get_token(self):
        data = {
            'grant_type': 'authorization_code',
            'code': self.ims_client_code,
            'client_id': self.ims_client_id,
            'client_secret': self.ims_client_secret
        }
        response = requests.post(self.ims_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        response.raise_for_status()
        return response.json()

    @classmethod
    def _expired(cls, token):
        now = ImsTokenProvider._now()
        if 'expiration_time_ms' not in token:
            return True
        if token['expiration_time_ms'] < now:
            return True
        return False

    @classmethod
    def _now(cls):
        return int(time.time() * 1_000)
