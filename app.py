
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_migrate import Migrate
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timezone
from flask import jsonify, request
import random
import os
import secrets
from PIL import Image



app = Flask(__name__)
app.secret_key = '6b880aec9cf0aa3f080c2741ac93ade3f5791da31c307f0b07eeb180c5f7bc76'



basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mohamedalo437@gmail.com'
app.config['MAIL_PASSWORD'] = 'dbyk gytc ippv pstg' 
app.config['MAIL_DEFAULT_SENDER'] = 'mohamedalo437@gmail.com'



db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
mail = Mail(app)


def get_serializer():
    return URLSafeTimedSerializer(app.secret_key)



login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.init_app(app)


# --- User Model ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    date_joined = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    profile_image = db.Column(db.String(150), nullable=False, default='default.png')

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))



class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already exists. Please choose a different one.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already exists. Please choose a different one.")


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture')
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Username already taken.")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("Email already taken.")



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_image = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            stmt = db.select(User).filter_by(username=username.data)
            if db.session.execute(stmt).scalar():
                raise ValidationError('Username already taken.')

    def validate_email(self, email):
        if email.data != current_user.email:
            stmt = db.select(User).filter_by(email=email.data)
            if db.session.execute(stmt).scalar():
                raise ValidationError('Email already registered.')



def save_profile_picture(form_picture):
    picture_dir = os.path.join(app.root_path, 'static/profile_pics')
    os.makedirs(picture_dir, exist_ok=True)

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(picture_dir, picture_fn)

    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



asl_alphabet = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
asl_numbers = [str(i) for i in range(1, 11)]
asl_greetings = ["Hello", "Thank you", "Good morning", "Good night",
                 "How are you?", "I am fine", "My name is", "Nice to meet you"]
asl_days = ["Saturday","Sunday","Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday" ]



@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html',
        asl_alphabet=asl_alphabet,
        asl_numbers=asl_numbers,
        asl_greetings=asl_greetings,
        asl_days=asl_days
    )


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        stmt = db.select(User).filter_by(email=form.email.data)
        if db.session.execute(stmt).scalar():
            flash("Email already registered.", "danger")
            return render_template('register.html', form=form)

        stmt = db.select(User).filter_by(username=form.username.data)
        if db.session.execute(stmt).scalar():
            flash("Username already taken.", "danger")
            return render_template('register.html', form=form)

        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        stmt = db.select(User).filter_by(email=form.email.data)
        result = db.session.execute(stmt)
        user = result.scalar()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    image_file = url_for('static', filename='profile_pics/' + current_user.profile_image)
    return render_template('profile.html', image_file=image_file)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.profile_image.data:
            picture_file = save_profile_picture(form.profile_image.data)
            current_user.profile_image = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.profile_image)
    return render_template('edit_profile.html', form=form, image_file=image_file)


@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/sign-to-text')
def sign_to_text():
    return render_template('sign_to_text.html')

@app.route('/api/ai-text', methods=['POST'])
def ai_text():
    data = request.get_json()
    image_data = data.get('image')  # base64

   
    predicted_text = "Hello"  # هذا هيتبدل بالتحليل الحقيقي

    return jsonify({ "text": predicted_text })  
    
      
@app.route('/api/ai-sign', methods=['POST'])
def ai_sign():
    data = request.get_json()
    text = data.get('text', '').strip()
    
   
    video_url = "/static/videos/generated/demo_sign.mp4"
    
    return jsonify({
        "label": text,
        "video_url": video_url
    })



@app.route('/reset_password_otp_request', methods=['GET', 'POST'])
def reset_password_otp_request():
    if request.method == 'POST':
        email = request.form['email']
        stmt = db.select(User).filter_by(email=email)
        user = db.session.execute(stmt).scalar()
        if user:
            otp = str(random.randint(100000, 999999))
            session['reset_email'] = email
            session['reset_otp'] = otp
            session['otp_expiry'] = datetime.now(timezone.utc).timestamp() + 600
            session['otp_attempts'] = 0
            try:
                msg = Message(
                    subject="Password Reset OTP",
                    recipients=[email],
                    body=f"Your OTP is: {otp}"
                )
                mail.send(msg)
                flash("An OTP has been sent to your email.", "info")
                return redirect(url_for('reset_password_otp_verify'))
            except Exception as e:
                print(f"❌ Failed to send email: {e}")
                flash("Failed to send OTP.", "danger")
        else:
            flash("Email not found.", "danger")
    return render_template('reset_password_otp_request.html')


