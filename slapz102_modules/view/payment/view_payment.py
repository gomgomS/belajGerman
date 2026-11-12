import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template


def html_catalog(packages, user):
    return render_template("peserta/catalog.html", packages=packages, user=user)
# end def


def html_checkout(package, tier, amount, user):
    return render_template("peserta/checkout.html", package=package, tier=tier, amount=amount, user=user)
# end def


def html_order_detail(order, package, user):
    return render_template("peserta/order_detail.html", order=order, package=package, user=user)
# end def


def html_peserta_history(results, orders, user):
    return render_template("peserta/history.html", results=results, orders=orders, user=user)
# end def


def html_admin_orders(orders, user):
    return render_template("admin/orders.html", orders=orders, user=user)
# end def
