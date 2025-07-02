import jwt
import datetime
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import AccessDenied
import json
import logging

_logger = logging.getLogger(__name__)


SECRET_KEY = "YourSecretKey"  # Use a secure secret key in production


# Function to generate a JWT token
def generate_token(user_id, email, expiration_hours=1):
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expiration_hours),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


# Function to decode and validate a JWT token
def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise AccessDenied("Token has expired")
    except jwt.InvalidTokenError:
        raise AccessDenied("Invalid token")


# JWT decorator to protect routes
def jwt_required(func):
    def wrapper(*args, **kwargs):
        auth_header = request.httprequest.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                json.dumps({"error": "Missing or invalid token"}),
                status=401,
                mimetype="application/json",
            )

        token = auth_header.split(" ")[1]
        try:
            payload = decode_token(token)
            user = request.env["res.users"].sudo().browse(payload["sub"])
            _logger.info("payload['sub']: %s", payload.get("sub"))

            _logger.info("User: %s", user)
            _logger.info("User exists: %s", user.exists())

            if not user.exists():
                _logger.debug("tu")
                raise AccessDenied()
            request.user = user  # Attach authenticated user to the request
            request.env = request.env(user=user)  # Set Odoo environment user!
        except AccessDenied as e:
            return Response(
                json.dumps({"error": str(e)}), status=403, mimetype="application/json"
            )

        return func(*args, **kwargs)

    return wrapper
