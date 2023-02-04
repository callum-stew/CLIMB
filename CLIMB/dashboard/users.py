from datetime import date
from base64 import b64decode
import os
from secrets import token_urlsafe

from flask import render_template, request, make_response, redirect, url_for, current_app, g, jsonify, flash
from werkzeug.security import generate_password_hash

from CLIMB.auth import login_required, permission_required
from CLIMB.CLIMB_data import person_from_id, create_person
from CLIMB import email, db

from . import dashboard_bp


@dashboard_bp.route('/user_search', methods=('POST',))
@login_required
def user_search():
    """ Searchers database for users using data from POST and returns JSON response """

    search_value = request.get_json()['user_search']
    response = {'member_count': 0,
                'members': [],
                'staff_count': 0,
                'staff': []}
    cur = db.connection.cursor()

    if g.user.has_permission('MEMBER_DATA'):
        # get members
        cur.execute('SELECT * FROM person WHERE user_type = \'MEMBER\' AND (first_name LIKE ? OR email LIKE ?) AND deleted = 0',
                    (search_value+'%', search_value+'%'))
        result = cur.fetchall()

        response['member_count'] = len(result)
        response['members'] = []
        if response['member_count'] <= 5:
            for member in result:
                full_name = member['first_name']+' '
                if member['middle_name']:
                    full_name += (member['middle_name']+' ')
                full_name += member['last_name']

                member_details = {
                    'id': member['person_id'],
                    'full_name':  full_name,
                    'email': member['email']
                }
                response['members'].append(member_details)

    if g.user.has_permission('STAFF_DATA'):
        # get staff
        cur.execute('SELECT * FROM person WHERE (user_type = \'STAFF\' OR user_type = \'ADMIN\') AND (first_name LIKE ? OR email LIKE ?)',
                    (search_value + '%', search_value + '%'))
        result = cur.fetchall()

        response['staff_count'] = len(result)
        response['staff'] = []
        if response['staff_count'] <= 5:
            for staff in result:
                full_name = staff['first_name'] + ' '
                if staff['middle_name']:
                    full_name += (staff['middle_name'] + ' ')
                full_name += staff['last_name']

                staff_details = {
                    'id': staff['person_id'],
                    'full_name': full_name,
                    'email': staff['email']
                }
                response['staff'].append(staff_details)

    return make_response(jsonify(response), 200)


@dashboard_bp.route('/member', methods=('GET', 'POST', 'DELETE'))
@permission_required('MEMBER_DATA')
def members_create():
    """ Create, edit and delete members """

    person_id = request.args.get('pid')  # Uses url parameters to send person_id

    if request.method == 'POST':
        if person_id:
            # Update a person
            try:
                member = person_from_id(person_id)
            except KeyError:
                flash('This person dose not exist', category="danger")
                return redirect(url_for('dashboard_bp.dashboard'))

            try:
                set_details(member, request.form)
            except KeyError as e:
                if 'field' in str(e):
                    if 'email' in str(e):
                        flash('This email is already in use', category='danger')
                else:
                    flash('An Error has occurred', category='danger')
                    member = None

                return render_template('staff_dashboard_member_edit.jinja2', member=member, user=g.user)
        else:
            # Create a person
            member = create_person('MEMBER')
            set_details(member, request.form)

            # generate a random password
            temp_password = token_urlsafe(12)
            temp_password_hash = generate_password_hash(temp_password)
            member.password_hash = temp_password_hash
            member.temp_password = True

            try:
                member.create()
            except KeyError as e:
                if 'field' in str(e):
                    if 'email' in str(e):
                        flash('This email is already in use', category='danger')
                else:
                    print(e)
                    flash('An Error has occurred', category='danger')
                    member = None
                    
                return render_template('staff_dashboard_member_edit.jinja2', member=member, user=g.user)

            # Send email with password to new member
            content = "Subject: CLIMB Password\n\nPassword: "+temp_password
            email.send_email(member.email, content)

        # decode and save image
        img_data = request.form['image']
        if img_data != '0':
            path = os.path.join(current_app.root_path, 'static', 'user_images',
                                "user_img_" + str(member.person_id) + ".jpg")
            with open(path, 'wb') as f:
                f.write(b64decode(img_data[23:]))

        return redirect(url_for('dashboard_bp.dashboard', id=member.person_id))

    elif request.method == 'DELETE':
        # Delete member
        member = person_from_id(request.get_json()['id'])
        member.delete()

        # Delete image
        path = os.path.join(current_app.root_path, 'static', 'user_images',
                            "user_img_" + str(request.get_json()['id']) + ".jpg")
        if os.path.isfile(path):
            os.remove(path)

        return make_response('success', 200)

    if person_id:
        return render_template('staff_dashboard_member_edit.jinja2', member=person_from_id(person_id), user=g.user)
    else:
        return render_template('staff_dashboard_member_edit.jinja2', member=None, user=g.user)


