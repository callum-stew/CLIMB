from datetime import date

from CLIMB import db

from .data import ProductData, SaleData, SaleHasProductData
from .person_factory import person_from_id


class Product:
    def __init__(self, product_id=None):
        self._product_data = ProductData(product_id)
        self._product_id = self._product_data['product_id']

    def create(self):
        if self._product_data.created:
            return False

        if self.shop_position is None:
            cur = db.connection.cursor()
            cur.execute('SELECT COUNT(*) FROM product')
            pos = cur.fetchone()
            self.shop_position = int(pos['COUNT(*)'])

        valid, issue = self._product_data.data_valid()
        if not valid and issue != ['product_id']:
            raise ValueError(issue)
        self._product_data.create()
        self._product_id = self._product_data['product_id']

    def delete(self, safe=True):
        if not safe:
            if self._product_data.created:
                self._product_data.delete()

        else:
            self._product_data['deleted'] = 1

    @property
    def product_id(self):
        return self._product_id

    @property
    def deleted(self):
        return self._product_data['deleted']

    @property
    def name(self):
        return self._product_data['name']

    @name.setter
    def name(self, value):
        self._product_data['name'] = value

    @property
    def price(self):
        return self._product_data['price']

    @price.setter
    def price(self, value):
        self._product_data['price'] = value

    @property
    def shop_position(self):
        return self._product_data['shop_position']

    @shop_position.setter
    def shop_position(self, value):
        self._product_data['shop_position'] = value


def get_all_products(order_by_position=False, show_deleted=False):
    products = []
    cur = db.connection.cursor()
    query = 'SELECT product_id FROM product'
    if not show_deleted:
        query += ' WHERE deleted = 0'
    if order_by_position:
        query += ' ORDER BY shop_position'
    cur.execute(query)
    data = cur.fetchall()
    for row in data:
        products.append(Product(product_id=row['product_id']))
    return products


def get_booking_products():
    products = []
    cur = db.connection.cursor()
    query = "SELECT product_id FROM product WHERE deleted = 0 AND name = 'adult'"
    cur.execute(query)
    data = cur.fetchone()
    products.append(Product(data['product_id']))
    query = "SELECT product_id FROM product WHERE deleted = 0 AND name = 'child'"
    cur.execute(query)
    data = cur.fetchone()
    products.append(Product(data['product_id']))
    return products


class Sale:
    def __init__(self, sale_id=None):
        self._sale_data = SaleData(sale_id=sale_id)
        self._sale_id = self._sale_data['sale_id']
        self._sale_has_product_data = SaleHasProductData()
        self._products = []
        if self._sale_data.created:
            for product in self._sale_has_product_data.get_items(sale_id=self.sale_id):
                self._products.append([Product(product[1]['product_id']), product[2]['number_of_products']])

    def add_product(self, product, quantity):
        update = None
        for index in range(len(self._products)):
            if product in self._products[index]:
                update = index
                break
        if update is None:
            self._products.append([product, quantity])
            if self._sale_data.created:
                self._sale_has_product_data.add_item(self.sale_id, product.product_id,
                                                     {'number_of_products', quantity})
        else:
            self._products[update][1] = quantity
            if self._sale_data.created:
                self._sale_has_product_data.update_item(self.sale_id, product.product_id,
                                                        {'number_of_products', quantity})

    def create(self):
        if self._sale_data.created:
            return False

        self._sale_data['date'] = date.today()

        valid, issue = self._sale_data.data_valid()
        if not valid and issue != ['sale_id']:
            raise ValueError(issue)
        self._sale_data.create()
        self._sale_id = self._sale_data['sale_id']

        for product in self._products:
            self._sale_has_product_data.add_item(self.sale_id, product[0].product_id,
                                                 {'number_of_products': product[1]})

    def delete(self, product):
        exists = None
        for index in range(len(self._products)):
            if product in self._products[index]:
                exists = index
        if exists is not None:
            self._sale_has_product_data.delete_items(self.sale_id, product.product_id)
            del self._products[exists]

    @property
    def sale_id(self):
        return self._sale_id

    @property
    def products(self):
        return self._products

    @property
    def total(self):
        total = 0
        for product in self._products:
            total += (float(product[0].price) * product[1])
        return round(total, 2)

    @property
    def date(self):
        return self._sale_data['date']

    @property
    def staff(self):
        return person_from_id(self._sale_data['staff_person_id'])

    @staff.setter
    def staff(self, person):
        self._sale_data['staff_person_id'] = person.person_id

    @property
    def member(self):
        return person_from_id(self._sale_data['member_person_id'])

    @member.setter
    def member(self, person):
        self._sale_data['member_person_id'] = person.person_id


def get_sales(person):
    sales = []
    cur = db.connection.cursor()
    query = 'SELECT sale_id FROM sale WHERE member_person_id = ?'
    cur.execute(query, (person.person_id,))
    data = cur.fetchall()
    for row in data:
        sales.append(Sale(row['sale_id']))
    return sales[::-1]
