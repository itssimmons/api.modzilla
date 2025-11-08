from werkzeug.wrappers import Response
from addons.builder import Builder

import json
from typing import Callable, Any, Optional, Set, MutableMapping


class Auth:
    def __init__(self, wsgi_app: Callable[..., Any], urls: Optional[Set[str]] = None):
        self.wsgi_app = wsgi_app
        self.urls = urls

    def __call__(self, environ: MutableMapping[str, Any], start_response: Callable[..., Any]) -> Any:
        path = environ.get("PATH_INFO", "")

        if self.urls is None or any(path.startswith(url.rstrip("*")) for url in self.urls):
            auth_header = environ.get("HTTP_AUTHORIZATION", "")
            if not auth_header or not auth_header.startswith("Bearer "):
                res = Response(
                    json.dumps({
                        "exception": {
                            "message": "Unauthorized",
                            "code": "UNAUTHORIZED",
                            "details": {"path": path},
                        }
                    }),
                    mimetype="application/json",
                    status=401,
                )
                return res(environ, start_response)

            client_token = auth_header.split(" ", 1)[1]
            server_token = (Builder.query("tokens")
            .fields(['user_id'])
            .where(f"token = '{client_token}'")
            .limit(1)
            .read())

            if not server_token.exists:
                res = Response(
                    json.dumps({
                        "exception": {
                            "message": "Forbidden",
                            "code": "FORBIDDEN",
                            "details": {"path": path},
                        }
                    }),
                    mimetype="application/json",
                    status=403,
                )
                return res(environ, start_response)

        return self.wsgi_app(environ, start_response)