def set_details(user, form):
    user.first_name = form['first_name']
    user.middle_name = form['middle_name']
    user.last_name = form['last_name']
    user.address_line_1 = form['address_line_1']
    user.address_line_2 = form['address_line_2']
    user.address_line_3 = form['address_line_3']
    user.county = form['county']
    user.postcode = form['postcode']
    user.date_of_birth = form['date_of_birth']
    user.email = form['email']
    user.home_phone = form['home_phone']
    user.mobile_phone = form['mobile_phone']
    user.emergency_name = form['emergency_name']
    user.emergency_phone = form['emergency_phone']


@dashboard_bp.route('/staff_edit', methods=('GET', 'POST', 'DELETE'))
@permission_required('STAFF_DATA')
def staff():
    """ Create, edit and delete staff """

    person_id = request.args.get('pid')  # Uses url parameters to send person_id

    if request.method == 'POST':
        if person_id:
            # Update a staff member
            try:
                staff = person_from_id(person_id)
            except KeyError:
                flash('This person dose not exist', category="danger")
                return redirect(url_for('dashboard_bp.dashboard'))

            try:
                set_details(staff, request.form)

                # Set or remove permissions
                permissions = {'STORE_CONFIG',
                               'SETTINGS',
                               'BOOKINGS',
                               'FORMS',
                               'MAKE_TRANSACTIONS',
                               'VIEW_TRANSACTIONS',
                               'MEMBER_DATA',
                               'STAFF_DATA'}
                checked_permissions = permissions.intersection(set(request.form.keys()))

                for permission in checked_permissions:
                    if not staff.has_permission(permission):
                        staff.add_permission(permission)
                unchecked_permissions = permissions - checked_permissions

                if staff.user_type == 'ADMIN' and unchecked_permissions:
                    flash('Admin account can not have permissions removed', category='danger')
                else:
                    for permission in unchecked_permissions:
                        if staff.has_permission(permission):
                            staff.remove_permission(permission)

            except KeyError as e:
                if 'field' in str(e):
                    if 'email' in str(e):
                        flash('This email is already in use', category='danger')
                else:
                    flash('An Error has occurred', category='danger')
                    staff = None

                return render_template('staff_dashboard_staff_edit.jinja2', staff=staff, user=g.user)
        else:
            # Create a person
            staff = create_person('STAFF')
            set_details(staff, request.form)

            # Set or remove permissions
            permissions = {'STORE_CONFIG',
                           'SETTINGS',
                           'BOOKINGS',
                           'FORMS',
                           'MAKE_TRANSACTIONS',
                           'VIEW_TRANSACTIONS',
                           'MEMBER_DATA',
                           'STAFF_DATA'}
            checked_permissions = permissions.intersection(set(request.form.keys()))

            for permission in checked_permissions:
                if not staff.has_permission(permission):
                    staff.add_permission(permission)

            # generate a random password
            temp_password = token_urlsafe(12)
            temp_password_hash = generate_password_hash(temp_password)
            staff.password_hash = temp_password_hash
            staff.temp_password = True

            try:
                staff.create()
            except KeyError as e:
                if 'field' in str(e):
                    if 'email' in str(e):
                        flash('This email is already in use', category='danger')
                else:
                    print(str(e))
                    flash('An Error has occurred', category='danger')
                    staff = None
                    
                return render_template('staff_dashboard_staff_edit.jinja2', staff=staff, user=g.user)

            # Send email with password to new staff
            content = "Subject: CLIMB Password\n\nPassword: "+temp_password
            email.send_email(staff.email, content)

        flash('Staff updated', category='success')

        return redirect(url_for('dashboard_bp.person_list', type='staff'))

    elif request.method == 'DELETE':
        # Delete staff
        member = person_from_id(request.get_json()['id'])
        if member.user_type == 'ADMIN':
            return make_response('can not delete admin', 418)
        member.delete()

        return make_response('success', 200)

    if person_id:
        return render_template('staff_dashboard_staff_edit.jinja2', staff=person_from_id(person_id), user=g.user)
    else:
        return render_template('staff_dashboard_staff_edit.jinja2', staff=None, user=g.user)


