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
auth.define_tables(username=True, signature=False)

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True