@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    if 'reset_email' not in session:
        flash("Session expired.", "danger")
        return redirect(url_for('reset_password_otp_request'))
    email = session['reset_email']
    stmt = db.select(User).filter_by(email=email)
    user = db.session.execute(stmt).scalar()
    if not user:
        flash("User not found.", "danger")
        session.pop('reset_email', None)
        return redirect(url_for('reset_password_otp_request'))
    otp = str(random.randint(100000, 999999))
    session['reset_otp'] = otp
    session['otp_expiry'] = datetime.now(timezone.utc).timestamp() + 600
    session['otp_attempts'] = 0
    try:
        msg = Message(
            subject="Password Reset OTP",
            recipients=[email],
            body=f"Your new OTP is: {otp}"
        )
        mail.send(msg)
        flash("A new OTP has been sent.", "info")
    except Exception as e:
        print(f"Failed to resend OTP: {e}")
        flash("Failed to resend OTP.", "danger")
    return redirect(url_for('reset_password_otp_verify'))


@app.route('/reset_password_otp_verify', methods=['GET', 'POST'])
def reset_password_otp_verify():
    if 'reset_email' not in session:
        flash("Request a new OTP.", "warning")
        return redirect(url_for('reset_password_otp_request'))
    now = datetime.now(timezone.utc).timestamp()
    if now > session.get('otp_expiry', 0):
        session.pop('reset_email', None)
        session.pop('reset_otp', None)
        session.pop('otp_attempts', None)
        flash("OTP expired.", "danger")
        return redirect(url_for('reset_password_otp_request'))
    if request.method == 'POST':
        entered_otp = request.form['otp']
        session['otp_attempts'] += 1
        if session['otp_attempts'] >= 5:
            session.pop('reset_email', None)
            session.pop('reset_otp', None)
            session.pop('otp_attempts', None)
            flash("Too many attempts.", "danger")
            return redirect(url_for('reset_password_otp_request'))
        if entered_otp == session.get('reset_otp'):
            return redirect(url_for('reset_password_set'))
        else:
            flash("Invalid OTP.", "danger")
    return render_template('reset_password_otp_verify.html')


@app.route('/reset_password_set', methods=['GET', 'POST'])
def reset_password_set():
    if 'reset_email' not in session:
        flash("Unauthorized.", "danger")
        return redirect(url_for('login'))
    if request.method == 'POST':
        password = request.form['password']
        email = session['reset_email']
        stmt = db.select(User).filter_by(email=email)
        user = db.session.execute(stmt).scalar()
        if user:
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')
            db.session.commit()
            session.pop('reset_email', None)
            session.pop('reset_otp', None)
            session.pop('otp_expiry', None)
            session.pop('otp_attempts', None)
            flash("Password reset!", "success")
            return redirect(url_for('login'))
    return render_template('reset_password_set.html')



@app.route('/letter/<letter>')
def letter_detail(letter):
    if letter not in asl_alphabet:
        flash("Letter not found.", "danger")
        return redirect(url_for('home'))
    return render_template('letter.html', letter=letter)


@app.route('/number/<num>')
def number_detail(num):
    if num not in asl_numbers:
        flash("Number not found.", "danger")
        return redirect(url_for('home'))
    return render_template('number.html', num=num)


@app.route('/phrase/<path:phrase>')
def phrase_detail(phrase):
    if phrase not in asl_greetings:
        flash("Phrase not found.", "danger")
        return redirect(url_for('home'))
    return render_template('phrase.html', phrase=phrase)


@app.route('/day/<day>')
def day_detail(day):
    if day not in asl_days:
        flash("Day not found.", "danger")
        return redirect(url_for('home'))
    return render_template('day.html', day=day)



@app.route('/test-pwa')
def test_pwa():
    return render_template('test_pwa.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")
    app.run(debug=True)