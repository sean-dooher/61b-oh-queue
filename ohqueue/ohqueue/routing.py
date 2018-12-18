from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
import backend_app.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': SessionMiddlewareStack(
        AuthMiddlewareStack(
            URLRouter(
                backend_app.routing.websocket_routing
            )
        )
    )
})