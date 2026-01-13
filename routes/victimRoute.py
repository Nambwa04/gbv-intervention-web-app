from flask import Blueprint, current_app, request, jsonify, render_template, redirect, session, url_for, flash
from models.responders import ResponderModel
from models.victim import VictimModel
from models.user import mongo, User, bcrypt
from bson import ObjectId 
from datetime import datetime
from services.victimService import VictimService
from models.decorators import role_required
from utils import generate_default_password 

# Add these imports if not already present
from models.emergency import EmergencyModel
from services.location_service import LocationService
from services.notification_service import NotificationService
from bson.objectid import ObjectId
from datetime import datetime

# Create Blueprint
victim_bp = Blueprint('victim', __name__)
victim_model = VictimModel(mongo)

victimService = VictimService()

# Initialize the services
emergency_model = EmergencyModel(mongo)
location_service = LocationService()
notification_service = NotificationService(mongo)

@victim_bp.route('/manage_victims', methods=['GET'])
@role_required('admin')
def manage_victims():
    try:
        # Use the VictimModel instance directly
        victims = victim_model.get_all_victims()
        
        # Process the data for display
        processed = []
        for victim in victims:
            victim_copy = dict(victim)
            if '_id' in victim_copy:
                victim_copy['_id'] = str(victim_copy['_id'])
            if 'user_id' in victim_copy:
                victim_copy['user_id'] = str(victim_copy['user_id'])
            processed.append(victim_copy)
        
        print(f"Found {len(processed)} victims")
        return render_template('victims.html', victims=processed)
    except Exception as e:
        print(f"Error in manage_victims: {str(e)}")
        flash(f"Error loading victims: {str(e)}", "error")
        return render_template('victims.html', victims=[])

@victim_bp.route('/add_victim', methods=['POST'])
def add_victim():
    try:
        # Extract form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        location = request.form.get('location')
        case_description = request.form.get('case_description', '')
        password = request.form.get('password', 'defaultPassword123')  # Add default password
        role = 'victim'

        # Create user account first (using full name for username)
        username = f"{first_name} {last_name}"
        user_result = User.register_user(username, email, password, role)
        
        if not user_result:
            flash("Failed to create user account", "error")
            return redirect(url_for('victim.manage_victims'))

        user_id = user_result.inserted_id
        print(f"Created user with ID: {user_id}")  # Debug log

        # Create victim profile
        victim_data = {
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "gender": gender,
            "location": location,
            "case_description": case_description,
            "created_at": datetime.now()
        }

        # Insert into victims collection using mongo directly
        mongo.db.victims.insert_one(victim_data)
        print(f"Created victim profile for user ID: {user_id}")  # Debug log

        flash("Victim added successfully!", "success")
        return redirect(url_for('victim.manage_victims'))

    except Exception as e:
        print(f"Error in add_victim: {str(e)}")  # Debug log
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('victim.manage_victims'))

@victim_bp.route('/edit_victim/<victim_id>', methods=['POST'])
def edit_victim(victim_id):
    try:
        # Collect all form data into a dictionary
        updated_data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'gender': request.form.get('gender'),
            'location': request.form.get('location'),
            'case_description': request.form.get('case_description')
        }
        
        # Validate that all required fields are provided
        if not all([updated_data['first_name'], updated_data['last_name'], updated_data['email'], 
                   updated_data['phone'], updated_data['gender'], updated_data['location']]):
            flash('All fields are required!', 'error')
            return redirect(url_for('victim.manage_victims'))
        
        print(f"Updating victim with ID: {victim_id}")
        print(f"Updated data: {updated_data}")
        
        # Use the update_victim method from VictimModel which supports _id directly
        result = victim_model.update_victim(victim_id, updated_data)
        
        if result.modified_count > 0:
            flash('Victim updated successfully', 'success')
        else:
            flash('No changes made or victim not found', 'error')
    except Exception as e:
        flash(f'Error updating victim: {str(e)}', 'error')
    return redirect(url_for('victim.manage_victims'))

@victim_bp.route('/delete_victim/<victim_id>', methods=['POST'])
@role_required('admin')
def delete_victim(victim_id):
    try:
        result = victim_model.delete_victim(victim_id)
        if result.deleted_count > 0:
            flash("Victim deleted successfully", "success")
        else:
            flash("Victim not found", "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    return redirect(url_for('victim.manage_victims'))

@victim_bp.route('/search_victim', methods=['GET'])
def search_victim():
    search_query = request.args.get('search_query', '').strip()
    gender = request.args.get('gender', '').strip()

    # Redirect if no search criteria are provided
    if not search_query and not gender:
        return redirect(url_for('victim.manage_victims'))

    # Search by query and/or gender
    victims = victimService.search_victims(search_query, gender)

    return render_template('victims.html', victims=victims)

# Add these routes for SOS functionality
@victim_bp.route('/sos', methods=['POST'])
def trigger_sos():
    """Trigger an SOS emergency alert"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    try:
        # Get the victim's current location if available
        location = location_service.get_victim_location(user_id)
        
        # Create an emergency case
        description = request.json.get('description', "Emergency SOS activated")
        case_id = emergency_model.create_emergency_case(user_id, location, description)
        
        # Notify all available responders
        responders = ResponderModel.get_available_responders()
        for responder in responders:
            notification_service.create_notification(
                responder['_id'],
                "EMERGENCY SOS ALERT",
                "A victim has triggered an emergency SOS alert. Immediate attention required.",
                "emergency",
                {"case_id": case_id}
            )
        
        return jsonify({
            "success": True, 
            "message": "SOS alert sent successfully",
            "case_id": case_id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error triggering SOS: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@victim_bp.route('/sos/history')
def sos_history():
    """View SOS history for the victim"""
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))
    
    try:
        # Get all emergency cases for this victim
        cases = emergency_model.get_cases_by_victim(user_id)
        
        return render_template("victim/sos_history.html", cases=cases)
        
    except Exception as e:
        flash(f"Error retrieving SOS history: {str(e)}", "error")
        return redirect(url_for('victim.dashboard'))