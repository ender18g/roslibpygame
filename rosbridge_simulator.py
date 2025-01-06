import json
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.internet import reactor, task

# Define a simple WebSocket protocol class
class SimpleWebSocketProtocol(WebSocketServerProtocol):
    def onOpen(self):
        # Start sending odometry messages when a connection is opened
        self.send_odometry_task = task.LoopingCall(self.send_odometry_message)
        self.send_odometry_task.start(1.0)  # Send odometry messages every second

    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                # Decode and print JSON message as a Python dictionary
                message = json.loads(payload.decode('utf8'))
                print(message)
            except json.JSONDecodeError:
                print("Received invalid JSON.")

    def send_odometry_message(self):
        # Example odometry message in JSON format, wrapped with 'op' key
        odometry_message = {
            "op": "publish",
            "topic": "/juliet/odom",
            "msg": {
                "header": {
                    "stamp": "1234567890.123456",
                    "frame_id": "odom"
                },
                "pose": {
                    "pose": {
                        "position": {"x": 1.0, "y": 2.0, "z": 0.0},
                        "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
                    }
                },
                "twist": {
                    "twist": {
                        "linear": {"x": 0.1, "y": 0.0, "z": 0.0},
                        "angular": {"x": 0.0, "y": 0.0, "z": 0.1}
                    }
                }
            }
        }
        self.sendMessage(json.dumps(odometry_message).encode('utf8'))

if __name__ == "__main__":
    # Create a WebSocket server factory
    factory = WebSocketServerFactory("ws://0.0.0.0:9090")
    factory.protocol = SimpleWebSocketProtocol

    # Start listening for WebSocket connections
    reactor.listenTCP(9090, factory)
    print("WebSocket server running on ws://0.0.0.0:9090")
    reactor.run()
