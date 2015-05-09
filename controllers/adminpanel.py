# -*- coding: utf-8 -*-

# coding: utf8
@auth.requires_membership('admin')
def index(): 
    return locals()

@auth.requires_membership('admin')
def products():
    products_grid  = SQLFORM.grid(db.product, csv=False) 
    return locals()

@auth.requires_membership('admin')
def product_categories():
    categories_grid = SQLFORM.grid(db.category, csv=False)
    return locals()

@auth.requires_membership('admin')
def orders(): 
    return locals()

@auth.requires_membership('admin')
def store_users(): 
    users_grid = SQLFORM.grid(db.auth_user, csv=False)
    return locals()

@auth.requires_membership('admin')
def user_groups(): 
    groups_grid = SQLFORM.grid(db.auth_membership, csv=False)
    return locals()

@auth.requires_membership('admin')
def suppliers():
    suppliers_grid  = SQLFORM.grid(db.supplier, csv=False)
    return locals()

@auth.requires_membership('admin')
def carriers():
    carriers_grid  = SQLFORM.grid(db.carrier, csv=False) 
    return locals()

@auth.requires_membership('admin')
def carriers_tax():
    carriers_tax_grid  = SQLFORM.grid(db.carrier_tax, csv=False) 
    return locals()

@auth.requires_membership('admin')
def invoices(): 
    return locals()

@auth.requires_membership('admin')
def merchandise_returns(): 
    return locals()

@auth.requires_membership('admin')
def statuses(): 
    return locals()

@auth.requires_membership('admin')
def order_messages(): 
    return locals()

@auth.requires_membership('admin')
def costumers():
    costumer_grid = db(db.auth_user) 
    return locals()

@auth.requires_membership('admin')
def costumer_groups(): 
    return locals()

@auth.requires_membership('admin')
def shopping_carts(): 
    return locals()



@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)