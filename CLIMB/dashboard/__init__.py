from datetime import datetime, timedelta
import json

from flask import Blueprint, render_template, request, g, redirect, url_for, flash, abort, make_response, jsonify

from CLIMB.auth import login_required, permission_required
from CLIMB.CLIMB_data import person_from_id, get_all_products, get_booking_products, get_sales, Settings, WeekDaySettings, CustomDaySettings, Booking, get_bookings_between_timestamp, get_bookings_from_person, Product

dashboard_bp = Blueprint('dashboard_bp', __name__,
                         template_folder='templates',
                         static_folder='static')

from . import users, store


@dashboard_bp.route('/')
@login_required
def dashboard():
    """ Dashboard for staff and members """
    settings = Settings()

    if g.user.user_type in ['STAFF', 'ADMIN']:
        # render staff dashboard with member data if id in request args
        selected_member = None
        user_bookings = []
        available_booking = None
        selected_person_id = request.args.get('pid')
        if selected_person_id:
            try:
                selected_person = person_from_id(selected_person_id)
                if selected_person.user_type == 'MEMBER':
                    selected_member = selected_person
            except KeyError:
                flash('That person dose not exist.', category="danger")
                return redirect(request.path, code=302)

            user_bookings = get_bookings_from_person(selected_person_id)
            if len(user_bookings) > 0:
                available_booking = user_bookings[0]
                del user_bookings[0]
                arrival_range = timedelta(minutes=int(settings.get('arrival_range')))
                if (datetime.now() + arrival_range).timestamp() > available_booking.start > (datetime.now() - arrival_range).timestamp():
                    available_booking.open = True
                else:
                    available_booking.open = True

        return render_template('staff_dashboard.jinja2',
                               title='CLIMB - Dashboard',
                               user=g.user,
                               selected_member=selected_member,
                               products=get_all_products(order_by_position=True),
                               adult_price=settings.get('adult_price'),
                               bookings=user_bookings,
                               child_price=settings.get('child_price'),
                               available_booking=available_booking)

    elif g.user.user_type == 'MEMBER':
        # redirect to member bookings
        return redirect(url_for('dashboard_bp.bookings'))


@dashboard_bp.route('/settings', methods=('GET', 'POST'))
@permission_required('SETTINGS')
def settings():
    """ Staff settings page """

    settings = Settings()
    week_days = WeekDaySettings()
    custom_days = CustomDaySettings()
    errors = []

    if request.method == 'POST':
        if request.form['type'] == 'settings':
            # change general settings
            settings.set('number_of_people', request.form['numPeople'])
            settings.set('adult_price', round(float(request.form['adultPrice']), 2))
            settings.set('child_price', round(float(request.form['childPrice']), 2))
            settings.set('arrival_range', int(request.form['arrivalRange']))

            booking_products = get_booking_products()

            # update adult price product
            if booking_products[0].price != str(round(float(request.form['adultPrice']), 2)):
                position = booking_products[0].shop_position
                booking_products[0].delete()
                product = Product()

                product.shop_position = position
                product.name = 'adult'
                product.price = round(float(request.form['adultPrice']), 2)
                product.create()

            # update child price product
            if booking_products[1].price != str(round(float(request.form['childPrice']), 2)):
                position = booking_products[1].shop_position
                booking_products[1].delete()
                product = Product()

                product.shop_position = position
                product.name = 'child'
                product.price = round(float(request.form['childPrice']), 2)
                product.create()

            flash('Settings updated.', category='info')

        elif request.form['type'] == 's-days':
            # change general week settings
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                error = False
                submitted_fields = request.form.keys()

                is_open = True if day+'-open' in submitted_fields else False
                open_time = None if day+'-o-time' not in submitted_fields else request.form[day+'-o-time']
                close_time = None if day+'-c-time' not in submitted_fields else request.form[day+'-c-time']

                if is_open and (open_time == '' or close_time == ''):
                    flash('Please select an opening and closing time for open days', category='danger')
                    error = True
                elif is_open and open_time != '' and close_time != '' and datetime.strptime(open_time, '%H:%M') >= datetime.strptime(close_time, '%H:%M'):
                    flash('Please select a closing time later than opening time', category='danger')
                    error = True
                if error:
                    errors.append(day)
                else:
                    week_days.set(day, open=is_open, opening_time=open_time, closing_time=close_time)

            if not error:
                flash('Settings updated.', category='info')

        elif request.form['type'] == 'c-day':
            # change or create custom day settings
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            submitted_fields = request.form.keys()

            date = request.form['date']
            is_open = True if 'open' in submitted_fields else False
            open_time = None if 'o-time' not in submitted_fields else request.form['o-time']
            close_time = None if 'c-time' not in submitted_fields else request.form['c-time']

            if is_open and (open_time == '' or close_time == ''):
                flash('Please select an opening and closing time for open days', category='danger')
            elif is_open and open_time != '' and close_time != '' and datetime.strptime(open_time, '%H:%M') >= datetime.strptime(close_time, '%H:%M'):
                flash('Please select a closing time later than opening time', category='danger')
            else:
                week_data = week_days.get(days[datetime.strptime(date, '%Y-%m-%d').weekday()])

            # dose an entry exist for this date
            try:
                custom_days.get(date)
                exist = True
            except KeyError:
                exist = False

            # do not create entry if no entry exists and is same as general week day
            if week_data != {'open': 1 if is_open else 0, 'opening_time': open_time, 'closing_time': close_time} and not exist:
                custom_days.set(date, open=is_open, opening_time=open_time, closing_time=close_time)

            flash('Custom day created.', category='info')

    return render_template('staff_dashboard_settings.jinja2',
                           title='CLIMB - Settings',
                           user=g.user,
                           settings=settings,
                           week_days=week_days,
                           custom_days=custom_days,
                           errors=errors)


