from models import mongo, User
from bson import ObjectId
from flask_mail import Message, Mail
from datetime import datetime

mail = Mail()

def generate_default_password():
    import random
    import string
    length = 8
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def send_password_email(email, password):
    msg = Message(
        subject="Your Account Password",
        sender="current_app.config['MAIL_USERNAME']",
        recipients=[email],
    )
    msg.body = f"Your account has been created. Your temporary password is: {password}"
    mail.send(msg)

class VictimService:
    def __init__(self):
        self.victims = mongo.db.victims
        self.cases = mongo.db.cases
        self.resources = mongo.db.resources
        self.messages = mongo.db.messages

    def get_all_victims(self):
        victims = list(self.victims.find())
        for victim in victims:
            victim['_id'] = str(victim['_id'])
        return victims

    def get_victim_profile(self, user_id):
        """Get or create victim profile"""
        try:
            profile = self.victims.find_one({"user_id": ObjectId(user_id)})
            if not profile:
                # Create default profile if it doesn't exist
                profile = self._create_default_profile(user_id)
            return profile
        except Exception as e:
            print(f"Error getting victim profile: {str(e)}")
            return None

    def _create_default_profile(self, user_id):
        try:
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                profile = {
                    "user_id": ObjectId(user_id),
                    "first_name": user.get("first_name", ""),
                    "last_name": user.get("last_name", ""),
                    "email": user.get("email", ""),
                    "phone": user.get("phone", ""),
                    "gender": user.get("gender", ""),
                    "location": "",
                    "case_description": "",
                    "location_sharing": False,
                    "created_at": datetime.now()
                }
                self.victims.insert_one(profile)
                return profile
        except Exception as e:
            print(f"Error creating default profile: {str(e)}")
            return None

    def create_victim_profile(self, user_id, username, email, phone, location="Unknown", gender="Unknown", case_description=""):
        if User.find_by_email(email):
            raise ValueError("Email already exists!")

        if not phone.isdigit() or len(phone) != 10:
            raise ValueError("Invalid phone number!")

        default_password = generate_default_password()

        User.register_user(username, email, default_password, role="victim")
        
        # Insert a new victim profile
        return self.victims.insert_one({
            "user_id": user_id,
            "username": username,
            "email": email,
            "phone": phone,
            "location": location,
            "gender": gender,
            "case_description": case_description
        })

    def update_victim_profile(self, user_id, update_data):
        """Update victim profile"""
        try:
            result = self.victims.update_one(
                {"user_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating victim profile: {str(e)}")
            return False

    def delete_victim_profile(self, victim_id):
        # Fetch the victim to get the user_id
        victim = self.victims.find_one({"_id": ObjectId(victim_id)})
        if not victim:
            raise ValueError("Victim not found")

        # Delete the corresponding user
        User.collection.delete_one({"_id": victim["user_id"]})  # Use the user_id from the victim document

        # Delete the victim profile
        return self.victims.delete_one({"_id": ObjectId(victim_id)})

    def search_victims(self, search_query=None, gender=None):
        # Build the dynamic query
        query = {"$or": []}

        # Try searching by ObjectId if the search query is a valid ID
        if search_query:
            try:
                if ObjectId.is_valid(search_query):
                    query["$or"].append({"_id": ObjectId(search_query)})
            except Exception as e:
                print(f"ObjectId error: {e}")

            # Search by username or email (case-insensitive)
            query["$or"].extend([
                {"username": {"$regex": search_query, "$options": "i"}},
                {"email": {"$regex": search_query, "$options": "i"}}
            ])

        # Filter by gender if provided (case-insensitive)
        if gender:
            query["gender"] = {"$regex": f"^{gender}$", "$options": "i"}

        # If no search criteria are provided, get all victims
        if not query["$or"]:
            query.pop("$or")

        # Execute the query and convert ObjectId to string
        victims = list(self.victims.find(query))
        for victim in victims:
            victim['_id'] = str(victim['_id'])

        return victims

    def get_victim_cases(self, user_id):
        try:
            return list(self.cases.find({"victim_id": ObjectId(user_id)}))
        except Exception as e:
            print(f"Error getting victim cases: {str(e)}")
            return []

    def get_victim_cases_with_details(self, user_id):
        """Get all cases for a victim with responder details"""
        try:
            # Get all cases for this victim
            cases = list(mongo.db.emergency_cases.find({"victim_id": ObjectId(user_id)}))
            
            # Add responder details to each case
            for case in cases:
                if 'responder_id' in case and case['responder_id']:
                    responder = mongo.db.responders.find_one({"user_id": case['responder_id']})
                    if responder:
                        case['responder_name'] = responder.get('name', 'Unknown Responder')
                
                # Ensure _id is string
                case['_id'] = str(case['_id'])
                
            return cases
        except Exception as e:
            print(f"Error getting victim cases with details: {str(e)}")
            return []

    def get_available_resources(self):
        try:
            return list(self.resources.find({}))
        except Exception as e:
            print(f"Error getting resources: {str(e)}")
            return []

    def get_victim_messages(self, user_id):
        try:
            return list(self.messages.find({'room': 'victim_to_responder'}).sort("timestamp", 1))
        except Exception as e:
            print(f"Error getting messages: {str(e)}")
            return []

    def update_victim_location(self, user_id, location_data):
        try:
            result = self.victims.update_one(
                {"user_id": ObjectId(user_id)},
                {"$set": location_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating location: {str(e)}")
            return False

    def send_message(self, user_id, content):
        try:
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            message = {
                "sender_id": ObjectId(user_id),
                "sender_username": user["username"],
                "content": content,
                "timestamp": datetime.now()
            }
            self.messages.insert_one(message)
            return True
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False

# Instantiate VictimService
victimService = VictimService()