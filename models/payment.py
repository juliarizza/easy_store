# -*- coding: utf-8 -*-

db.define_table('pending_transaction',
	Field('user_id', 'reference auth_user'),
	Field('products'),
	Field('ammount', 'double'),
	Field('confirmed', 'boolean', default=False),
	auth.signature
	)

db.define_table('confirmed_transaction',
	Field('user_id', 'reference auth_user'),
	Field('products'),
	Field('ammount', 'double'),
	Field('pending_id', 'reference pending_transaction', ondelete='SET NULL'),
	Field('payment_system_code'),
	Field('confirmation_time', 'datetime'),
	Field('tokes', 'integer'),
	auth.signature
	)