@dashboard_bp.route('/custom_day_data', methods=('POST',))
@permission_required('SETTINGS')
def custom_day_data():
    """ Retrieve data about date """

    custom_days = CustomDaySettings()
    week_days = WeekDaySettings()

    date = request.get_json()['date']
    day = request.get_json()['day']

    # if no custom entry exists return general week day data
    try:
        data = custom_days.get(date)
    except KeyError:
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        data = week_days.get(days[int(day)-1])

    return make_response(jsonify(data), 200)


def get_calendar_data():
    settings = Settings()
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    data = {'day': {}, 'date': {}}
    week_days = WeekDaySettings()
    custom_days = CustomDaySettings()
    for day in days:
        data['day'][day] = week_days.get(day)
    for date in custom_days.dates:
        if datetime.strptime(date, '%Y-%m-%d') >= datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d'):
            data['date'][date] = custom_days.get(date)

    return json.dumps(data)


def set_booking_details(booking):
    booking.person_id = g.user.person_id
    booking.adults = request.form['numAdult']
    booking.children = request.form['numChild']
    start = int(request.form['time']) / 1000
    length = int(request.form['length'])
    booking.start = start
    booking.end = start + (length * 60)


@dashboard_bp.route('/bookings', methods=('GET', 'POST', 'DELETE'))
@login_required
def bookings():
    settings = Settings()

    data = get_calendar_data()

    booking_id = request.args.get('bid')
    date = request.args.get('date')

    if g.user.user_type in ['STAFF', 'ADMIN']:
        # staff page to view current bookings

        if not g.user.has_permission('BOOKINGS'):
            abort(403)

        if not date:
            date = datetime.now()
        else:
            date = datetime.fromtimestamp(int(date) / 1000)
        date = datetime(year=date.year, month=date.month, day=date.day, hour=0, second=0)
        day_end = date + timedelta(days=1)
        bookings = get_bookings_between_timestamp(date.timestamp(), day_end.timestamp())
        people = {}
        for booking in bookings:
            if booking.person_id not in people.keys():
                people[booking.person_id] = person_from_id(booking.person_id)

        return render_template('staff_dashboard_bookings.jinja2',
                               title='CLIMB - Bookings',
                               user=g.user, calendar_data=data,
                               adult_price=settings.get('adult_price'),
                               bookings=bookings,
                               child_price=settings.get('child_price'),
                               max_people=settings.get('number_of_people'),
                               selected_date=date.timestamp(),
                               booking_people=people,
                               current_date=datetime.now().timestamp())
    
    elif g.user.user_type == 'MEMBER':
        # member page to view, edit, delete and create members bookings

        if request.method == 'POST':
            if booking_id:
                old_booking = Booking(booking_id=booking_id)
                old_person_id = old_booking.person_id
                set_booking_details(old_booking)
                old_booking.person_id = old_person_id
                flash('booking updated', category='info')
            else:
                new_booking = Booking()
                set_booking_details(new_booking)
                new_booking.create()
                flash('booking created', category='info')

            return redirect(url_for('dashboard_bp.dashboard'))

        elif request.method == 'DELETE':
            delete_booking = Booking(booking_id=request.get_json()['id'])
            delete_booking.delete()

        selected_booking = None
        if booking_id:
            selected_booking = Booking(booking_id=booking_id)

        user_bookings = get_bookings_from_person(g.user.person_id)

        return render_template('member_dashboard_bookings.jinja2',
                               title='CLIMB - Bookings',
                               user=g.user,
                               calendar_data=data,
                               adult_price=settings.get('adult_price'),
                               bookings=user_bookings,
                               child_price=settings.get('child_price'),
                               max_people=settings.get('number_of_people'),
                               selected_booking=selected_booking)


