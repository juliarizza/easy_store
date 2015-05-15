# -*- coding: utf-8 -*-

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