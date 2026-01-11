from flask_socketio import SocketIO
from models.user import User
from models import mongo
import threading
import time

class RealtimeService:
    def __init__(self):
        self.socketio = SocketIO()  # Initialize SocketIO
        self.last_known_state = None  # Store the last known state of the data
        self.thread = None  # Thread for monitoring changes
        self.thread_stop = None  # Flag to stop the thread

    def init_app(self, app):
        self.socketio.init_app(app)  # Initialize SocketIO with the Flask app

        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')  # Log when a client connects
            self.start_monitoring()  # Start monitoring for changes

        def start_monitoring(self):
            if not self.thread:
                # Create and start a daemon thread to monitor changes
                self.thread = threading.Thread(target=self._check_for_changes)
                self.thread.daemon = True
                self.thread.start()

        def _check_for_changes(self):
            try:
                while not self.thread_stop:
                    # Monitor the 'users' collection in MongoDB
                    collection = mongo.db.users
                    current_data = list(collection.find({}, {'_id': 0}))

                    # If data has changed, emit an update event
                    if current_data != self.last_known_state:
                        self.last_known_state = current_data
                        self.socketio.emit('data_update', {'data': current_data})

                    time.sleep(1)  # Check for changes every second
            except Exception as e:
                print(f"Error in monitoring thread: {e}")
                time.sleep(5)  # Wait for 5 seconds before checking again

        def stop_monitoring(self):
            self.thread_stop = True  # Set the flag to stop the thread
            if self.thread:
                self.thread.join()  # Wait for the thread to finish

# Singleton instance of RealtimeService
realtime_service = RealtimeService()
#realtime_service.init_app(app)