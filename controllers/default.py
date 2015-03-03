# -*- coding: utf-8 -*-

if not session.cart:
    # instantiate new cart
    session.cart, session.balance = [], 0

def index():
    now = datetime.datetime.now()
    span = datetime.timedelta(days=10)
    featured = db(db.product.created_on >= (now-span)).select(limitby=(0,3), orderby=~db.product.created_on)
    return dict(featured=featured)

def show_products():
    if request.vars.category:
        products = db(db.product.category == request.vars.category).select(limitby=(0,20),
                                                                            orderby=db.product.name)
    else:
        products = db(db.product).select(limitby=(0,20), orderby=~db.product.name)
    return dict(products=products)

def product():
    if not request.args: redirect(URL(c='default',f='index'))
    try:
        int(request.args(0))
    except ValueError:
        raise HTTP(404, 'Product not found. Invalid ID.')

    product = db(db.product.id == int(request.args(0))).select().first()
    specification = db(db.specification.product == product.id).select().first()
    reviews = db(db.review.product == product.id).select()

    form = SQLFORM.factory(
        Field('quantity', 'integer', default=1),
        _class="form-inline"
        )
    if form.accepts(request.vars, session):
        quantity = int(form.vars.quantity)
        if quantity > product.quantity or quantity <= 0:
            response.flash = T('Unavailable quantity.')
        else:
            for prod in session.cart:
                if prod[0] == product.id:
                    prod[1] += quantity
                    break
                else:
                    session.cart.append([product.id, quantity])
                    break
            else:
                session.cart.append([product.id, quantity])
            redirect(URL(c='default',f='checkout'))

    return dict(product=product, specification=specification, reviews=reviews, form=form)

def remove_from_cart():
    del session.cart[int(request.args(0))]
    redirect(URL(c='default',f='checkout'))

def empty_cart():
    session.cart = None
    session.balance = 0
    redirect(URL(c='default',f='checkout'))

def checkout():
    order = []
    balance = 0
    for product_id, qty in session.cart:
        product = db(db.product.id == product_id).select().first()
        total_price = qty*product.price
        order.append((product_id, qty, total_price, product))
        balance += total_price
    session.balance = balance

    button1 = A(T('Continue shopping'), _href=URL('default', 'index'))
    button2 = A(T('Buy'), _href=URL('select_address'))
    return dict(order=order, balance=balance)

@auth.requires_login()
def select_address():
    addresses = db(db.address.user_id == auth.user.id).select()

    adrs = []
    for address in addresses:
        adrs.append(address.address+', '+str(address.adr_number))

    form = SQLFORM.factory(
        Field('address', requires=IS_IN_SET(adrs))
        )
    if form.accepts(request.vars):
        session.address = form.vars.address
        redirect(URL('default', 'buy'))

    button = A(T('New address'), _href=URL('create_address'))
    return dict(addresses=addresses, button=button, form=form)

@auth.requires_login()
def create_address():
    db.address.user_id.default = auth.user.id
    db.address.user_id.readable = db.address.user_id.writable = False

    form = SQLFORM(db.address)
    if form.process().accepted:
        if session.cart and session.balance != 0:
            redirect(URL('default', 'select_address'))
        else:
            redirect(URL('default', 'index'))
    return dict(form=form)

@auth.requires_login()
def buy():
    db.pending_transaction.user_id.default = auth.user.id
    db.pending_transaction.user_id.readable = db.pending_transaction.user_id.writable = False
    db.pending_transaction.confirmed.readable = db.pending_transaction.confirmed.writable = False

    pending = dict(user_id=auth.user.id,
                    products=session.cart,
                    ammount=session.balance)

    pending_record = db.pending_transaction.insert(**pending)
    pending['id'] = pending_record
    session.pending = pending
    redirect(URL('default', 'paypal'))

@auth.requires_login()
def paypal():
    if not session.pending:
        redirect(URL('default', 'index'))
    return dict()

def success():
    log_in_file(str(request.vars), '/tmp/paypalreturn.txt')
    if request.vars.payment_status == 'Completed':
        message = T("Thank you! Your payment is completed and your order number %(invoice)s is now available." % request.vars)
        for product in session.cart:
            prod = db(db.product.id == product[0]).select().first()
            prod.update_record(quantity=prod.quantity-product[1])
            db.commit()
        session.cart = []
        session.address = None
        session.balance = 0
        session.pending = None
    else:
        message = T("Sorry, something went wrong! Try again later.")
    return dict(message=message)

def ipn():
    import json
    write_logs(request)

    pending = db.pending_transaction(id=request.vars.invoice, confirmed=False)
    if not pending:
        return 'NOT FOUND'

    already_confirmed = db.confirmed_transaction(pending_id=pending.id)
    if already_confirmed:
        return dict(status="Already Confirmed", data=already_confirmed)

    if request.vars.payment_status == 'Completed':
        confirmed = db.confirmed_transaction.insert(user_id=pending.user_id,
                                                    token_class=pending.token_class,
                                                    ammount=pending.ammount,
                                                    payment_system=pending.payment_system,
                                                    pending_id=pending.id,
                                                    payment_system_code=None,
                                                    confirmation_time=request.now,
                                                    tokens=generate_tokens(pending.token_class, peding.ammount)
                                                    )
        pending.update_record(confirmed=True)
        mail.send(to=pending.user_id.email, subject="Your payment is now confirmed", message="Thanks, your payment is confirmed.")

    else:

        path = "/tmp/ipn_not_completed.txt"
        message = '-' * 80
        message += '\nIPN NOT COMPLETED\n'
        message += str(request.vars)
        message += '\n'
        log_in_file(message, path)

    return json.dumps(request.vars)


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


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
