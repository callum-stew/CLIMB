from datetime import datetime

from flask import Blueprint, render_template, request, g, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash

from CLIMB.CLIMB_data import create_person, Settings, WeekDaySettings, Product
from CLIMB import db

first_run_bp = Blueprint('first_run_bp', __name__,
                         template_folder='templates',
                         static_folder='static')


@first_run_bp.before_app_request
def redirect_on_first_run():
    """ Redirect to setup page if first run and requesting webpage """

    settings = Settings()
    is_first_run = settings.get('FIRST_RUN')

    # check endpoint to prevent redirect loop
    if is_first_run == '1' and not any(target in request.endpoint for target in ['first_run_bp', 'static', 'favicon']):
        return redirect(url_for('first_run_bp.first_run'))


@first_run_bp.route('/', methods=('GET', 'POST'))
def first_run():
    """ setup database with initial settings and create admin user """

    day_errors = []

    if request.method == 'POST':
        # Create member
        try:
            # assign personal details
            staff = create_person('ADMIN')
            staff.first_name = request.form['first_name']
            staff.middle_name = request.form['middle_name']
            staff.last_name = request.form['last_name']
            staff.address_line_1 = request.form['address_line_1']
            staff.address_line_2 = request.form['address_line_2']
            staff.address_line_3 = request.form['address_line_3']
            staff.county = request.form['county']
            staff.postcode = request.form['postcode']
            staff.date_of_birth = request.form['date_of_birth']
            staff.email = request.form['email']
            staff.home_phone = request.form['home_phone']
            staff.mobile_phone = request.form['mobile_phone']
            staff.emergency_name = request.form['emergency_name']
            staff.emergency_phone = request.form['emergency_phone']

            # assign permissions
            permissions = ['STORE_CONFIG',
                           'SETTINGS',
                           'BOOKINGS',
                           'MAKE_TRANSACTIONS',
                           'VIEW_TRANSACTIONS',
                           'MEMBER_DATA',
                           'STAFF_DATA']
            for permission in permissions:
                staff.add_permission(permission)

        except KeyError as e:
            if 'field' in str(e):
                if 'email' in str(e):
                    flash('This email is already in use', category='danger')
            else:
                flash('An Error has occurred', category='danger')

            return redirect(request.path, code=302)

        # check passwords match
        staff_password = request.form['password']
        staff_password_repeat = request.form['repeatPassword']

        error = False
        if staff_password != staff_password_repeat:
            flash('Password do not match', category='danger')
            error = True

        # general settings
        settings = Settings()
        settings.set('number_of_people', request.form['numPeople'])
        settings.set('adult_price', round(float(request.form['adultPrice']), 2))
        settings.set('child_price', round(float(request.form['childPrice']), 2))
        settings.set('arrival_range', int(request.form['arrivalRange']))
        settings.set('FIRST_RUN', 0)

        # create adult price product
        adult_product = Product()
        adult_product.name = 'adult'
        adult_product.price = round(float(request.form['adultPrice']), 2)

        # create child price product
        child_product = Product()
        child_product.name = 'child'
        child_product.price = round(float(request.form['childPrice']), 2)

        # change general week settings
        week_days = WeekDaySettings()
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            day_error = False
            submitted_fields = request.form.keys()

            is_open = True if day + '-open' in submitted_fields else False
            open_time = None if day + '-o-time' not in submitted_fields else request.form[day + '-o-time']
            close_time = None if day + '-c-time' not in submitted_fields else request.form[day + '-c-time']

            if is_open and (open_time == '' or close_time == ''):  # open/close time not set
                flash('Please select an opening and closing time for open days', category='danger')
                day_error = True
            elif is_open and datetime.strptime(open_time, '%H:%M') >= datetime.strptime(close_time, '%H:%M'):  # close time earlier than open time
                flash('Please select a closing time later than opening time', category='danger')
                day_error = True
            if day_error:
                day_errors.append(day)
            else:
                week_days.set(day, open=is_open, opening_time=open_time, closing_time=close_time)

        if not error and not day_errors:
            staff.password_hash = generate_password_hash(staff_password)
            staff.create()
            adult_product.create()
            child_product.create()

            session.clear()
            session['user_id'] = staff.person_id

            return redirect(url_for('dashboard_bp.dashboard'))
        else:
            return redirect(request.path, code=302)

    return render_template('first_boot.jinja2',
                           title='CLIMB - First Run',
                           day_errors=day_errors)
