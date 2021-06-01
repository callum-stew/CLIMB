from flask import render_template, request, make_response, g, flash, redirect

from CLIMB.auth import permission_required
from CLIMB.CLIMB_data import Product, get_all_products, Sale, person_from_id, Booking, get_booking_products

from . import dashboard_bp


@dashboard_bp.route('/store_config', methods=('GET', 'POST', 'DELETE'))
@permission_required('STORE_CONFIG')
def store_config():
    """ Create, update and delete store items """

    selected_product = None
    selected_product_id = request.args.get('sid')

    product = None
    if selected_product_id:
        try:
            product = Product(product_id=selected_product_id)
        except KeyError:
            flash('Product dose not exist', category='danger')
            return redirect(request.path, code=302)

    if request.method == 'POST':
        if selected_product_id:
            # Update product
            # Can't change entry price store item
            if product.name in ['adult', 'child']:
                flash('Please change the price of entry in the settings page.', category='danger')
                return redirect(request.path, code=302)
            
            # Disable old product entry and create new one
            position = product.shop_position
            product.delete()
            product = Product()

            product.shop_position = position
            product.name = request.form['name']
            product.price = round(float(request.form['price']), 2)
            product.create()

            selected_product = product

        else:
            # Create product
            new_product = Product()
            if request.form['name'] in ['adult', 'child']:
                flash('That name is a reserved, please use a diferent name.', category='danger')
                return redirect(request.path, code=302)
            new_product.name = request.form['name']
            new_product.price = round(float(request.form['price']), 2)
            new_product.user_specific = 0
            new_product.create()

    elif request.method == 'DELETE':
        # Delete product
        # Can't change entry price store item
        if product.name in ['adult', 'child']:
            flash('Please change the price of entry in the settings page.', category='danger')
            return redirect(request.path, code=302)

        product.delete()
        return make_response('success', 200)

    else:
        # Get selected product data
        if selected_product_id:
            try:
                selected_product = Product(product_id=selected_product_id)
            except KeyError:
                flash('Product dose not exist', category='danger')
                return redirect(request.path, code=302)

    return render_template('staff_dashboard_store_config.jinja2', title='Store - Config',
                           products=get_all_products(order_by_position=True),
                           selected_product=selected_product, user=g.user)


@dashboard_bp.route('/update_store_order', methods=['PUT'])
@permission_required('STORE_CONFIG')
def update_store_order():
    """ Changes the product positions in database """

    order = request.get_json()
    for i in range(len(order)):
        item = Product(product_id=int(order[i]))
        item.shop_position = i
    return make_response('success', 200)


@dashboard_bp.route('/complete_order', methods=['POST'])
@permission_required('MAKE_TRANSACTIONS')
def complete_order():
    """ Creates new sale in database """

    new_sale = Sale()

    products = []
    for product in request.get_json()['products']:
        products.append((Product(product[0]), product[1]))
    if request.get_json()['bookings']:
        booking = Booking(request.get_json()['bookings'][0])
        booking_products = get_booking_products()
        if booking.adults:
            products.append((booking_products[0], booking.adults))
        if booking.children:
            products.append((booking_products[1], booking.children))

    member = person_from_id(request.get_json()['member_id'])

    new_sale.staff = g.user
    new_sale.member = member
    for product in products:
        new_sale.add_product(product[0], product[1])

    new_sale.create()
    if request.get_json()['bookings']:
        booking.completed = 1
    return make_response('success', 200)
