from flask import current_app
from models import mongo
from bson import ObjectId
from datetime import datetime

class LocationService:
    def update_victim_location(self, user_id, latitude, longitude, address=None, city=None):
        """
        Update the location of a victim
        """
        location_data = {
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': datetime.utcnow()
        }
        
        # Add address info if provided
        if address:
            location_data['address'] = address
        if city:
            location_data['city'] = city
        
        # Update the user document with the location information
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'location': location_data}}
        )
        
        # Also update the victim profile
        mongo.db.victims.update_one(
            {'user_id': ObjectId(user_id)},
            {'$set': {
                'current_location': location_data,
                'last_location_update': datetime.utcnow()
            }}
        )
        
        # Also store in separate locations collection for historical tracking
        location_entry = {
            'user_id': ObjectId(user_id),
            'latitude': latitude,
            'longitude': longitude,
            'address': address,
            'city': city,
            'timestamp': datetime.utcnow(),
            'source': 'auto'  # Mark as auto-detected
        }
        
        mongo.db.locations.insert_one(location_entry)
        return True
    
    def get_victim_location(self, user_id):
        """
        Get the most recent location of a victim
        """
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user and 'location' in user:
            return user['location']
        return None
    
    def get_all_victim_locations(self):
        """
        Get all victims with their most recent locations
        """
        users = mongo.db.users.find(
            {'role': 'victim', 'location': {'$exists': True}},
            {'_id': 1, 'username': 1, 'location': 1}
        )
        
        return list(users)
    
    def get_victim_location_history(self, user_id, limit=10):
        """
        Get location history for a victim
        """
        locations = mongo.db.locations.find(
            {'user_id': ObjectId(user_id)}
        ).sort('timestamp', -1).limit(limit)
        
        return list(locations)