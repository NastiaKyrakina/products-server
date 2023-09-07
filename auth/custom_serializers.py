import logging
import math

from dj_rest_auth.serializers import LoginSerializer
import base64

class CustomLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        logger = logging.getLogger('django')
        logger.info("User "+ attrs.get("username")+ " Log into system")
        password = attrs.get('password')
        password = base64.b64decode(password).decode("utf-8")
        attrs['password'] = password
        return super().validate(attrs)