import json
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.internet import reactor

class RoslibpyWebSocketProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print(f"Client connecting: {request.peer}")

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        try:
            if isBinary:
                print("Binary messages are not supported.")
                return

            message = json.loads(payload.decode('utf8'))
            print(f"Received message: {message}")
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON message: {e}")

    def onClose(self, wasClean, code, reason):
        print(f"WebSocket connection closed: {reason}")

class RoslibpyWebSocketServerFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = RoslibpyWebSocketProtocol

if __name__ == "__main__":
    # WebSocket server configuration
    ws_host = "0.0.0.0"
    ws_port = 9090

    print(f"Starting WebSocket server on ws://{ws_host}:{ws_port}")

    factory = RoslibpyWebSocketServerFactory(f"ws://{ws_host}:{ws_port}")
    reactor.listenTCP(ws_port, factory)

    # Start Twisted reactor loop
    print("WebSocket server running.")
    reactor.run()