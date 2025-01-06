import json
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.internet import reactor

# Define a simple WebSocket protocol class
class SimpleWebSocketProtocol(WebSocketServerProtocol):
    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                # Decode and print JSON message as a Python dictionary
                message = json.loads(payload.decode('utf8'))
                print(message)
            except json.JSONDecodeError:
                print("Received invalid JSON.")

if __name__ == "__main__":
    # Create a WebSocket server factory
    factory = WebSocketServerFactory("ws://0.0.0.0:9090")
    factory.protocol = SimpleWebSocketProtocol

    # Start listening for WebSocket connections
    reactor.listenTCP(9090, factory)
    print("WebSocket server running on ws://0.0.0.0:9090")
    reactor.run()