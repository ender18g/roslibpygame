import json
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.internet import reactor

# Define a WebSocket protocol class that handles WebSocket events
class RoslibpyWebSocketProtocol(WebSocketServerProtocol):
    # Called when a client connects to the server
    def onConnect(self, request):
        print(f"Client connecting: {request.peer}")

    # Called when the WebSocket connection is opened
    def onOpen(self):
        print("WebSocket connection open.")

    # Called when a message is received from the client
    def onMessage(self, payload, isBinary):
        try:
            if isBinary:
                print("Binary messages are not supported.")
                return

            # Decode the JSON message
            message = json.loads(payload.decode('utf8'))
            print(f"Received message: {message}")
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON message: {e}")

    # Called when the WebSocket connection is closed
    def onClose(self, wasClean, code, reason):
        print(f"WebSocket connection closed: {reason}")

# Define a WebSocket server factory class that creates protocol instances
class RoslibpyWebSocketServerFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = RoslibpyWebSocketProtocol

if __name__ == "__main__":
    # WebSocket server configuration
    ws_host = "0.0.0.0"  # Listen on all available interfaces
    ws_port = 9090       # Port to listen on

    print(f"Starting WebSocket server on ws://{ws_host}:{ws_port}")

    # Create a WebSocket server factory
    factory = RoslibpyWebSocketServerFactory(f"ws://{ws_host}:{ws_port}")
    # Listen for incoming TCP connections on the specified port
    reactor.listenTCP(ws_port, factory)

    # Start the Twisted reactor loop to handle events
    print("WebSocket server running.")
    reactor.run()