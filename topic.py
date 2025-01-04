class Topic:
    def __new__(cls, ros_instance, topic_name, message_type):
        # check if the topic already exists and return it!
        if topic_name in ros_instance.topic_dict:
            return ros_instance.topic_dict[topic_name]
        else:
            # otherwise create a new topic
            return super(Topic, cls).__new__(cls)
    

    def __init__(self, ros_instance, topic_name, message_type):
        self.ros = ros_instance
        self.topic_name = topic_name
        self.message_type = message_type
        # add the topic to the ros instance
        self.ros.add_topic(self)
        self.callbacks = []
        self.msg = None

    def publish(self, message):
        self.msg = message
        # msg is set, now we can call the callback functions
        if self.callbacks:
            [callback(self.msg) for callback in self.callbacks]


    def subscribe(self, callback):
        # add the callback to the topic
        self.callback = callback