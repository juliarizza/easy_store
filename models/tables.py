# -*- coding: utf-8 -*-
from gluon.tools import prettydate

# shipment info
db.define_table('address',
    Field('user_id', 'reference auth_user', label=T('User')),
    Field('receiver', label=T('Addressee')),
    Field('adr_type', label=T('Address Type')),
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
db.address.adr_type.requires = IS_IN_SET({1:T('Comercial'), 2:T('Residential')})
db.address.address.requires = IS_NOT_EMPTY()
db.address.adr_number.requires = IS_NOT_EMPTY()
db.address.neighborhood.requires = IS_NOT_EMPTY()
db.address.city.requires = IS_NOT_EMPTY()
db.address.adr_state.requires = IS_NOT_EMPTY()

# categories
db.define_table('category',
	Field('name', label=T('Name')),
	Field('description', 'text', label=T('Description')),
	format = '%(name)s'
	)
## validators
db.category.name.requires = IS_NOT_EMPTY()
## layout
categories = db(db.category).select()

# products
db.define_table('product',
	Field('name', label=T('Name')),
	Field('category', 'reference category', label=T('Category')),
    Field('short_description', length=256, label=T('Short description')),
    Field('description', 'text', label=T('Description')),
    Field('product_image', 'upload', label=T('Image')),
    Field('quantity', 'integer', default=0, label=T('Quantity in stock')),
    Field('price', 'double', default=0, label=T('Price')),
    auth.signature,
    format = '%(name)s'
	)


## validators
db.product.name.requires = IS_NOT_EMPTY()
db.product.category.requires = IS_EMPTY_OR(IS_IN_DB(db, 'category.id', '%(name)s'))
db.product.product_image.requires = IS_EMPTY_OR(IS_IMAGE())

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

## create admin role
if db(db.auth_group).count() == 0:
    admin = db.auth_group.insert(role='admin')
## create admin user and set it's membership
if db(db.auth_user).count() == 0:
    admin_user = db.auth_user.insert(username='admin', password=db.auth_user.password.validate('admin')[0])
    db.auth_membership.insert(group_id=admin, user_id=admin_user)