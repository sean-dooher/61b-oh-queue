from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
import backend.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': SessionMiddlewareStack(
        AuthMiddlewareStack(
            URLRouter(
                backend.routing.websocket_routing
            )
        )
    )
})