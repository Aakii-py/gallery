from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
mail = Mail(app)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    first_login = db.Column(db.Boolean, default=True)

# Account request model
class AccountRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    reason = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending/Approved/Declined

# File model
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_shared = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('gallery'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            if user.is_approved:
                login_user(user)
                if user.first_login:
                    return redirect(url_for('change_password'))
                return redirect(url_for('gallery'))
            flash('Your account is not approved yet!', 'danger')
        else:
            flash('Login failed. Check email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        reason = request.form['reason']
        existing_request = AccountRequest.query.filter_by(email=email).first()
        if existing_request:
            flash('Request already exists for this email.', 'danger')
        else:
            new_request = AccountRequest(name=name, email=email, reason=reason)
            db.session.add(new_request)
            db.session.commit()
            flash('Your registration request has been sent.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('gallery'))
    requests = AccountRequest.query.filter_by(status='Pending').all()
    users = User.query.all()
    return render_template('admin_dashboard.html', requests=requests, users=users)

@app.route('/admin/approve/<int:request_id>')
@login_required
def approve_request(request_id):
    if not current_user.is_admin:
        return redirect(url_for('gallery'))
    acc_request = AccountRequest.query.get_or_404(request_id)
    password = generate_password_hash('changeme123', method='sha256')
    user = User(username=acc_request.name, email=acc_request.email, password_hash=password, is_approved=True)
    db.session.add(user)
    acc_request.status = 'Approved'
    db.session.commit()

    # Send email notification
    msg = Message('Your Account is Approved!', recipients=[user.email])
    msg.body = f'''Hello {user.username},

Your account has been approved!

Default login password is: changeme123

Please login and update your password after login.

Thank you!
'''
    mail.send(msg)
    flash(f'Approved {user.username}. Email notification sent.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/decline/<int:request_id>')
@login_required
def decline_request(request_id):
    if not current_user.is_admin:
        return redirect(url_for('gallery'))
    acc_request = AccountRequest.query.get_or_404(request_id)
    acc_request.status = 'Declined'
    db.session.commit()
    flash('Request declined.', 'danger')
    return redirect(url_for('admin'))

@app.route('/gallery')
@login_required
def gallery():
    uploads = Upload.query.filter_by(owner_id=current_user.id).all()
    shared_uploads = Upload.query.filter_by(is_shared=True).all()
    return render_template('gallery.html', uploads=uploads, shared_uploads=shared_uploads)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            file.save(f'uploads/{filename}')
            new_upload = Upload(filename=filename, owner_id=current_user.id)
            db.session.add(new_upload)
            db.session.commit()
            flash(f'File {filename} uploaded successfully!', 'success')
            return redirect(url_for('gallery'))
    return render_template('upload.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('change_password'))
        current_user.password_hash = generate_password_hash(new_password, method='sha256')
        current_user.first_login = False
        db.session.commit()
        flash('Password changed successfully.', 'success')
        return redirect(url_for('gallery'))
    return render_template('change_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
