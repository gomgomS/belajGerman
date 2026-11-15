import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template


def html_order_detail(order, package, user):
    return render_template("student/order_detail.html", order=order, package=package, user=user)
# end def


def html_admin_orders(orders, user):
    return render_template("admin/orders.html", orders=orders, user=user)
# end def
