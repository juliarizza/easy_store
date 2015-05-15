# -*- coding: utf-8 -*-

if not session.cart:
    # instantiate new cart
    session.cart, session.balance = [], 0

def index():
    now = datetime.datetime.now()
    span = datetime.timedelta(days=10)
    product_list = db(db.product.created_on >= (now-span)).select(limitby=(0,3), orderby=~db.product.created_on)
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def register():
    form = auth.register()
    return locals()


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)