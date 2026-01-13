from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify, current_app
from models import mongo
from models.user import User
from services.victimService import victimService
from models.decorators import role_required
from bson import ObjectId
from datetime import datetime
from services.location_service import LocationService
from services.sos_service import SOSService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

victimProfile_bp = Blueprint('victimProfile', __name__)

# Initialize services
location_service = LocationService()
sos_service = SOSService()

@victimProfile_bp.route('/profile')
@role_required('victim')
def profile():
    try:
        user_id = session.get("user_id")
        if not user_id:
            flash("You need to login first", "error")
            return redirect(url_for('auth.login'))
        
        print(f"Looking up profile for user_id: {user_id}")
        user = User.find_by_id(ObjectId(user_id))
        profile_data = victimService.get_victim_profile(user_id)
        
        # Get cases with responder details
        cases = victimService.get_victim_cases_with_details(user_id)
        
        # Get resources
        resources = victimService.get_available_resources()
        
        # Get messages
        messages = victimService.get_victim_messages(user_id)
        
        print(f"User data: {user}")
        print(f"Profile data: {profile_data}")
        
        return render_template('victim_profile.html', 
                             profile=profile_data, 
                             user=user,
                             cases=cases,
                             resources=resources,
                             messages=messages)
    except Exception as e:
        print(f"Error in profile route: {str(e)}")
        flash("Error loading profile", "error")
        return redirect(url_for('auth.login'))

@victimProfile_bp.route('/update_profile', methods=['POST'])
@role_required('victim')
def update_profile():
    try:
        user_id = session.get("user_id")
        
        # Get phone - prefer full_phone if available, otherwise use phone
        phone = request.form.get('full_phone') or request.form.get('phone')
        
        update_data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'phone': phone,
            'gender': request.form.get('gender')
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if victimService.update_victim_profile(user_id, update_data):
            flash("Profile updated successfully", "success")
        else:
            flash("Error updating profile", "error")
            
        return redirect(url_for('victimProfile.profile'))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('victimProfile.profile'))

@victimProfile_bp.route('/change_password', methods=['POST'])
@role_required('victim')
def change_password():
    try:
        user_id = session.get("user_id")
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        user = User.find_by_id(ObjectId(user_id))
        if not User.verify_password(user, current_password):
            flash("Current password is incorrect", "error")
            return redirect(url_for('victimProfile.profile'))
        
        if User.update_password(user_id, new_password):
            flash("Password updated successfully", "success")
        else:
            flash("Error updating password", "error")
            
        return redirect(url_for('victimProfile.profile'))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('victimProfile.profile'))

@victimProfile_bp.route('/update_location', methods=['POST'])
@role_required('victim')
def update_location():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'success': False, 'error': 'Invalid location data'}), 400
        
        latitude = data['latitude']
        longitude = data['longitude']
        
        # Update location in database
        location_service.update_victim_location(user_id, latitude, longitude)
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating location: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Get messages
@victimProfile_bp.route('/get_messages', methods=['GET'])
@role_required('victim')
def get_messages():
    try:
        user_id = session.get("user_id")
        messages = list(mongo.db.messages.find({'room': 'victim_to_responder'}))
        for message in messages:
            message['_id'] = str(message['_id'])
            message['user_id'] = str(message['user_id'])
            message['timestamp'] = message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'messages': messages})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Send message
@victimProfile_bp.route('/send_message', methods=['POST'])
@role_required('victim')
def send_message():
    try:
        user_id = session.get("user_id")
        username = session.get("username")
        message_content = request.form.get('message')
        
        mongo.db.messages.insert_one({
            'user_id': ObjectId(user_id),
            'username': username,
            'room': 'victim_to_responder',
            'message': message_content,
            'timestamp': datetime.utcnow()
        })
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# SOS alert endpoint
@victimProfile_bp.route('/sos', methods=['POST'])
def trigger_sos():
    """Trigger an SOS emergency alert"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    try:
        # Get request data
        data = request.json
        description = data.get('description', "Emergency SOS activated")
        location = data.get('location')
        
        # Get victim info
        victim = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        victim_name = victim.get('username', 'Unknown') if victim else 'Unknown victim'
        
        # Create an emergency case - MAKE SURE THESE FIELDS MATCH EXACTLY
        emergency_case = {
            "victim_id": ObjectId(user_id),
            "victim_name": victim_name,
            "status": "PENDING",  # Must be exactly "PENDING" (all caps)
            "priority": "HIGH",   # Must be exactly "HIGH" (all caps)
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "description": description,
            "location": location,
            "responder_id": None,  # Must be None (Python None), not a string
            "responder_name": None
        }
        
        # Insert the emergency case
        result = mongo.db.emergency_cases.insert_one(emergency_case)
        case_id = str(result.inserted_id)
        
        # Debug print to confirm fields match query
        print(f"Created SOS case with ID: {case_id}")
        print(f"Case status: {emergency_case['status']}")
        print(f"Case priority: {emergency_case['priority']}")
        print(f"Case responder_id: {emergency_case['responder_id']}")
        
        # Rest of your notification code...
        
        return jsonify({
            "success": True, 
            "message": "SOS alert sent successfully",
            "case_id": case_id
        }), 200
        
    except Exception as e:
        print(f"Error triggering SOS: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500