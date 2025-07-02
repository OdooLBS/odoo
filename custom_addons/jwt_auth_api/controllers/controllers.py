import jwt
from odoo import http
from odoo.http import request, Response
import json
import logging
from ..utils.jwt_auth import generate_token, jwt_required  # Import utils functions

SECRET_KEY = "YourSecretKey"  # Use a secure secret key in production


_logger = logging.getLogger(__name__)


class JWTAuthController(http.Controller):

    @http.route("/api/auth/login", type="http", auth="none", csrf=False)
    def login(self, **kwargs):
        try:
            data = request.get_json_data()

            _logger.info("Received login request with data: %s", data)

            email = data.get("email")
            password = data.get("password")
            db = data.get("db")

            if not email or not password:
                return Response(
                    json.dumps({"error": "Email and password are required"}),
                    status=400,
                    mimetype="application/json",
                )

            # Validate user
            user = (
                request.env["res.users"].sudo().search([("login", "=", email)], limit=1)
            )

            _logger.info("User: %s", user.id)

            if user:
                credential = {"login": email, "password": password, "type": "password"}
                request.session.authenticate(db, credential)
                token = generate_token(user.id, user.login)
                return Response(
                    json.dumps({"token": token}),
                    status=200,
                    mimetype="application/json",
                )
            else:
                return Response(
                    json.dumps({"error": "Invalid credentials"}),
                    status=401,
                    mimetype="application/json",
                )

        except Exception as e:
            _logger.error(f"Error during login: {str(e)}", exc_info=True)
            return Response(
                json.dumps({"error": "Internal server error"}),
                status=500,
                mimetype="application/json",
            )

    @http.route("/api/auth/refresh", type="http", auth="none", csrf=False)
    def refresh_token(self, **kwargs):
        try:
            data = request.get_json_data()
            token = data.get("token")

            if not token:
                return Response(
                    json.dumps({"error": "Token is required"}),
                    status=400,
                    mimetype="application/json",
                )

            # Decode the token without verifying its expiration
            payload = jwt.decode(
                token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False}
            )

            # Generate a new token with a refreshed expiration time
            new_token = generate_token(payload["sub"], payload["email"])

            return Response(
                json.dumps({"token": new_token}),
                status=200,
                mimetype="application/json",
            )

        except jwt.ExpiredSignatureError:
            return Response(
                json.dumps({"error": "Token has expired"}),
                status=403,
                mimetype="application/json",
            )
        except jwt.InvalidTokenError:
            return Response(
                json.dumps({"error": "Invalid token"}),
                status=403,
                mimetype="application/json",
            )
        except Exception as e:
            _logger.error(f"Error during token refresh: {str(e)}", exc_info=True)
            return Response(
                json.dumps({"error": "Internal server error"}),
                status=500,
                mimetype="application/json",
            )


# Protected route
class JWTProtectedController(http.Controller):

    @http.route("/api/protected", type="http", auth="none", csrf=False)
    @jwt_required
    def protected_resource(self, **kwargs):
        user = request.user  # Access the authenticated user
        return Response(
            json.dumps(
                {"message": f"Welcome {user.name}, this is a protected resource!"}
            ),
            status=200,
            mimetype="application/json",
        )
