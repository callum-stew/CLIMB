import functools
from secrets import token_urlsafe

from flask import Blueprint, request, redirect, url_for, render_template, session, flash, g, abort
from werkzeug.security import check_password_hash, generate_password_hash

from CLIMB.CLIMB_data import person_from_email, person_from_id, create_person
from CLIMB import email

auth_bp = Blueprint('auth_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


def login_required(view):
    """ Wrapper to require a logged in user """

    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth_bp.login'))  # redirect to login page if not logged in

        return view(**kwargs)

    return wrapped_view


def permission_required(permission_name):
    """ Wrapper to check that person has permission """

    def decorator(view):

        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                return redirect(url_for('auth_bp.login'))
            if not g.user.has_permission(permission_name):
                abort(403)

            return view(**kwargs)

        return wrapped_view
    
    return decorator


@auth_bp.before_app_request
def load_logged_in_user():
    """ Adds user_id to request context"""

    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        try:
            g.user = person_from_id(user_id)
        except KeyError:
            g.user = None
            session.clear()
            return redirect(url_for('auth_bp.login'))



@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    """ Customer registration page """

    if request.method == 'POST':
        # Create member
        try:
            member = create_person('MEMBER')
            member.first_name = request.form['first_name']
            member.middle_name = request.form['middle_name']
            member.last_name = request.form['last_name']
            member.address_line_1 = request.form['address_line_1']
            member.address_line_2 = request.form['address_line_2']
            member.address_line_3 = request.form['address_line_3']
            member.county = request.form['county']
            member.postcode = request.form['postcode']
            member.date_of_birth = request.form['date_of_birth']
            member.email = request.form['email']
            member.home_phone = request.form['home_phone']
            member.mobile_phone = request.form['mobile_phone']
            member.emergency_name = request.form['emergency_name']
            member.emergency_phone = request.form['emergency_phone']

        except KeyError as e:
                if 'field' in str(e):
                    if 'email' in str(e):
                        flash('This email is already in use', category='danger')
                else:
                    flash('An Error has occurred', category='danger')
                
                return render_template('register.jinja2', title="CLIMB - Register")

        member_password = request.form['password']
        member_password_repeat = request.form['repeatPassword']

        error = False
        if member_password != member_password_repeat:
            flash('Password do not match', category='danger')
            error = True

        if not error:
            member.password_hash = generate_password_hash(member_password)
            member.create()

            session.clear()
            session['user_id'] = member.person_id

            return redirect(url_for('dashboard_bp.dashboard', id=member.person_id))
        
    return render_template('register.jinja2', title="CLIMB - Register")


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    """ Login page """

    if request.method == 'POST':
        if request.form['reg'] == '1':  # Register button
            return redirect(url_for('auth_bp.register'))

        else:
            error = False

            # get user
            user_email = request.form['email']
            user_password = request.form['password']
            try:
                user = person_from_email(user_email)
            except KeyError:
                error=True

            # check password
            if error or not check_password_hash(user.password_hash, user_password):
                error = True

            # add user id to session and redirect to dashboard
            if not error:
                session.clear()
                session['user_id'] = user.person_id
                if user.temp_password:
                    return redirect(url_for('auth_bp.change_password'))
                return redirect(url_for('dashboard_bp.dashboard'))
            else:
                flash('Incorrect login details', category='danger')

    return render_template('login.jinja2', title="CLIMB - Login")


@auth_bp.route('/forgot_password', methods=('GET', 'POST'))
def forgot_password():
    """ sends email with temporary password  """

    if request.method == 'POST':
        user_email = request.form['email']
        user = person_from_email(user_email)

        temp_password = token_urlsafe(12)  # generate a random password
        temp_password_hash = generate_password_hash(temp_password)
        user.password_hash = temp_password_hash
        user.temp_password = True

        content = "Subject: CLIMB Password\n\nPassword: " + temp_password
        email.send_email(user.email, content)

        return redirect(url_for('auth_bp.login'))

    return render_template('forgot_password.jinja2', title="CLIMB - Forgot Password")


@login_required
@auth_bp.route('/change_password', methods=('GET', 'POST'))
def change_password():
    """ sends email with temporary password  """

    if request.method == 'POST':
        user_password = request.form['password']
        user_password_repeat = request.form['repeatPassword']

        error = False
        if user_password != user_password_repeat:
            flash('Password do not match', category='danger')
            error = True

        if not error:
            g.user.password_hash = generate_password_hash(user_password)
            g.user.temp_password = False

            return redirect(url_for('dashboard_bp.dashboard'))

    return render_template('change_password.jinja2', title="CLIMB - Change Password")


@auth_bp.route('/logout')
def logout():
    """ Clears session and redirects to login page """
    
    session.clear()
    return redirect(url_for('auth_bp.login'))