@dashboard_bp.route('/edit_bookings', methods=('GET', 'POST', 'DELETE'))
@permission_required('BOOKINGS')
def edit_bookings():
    """ staff page to create and edit bookings """

    settings = Settings()

    data = get_calendar_data()

    booking_id = request.args.get('bid')
    person_id = request.args.get('pid')

    if request.method == 'POST':
        if booking_id:
            old_booking = Booking(booking_id=booking_id)
            if old_booking.start < datetime.now().timestamp():
                flash('old bookings cannot be changed', category='info')
                return redirect(url_for('dashboard_bp.bookings'))
            set_booking_details(old_booking)
            flash('booking updated', category='info')
        else:
            new_booking = Booking()
            set_booking_details(new_booking)
            new_booking.create()
            flash('booking created', category='info')

        return redirect(url_for('dashboard_bp.bookings'))

    elif request.method == 'DELETE':
        delete_booking = Booking(booking_id=request.get_json()['id'])
        delete_booking.delete()

    selected_booking = None
    if booking_id:
        selected_booking = Booking(booking_id=booking_id)
        person = person_from_id(selected_booking.person_id)
    else:
        person = person_from_id(person_id) if person_id else g.user

    return render_template('staff_dashboard_edit_booking.jinja2',
                           title='CLIMB - Bookings',
                           user=g.user,
                           calendar_data=data,
                           adult_price=settings.get('adult_price'),
                           child_price=settings.get('child_price'),
                           max_people=settings.get('number_of_people'),
                           selected_booking=selected_booking,
                           booking_person=person,
                           current_date=datetime.now().timestamp())


@dashboard_bp.route('/check_booking', methods=['POST'])
def check_booking():
    """ finds the max number of people from overlapping bookings
     to ensure number of people is not greater than the max allowed """

    settings = Settings()
    data = request.get_json()
    response = {}
    
    for block in data.keys():
        start = data[block]['start']
        end = data[block]['end']
        num_new_people = data[block]['peopleNum']
        selected_booking_id = data[block]['booking_id']
        current_bookings = get_bookings_between_timestamp(start/1000, end/1000)

        max_booked_people = 0
        booked_people = 0
        start_times = []
        end_times = []
        overlap = False

        for booking in current_bookings:
            # dose not include the selected booking
            if booking.booking_id == selected_booking_id:
                continue
            # dose not allow overlapping booking made by same person
            elif (selected_booking_id is not None and booking.person_id == Booking(selected_booking_id).person_id) or (selected_booking_id is None and booking.person_id == g.user.person_id):
                overlap = True

            # add start time and end time to the arrays in a sorted order
            start_times.append((int(booking.start), booking.adults+booking.children))
            if end_times:
                inserted = False
                for i in range(len(end_times)):
                    if int(booking.end) < end_times[i][0]:
                        end_times.insert(i, (int(booking.end), booking.adults+booking.children))
                        inserted = True
                        break
                if not inserted:
                    end_times.append((int(booking.end), booking.adults+booking.children))
            else:
                end_times.append((int(booking.end), booking.adults+booking.children))

        # loop through items in start and end times lists
        for i in range(len(start_times)+len(end_times)):
            # brake when the are no more bookings to check
            if len(start_times) == 0:
                break
            # on booking start add number of people to booked_people
            if start_times[0][0] <= end_times[0][0]:
                booked_people += start_times[0][1]
                del start_times[0]
            # on booking end remove number of people from booked_people
            elif start_times[0][0] >= end_times[0][0]:
                booked_people -= end_times[0][1]
                del end_times[0]
            # track maximum value of booked_people
            if booked_people > max_booked_people:
                max_booked_people = booked_people

        # block not valid on True caused by overlap or max_people create that people capacity
        response[block] = True if overlap else int(settings.get('number_of_people')) < max_booked_people+int(num_new_people)

    return make_response(jsonify(response), 200)


@dashboard_bp.route('/transactions')
@login_required
def transactions():
    """ page to view stats on transactions """

    if g.user.user_type in ['STAFF', 'ADMIN']:
        if not g.user.has_permission('VIEW_TRANSACTIONS'):
            abort(403)
        # TODO: Staff transaction data
        return redirect(url_for('dashboard_bp.dashboard'))

    else:
        return render_template('member_dashboard_transactions.jinja2',
                               title='CLIMB - Transactions',
                               user=g.user,
                               transactions=get_sales(g.user))
