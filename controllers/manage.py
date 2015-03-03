# -*- coding: utf-8 -*-
import os
from gluon.fileutils import listdir

@auth.requires_membership('admin')
def index():
	btn = A('Setup', _href=URL('manage', 'setup'), _class='btn btn-large btn-block')
	btn2 = A('Categories', _href=URL('manage', 'select', args='category'), _class='btn btn-large btn-block btn-primary')
	btn3 = A('Products', _href=URL('manage', 'select', args='product'), _class='btn btn-large btn-block')
	btn4 = A('Clear cache', _href=URL('manage', 'clear'), _class='btn btn-large btn-block btn-primary')
	return dict(btn=btn, btn2=btn2, btn3=btn3, btn4=btn4)

@auth.requires_membership('admin')
def setup():
	form = SQLFORM(db.info, store, showid=False)
	if form.process().accepted:
		redirect(URL(c='manage', f='index'))
	return dict(form=form)

@auth.requires_membership('admin')
def select():
	table = request.args(0)
	items = db(db[table]).select()
	return dict(table=table, items=items)

@auth.requires_membership('admin')
def insert():
	table = request.args(0)
	form = SQLFORM(db[table])
	if form.process().accepted:
		redirect(URL(c='manage', f='select', args=table))
	return dict(table=table,form=form)

@auth.requires_membership('admin')
def edit():
	table = request.args(0)
	item = int(request.args(1))
	form = SQLFORM(db[table], item, showid=False)
	if form.process().accepted:
		redirect(URL(c='manage', f='select', args=table))
	return dict(table=table,form=form)

@auth.requires_membership('admin')
def remove():
	table = request.args(0)
	item = int(request.args(1))
	db(db[table].id == item).delete()
	db.commit()
	redirect(URL(c='manage', f='select', args=table))

@auth.requires_membership('admin')
def clear():
	app = request.application
	files = listdir('applications/%s/cache/' % app,'',0)
	for file in files: os.unlink(file)
	files=listdir('applications/%s/errors/' % app,'',0)
	for file in files: os.unlink(file)
	session.flash="cache cleaned"
	redirect(URL(c='manage', f='index'))
