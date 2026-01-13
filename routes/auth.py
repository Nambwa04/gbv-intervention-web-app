from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User, bcrypt
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from services.victimService import victimService
from utils import generate_reset_token, send_reset_email, verify_reset_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name", "")
        last_name = request.form.get("last_name", "")
        email = request.form.get("email", "")
        phone = request.form.get("full_phone") or request.form.get("phone", "")
        gender = request.form.get("gender", "")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Checking if user exists
        if User.find_by_email(email):
            flash("Email already exists", "danger")
            return redirect(url_for("auth.register"))

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("auth.register"))

        try:
            # Create new user with first_name and last_name
            user = User.register_user(f"{first_name} {last_name}", email, password, role="victim")
            user_id = user.inserted_id  # Ensure correct user_id retrieval
            
            print("Newly Registered User ID:", user_id)  # Debugging line

            # Create victim profile with new fields
            victimService.victims.insert_one({
                "user_id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "gender": gender,
                "location": "",
                "case_description": ""
            })

            print(request.form)  # Debugging line

            flash("Account created successfully", "success")
            return redirect(url_for("auth.login"))

        except DuplicateKeyError:
            flash("Username or Email already exists", "danger")
            return redirect(url_for("auth.register"))
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.find_by_email(email)
        
        if not user:
            print(f"User not found for email: {email}")  # Debug log
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

        if not User.verify_password(user, password):
            print(f"Password verification failed for user: {email}")  # Debug log
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

        # Store user details in session
        session["user_id"] = str(user["_id"])
        session["username"] = user.get("username", "")
        session["email"] = email
        session["role"] = user["role"].lower()

        print(f"Login successful - User ID: {session['user_id']}, Role: {session['role']}")  # Debug log

        # Redirect based on role
        try:
            if session["role"] == "admin":
                return redirect(url_for("admin.dashboard"))
            elif session["role"] == "responder":
                return redirect(url_for("responderProfile.profile"))
            elif session["role"] == "organization":
                return redirect(url_for("organizationProfile.profile"))
            elif session["role"] == "victim":
                return redirect(url_for("victimProfile.profile"))
            else:
                flash("Invalid role", "danger")
                return redirect(url_for("auth.login"))
        except Exception as e:
            print(f"Error during role redirect: {str(e)}")  # Debug log
            flash("Error during login", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return render_template("frontpage.html")

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash("Please enter your email address.", "error")
            return render_template('forgot_password.html')
        
        user = User.find_by_email(email)
        if user:
            try:
                # Generate a password reset token
                reset_token = generate_reset_token(user['email'])
                # Send the reset email
                send_reset_email(user['email'], reset_token)
                flash("Password reset link sent to your email. Please check your inbox.", "success")
            except Exception as e:
                print(f"Error sending reset email: {str(e)}")
                flash("An error occurred while sending the reset email. Please try again later.", "error")
                return render_template('forgot_password.html')
        else:
            # For security, don't reveal whether the email exists
            flash("If an account with that email exists, a password reset link has been sent.", "success")
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html')

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')
    if not token:
        flash("Invalid or missing token.", "error")
        return redirect(url_for('auth.forgot_password'))

    email = verify_reset_token(token)
    if not email:
        flash("Invalid or expired token. Please request a new password reset link.", "error")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validate password length
        if len(new_password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template('reset_password.html', token=token)

        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('reset_password.html', token=token)

        # Update the user's password
        user = User.find_by_email(email)
        if user:
            try:
                # Pass the plain password to update_password
                User.update_password(user['_id'], new_password)
                flash("Your password has been reset successfully. You can now log in with your new password.", "success")
                return redirect(url_for('auth.login'))
            except Exception as e:
                print(f"Error updating password: {str(e)}")
                flash("An error occurred while resetting your password. Please try again.", "error")
                return render_template('reset_password.html', token=token)
        flash("User not found.", "error")
    return render_template('reset_password.html', token=token)
