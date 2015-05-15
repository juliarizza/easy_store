# -*- coding: utf-8 -*-
def index():
    redirect(URL(c='default', f='index'))

def show_products():
    if request.vars.category:
        product_list = db(db.product.default_category == request.vars.category).select(limitby=(0,20),
                                                                            orderby=db.product.name)
    else:
        product_list = db(db.product).select(limitby=(0,20), orderby=~db.product.name)
    return locals()
    
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

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
