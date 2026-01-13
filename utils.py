import secrets
import string
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_mail import Message
from config import Config
from flask import current_app, url_for
from bson import ObjectId
from datetime import datetime
from models import mongo, mail
from models.user import User

def generate_default_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def verify_reset_token(token, max_age=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=max_age)
        return email

    except(BadSignature, SignatureExpired):
        return None

def send_reset_email(to_email, token):
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    msg = Message("Password Reset Request",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[to_email])
    msg.body = f"To reset your password, click the following link: {reset_url}\n\nIf you did not request a password reset, please ignore this email."
    
    try:
        mail.send(msg)
        print(f"Password reset email sent to {to_email}")
    except Exception as e:
        # Log the reset URL for development/testing when email fails
        print(f"Failed to send email: {str(e)}")
        print(f"\n{'='*60}")
        print(f"DEVELOPMENT MODE: Password Reset Link")
        print(f"{'='*60}")
        print(f"Email: {to_email}")
        print(f"Reset URL: {reset_url}")
        print(f"{'='*60}\n")
        # Re-raise if not a network error, otherwise allow the flow to continue
        if "Network is unreachable" not in str(e) and "Connection refused" not in str(e):
            raise

def ensure_user_profile(user_id, role):
    """Ensure a user has a profile in their role-specific collection"""
    try:
        user = User.find_by_id(ObjectId(user_id))
        if not user:
            return False

        collection_map = {
            'responder': mongo.db.responders,
            'victim': mongo.db.victims,
            'organization': mongo.db.organizations
        }

        collection = collection_map.get(role.lower())
        if not collection:
            return False

        # Check if profile exists
        profile = collection.find_one({"user_id": ObjectId(user_id)})
        if not profile:
            # Create basic profile
            profile_data = {
                "user_id": ObjectId(user_id),
                "name": user.get("username", ""),
                "email": user.get("email", ""),
                "created_at": datetime.now()
            }
            collection.insert_one(profile_data)
        return True
    except Exception as e:
        print(f"Error ensuring user profile: {str(e)}")
        return False