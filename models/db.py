# -*- coding: utf-8 -*-

if request.is_local:
    db = DAL('sqlite://store.sqlite',pool_size=1,check_reserved=['all'])
else:
    #change to the production database address
    db = DAL('sqlite://store.sqlite',pool_size=1,check_reserved=['all'])
    #db = DAL('mysql://username:password@host/db',check_reserved=['all'])
    #db = DAL('postgres://username:password@host/db',check_reserved=['all'])
    #db = DAL('mssql://username:password@host/db')
    #db = DAL('firebird://username:password')
    #db = DAL('oracle://username/password@db')
    #db = DAL('mongodb://username:password@host/db')

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## custom fields for user
auth.settings.extra_fields['auth_user'] = [
    Field('birth_date', 'datetime', label=T('Birth Date'), requires=IS_DATE()),
    Field('genre', label=T('Genre'), requires = IS_IN_SET([
                                                            ('0', T('Female')),
                                                            ('1', T('Male')), 
                                                            ('2', T('Other'))
                                                            ], zero = T('Select one')
                                                            )),
    Field('cssc', 'integer', label=T('User SSC (social security card)'))
    ]
## create all tables
auth.define_tables(username=False)
#auth.settings.login_userfield = 'email'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True


from gluon.tools import prettydate

# customer address
db.define_table('address',
    Field('user_id', 'reference auth_user', label=T('User')),
    Field('receiver', label=T('Addressee')),
    Field('adr_shipping', 'boolean', default=False, label=T('Shipping Address')),
    Field('zip_code', 'integer', label=T('Zip Code')),
    Field('address', label=T('Address')),
    Field('adr_number', 'integer', label=T('Number')),
    Field('complement', label=T('Complement')),
    Field('neighborhood', label=T('Neighborhood')),
    Field('city', label=T('City')),
    Field('adr_state', label=T('State'))
    )

## validators
db.address.user_id.requires = IS_IN_DB(db, 'auth_user.id', '%(first_name)s %(last_name)s')
db.address.receiver.requires = IS_NOT_EMPTY()
db.address.address.requires = IS_NOT_EMPTY()
db.address.adr_number.requires = IS_NOT_EMPTY()
db.address.neighborhood.requires = IS_NOT_EMPTY()
db.address.city.requires = IS_NOT_EMPTY()
db.address.adr_state.requires = IS_NOT_EMPTY()

# categories
db.define_table('category',
    Field('name', label=T('Name')),
    Field('description', 'text', label=T('Description')),
    Field('parent_category', 'integer'),
    format = '%(name)s'
    )
## validators
db.category.name.requires = IS_NOT_EMPTY()
db.category.parent_category.requires = IS_EMPTY_OR(IS_IN_DB(db, 'category.id','%(name)s'))

# suppliers
db.define_table('supplier',
    Field('name', label=T('Name')),
    Field('business_name', label=T('Business Name')),
    Field('phone', label=T('Phone')),
    Field('email', label=T('Email')),
    Field('address', label=T('Address')),
    Field('federal_id', label=T('Federal Id')),
    Field('state_id', label=T('State Id')),
    Field('info', 'text', label=T('Supplier Info')),
    format = '%(name)s'
    )
## validators
db.category.name.requires = IS_NOT_EMPTY()
db.category.parent_category.requires = IS_EMPTY_OR(IS_IN_DB(db, 'category.id','%(name)s'))

# products
db.define_table('product',
    Field('name', label=T('Name')),
    Field('short_description', length=256, label=T('Short description')),
    Field('description', 'text', label=T('Description')),
    Field('price', 'decimal(7,2)', default=0, label=T('Price')),
    Field('tax', 'decimal(7,2)', default=0, label=T('Tax')),
    Field('product_stok', 'integer', default=0, label=T('Quantity')),
    Field('featured_image', 'upload', label=T('Featured Image')),
    Field('default_category', 'reference category', label=T('Default Category')),
    Field('default_supplier', 'reference category', label=T('Default Supplier')),
    auth.signature,
    format = '%(name)s'
    )
db.product.default_category.requires = IS_IN_DB(db, 'category.id','%(name)s')

## validators
db.product.name.requires = IS_NOT_EMPTY()

# product category
db.define_table('product_category',
    Field('product_id', 'reference product'),
    Field('category_id', 'reference category')
    )
db.product_category.product_id.requires = IS_IN_DB(db, 'product.id', '%(name)s')
db.product_category.category_id.requires = IS_IN_DB(db, 'category.id', '%(name)s')

#product images
db.define_table('product_images',
    Field('image', 'upload'),
    Field('product_id', 'reference product'),
    )
#db.product_image.product_id.requires = IS_IN_DB(db, 'product.id', '%(name)s')

#product stok
db.define_table('product_stok',
    Field('product_id', 'reference product'),
    Field('quantity', 'integer'),
    Field('min_quantity', 'integer'),
    )
db.product_stok.product_id.requires = IS_IN_DB(db, 'product.id', '%(name)s')
db.product_stok.quantity.requires = IS_NOT_EMPTY()
db.product_stok.min_quantity.requires = IS_NOT_EMPTY()

# products specifications
db.define_table('specification',
    Field('product', 'reference product', unique=True, label=T('Product')),
    Field('processor', label=T('Processor')),
    Field('weight', 'double', label=T('Weight (kg)')),
    Field('memory', label=T('Memory')),
    Field('dimensions', label=T('Dimensions (W x D x H)(cm)')),
    Field('esp_storage', label=T('Storage')),
    Field('ethernet', label=T('Ethernet')),
    Field('battery', label=T('Battery')),
    Field('other', 'text', label=T('Other')),
    format = '%(product.name)s'
    )
## validators
db.specification.product.requires = IS_IN_DB(db, 'product.id', '%(name)s')

# reviews
db.define_table('review',
    Field('product', 'reference product'),
    Field('rv_message', 'text'),
    auth.signature
    )

# config
db.define_table('info',
    Field('name', label=T('Name')),
    Field('address', label=T('Address')), 
    Field('city', label=T('City')), 
    Field('state_uf', label=T('State')), 
    Field('zip_code', label=T('Zip Code')), 
    Field('phone', label=T('Phone')), 
    Field('fax', label=T('Fax')), 
    Field('email', label=T('Email')),
    Field('logo', 'upload', default='', label=T('Logo')),
    format = '%(name)s'
    )
## create unique record
if db(db.info).count() == 0:
    store = db.info.insert(name='Store name')
else:
    store = db(db.info).select().first()
## validators
db.info.name.requires = IS_NOT_EMPTY()
db.info.email.requires = IS_EMAIL()
db.info.logo.requires = IS_EMPTY_OR(IS_IMAGE())

## create admin user, groups and role
# if db(db.auth_group).count() == 0:
#     admin = db.auth_group.insert(role='admin')
#     db.auth_group.insert(role='costumer')
#     admin_user = db.auth_user.insert(email='admin@adm.in', password=db.auth_user.password.validate('admin')[0])
#     db.auth_membership.insert(group_id=admin, user_id=admin_user)