@dashboard_bp.route('/personal_info', methods=('GET', 'POST', 'DELETE'))
@login_required
def personal_info():
    """ Member can change or delete there own personal info """

    if request.method == 'POST':
        # Update member details
        member = g.user
        set_details(member, request.form)
        flash('Details Updated', category='info')

    elif request.method == 'DELETE':
        # Delete member
        member = g.user
        member.delete()

        # Delete image
        path = os.path.join(current_app.root_path, 'static', 'user_images',
                            "user_img_" + str(request.get_json()['id']) + ".jpg")
        if os.path.isfile(path):
            os.remove(path)
        return make_response('success', 200)

    return render_template('member_dashboard_personal_info.jinja2', title='CLIMB - Personal Info', member=g.user)


@dashboard_bp.route('/people')
@login_required
def person_list():
    person_type = request.args.get('type')
    search_value = request.args.get('search')
    people = []
    cur = db.connection.cursor()

    if person_type == 'member':
        # get members
        if g.user.has_permission('MEMBER_DATA'):
            if search_value:
                cur.execute('SELECT person_id FROM person WHERE user_type = \'MEMBER\' AND (first_name LIKE ? OR email LIKE ?) AND deleted = 0',
                            (search_value+'%', search_value+'%'))
                result = cur.fetchall()

                for member in result:
                    people.append(person_from_id(member['person_id']))

            else:
                cur.execute('SELECT person_id FROM person WHERE user_type = \'MEMBER\' AND deleted = 0')
                result = cur.fetchall()

                for member in result:
                    people.append(person_from_id(member['person_id']))

        else:
            flash('You do not have permission to view that', category='danger')
            return redirect(url_for('dashboard_bp.dashboard'))

    elif person_type == 'staff':
        # get staff
        if g.user.has_permission('STAFF_DATA'):
            if search_value:
                cur.execute('SELECT person_id FROM person WHERE (user_type = \'STAFF\' OR user_type = \'ADMIN\') AND (first_name LIKE ? OR email LIKE ?) AND deleted = 0',
                            (search_value + '%', search_value + '%'))
                result = cur.fetchall()

                for staff in result:
                    people.append(person_from_id(staff['person_id']))

            else:
                cur.execute('SELECT person_id FROM person WHERE (user_type = \'STAFF\' OR user_type = \'ADMIN\') AND deleted = 0')
                result = cur.fetchall()

                for staff in result:
                    people.append(person_from_id(staff['person_id']))

        else:
            flash('You do not have permission to view that', category='danger')
            return redirect(url_for('dashboard_bp.dashboard'))

    return render_template('staff_dashboard_person_view.jinja2', person_type=person_type, people=people, user=g.user)
