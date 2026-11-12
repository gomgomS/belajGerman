import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback
from flask import Blueprint, request, redirect, g, jsonify

from middleware import middleware_privilege
from view.payment import view_payment
import sanitize

payment_blueprint = Blueprint("payment_blueprint", __name__)


@payment_blueprint.route("/catalog", methods=["GET"])
def catalog():
    try:
        from exam_package import exam_package_proc
        result = exam_package_proc.get_all_packages(status="PUBLISHED")
        return view_payment.html_catalog(
            packages = result.get("data", []),
            user     = g.current_user if hasattr(g, "current_user") else None,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@payment_blueprint.route("/checkout/<package_pkey>/<tier>", methods=["GET"])
@middleware_privilege(roles=["peserta", "super_admin"])
def checkout_page(package_pkey, tier):
    try:
        from exam_package import exam_package_proc
        from payment      import payment_proc

        package_result = exam_package_proc.get_package_by_id(package_pkey)
        package        = package_result.get("data")
        if not package:
            return redirect("/catalog")
        # end if

        existing_access = payment_proc.check_user_access(g.current_user["user_id"], package_pkey)
        if existing_access["has_access"]:
            return redirect("/exam/" + package_pkey + "/start")
        # end if

        tier   = tier.upper()
        amount = package.get("price_premium", 0) if tier == "PREMIUM" else package.get("price_basic", 0)

        return view_payment.html_checkout(
            package = package,
            tier    = tier,
            amount  = amount,
            user    = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@payment_blueprint.route("/order/create", methods=["POST"])
@middleware_privilege(roles=["peserta", "super_admin"])
def create_order_post():
    try:
        params      = sanitize.clean_html_dic(request.form.to_dict())
        package_pkey = params.get("package_pkey", "")
        tier         = params.get("tier", "BASIC")

        from payment import payment_proc
        result = payment_proc.create_order(
            user_pkey    = g.current_user["user_id"],
            package_pkey = package_pkey,
            tier         = tier,
        )

        if result["status"] != "OK":
            return redirect("/checkout/" + package_pkey + "/" + tier)
        # end if

        return redirect("/order/" + result["order_pkey"])
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@payment_blueprint.route("/order/<order_pkey>", methods=["GET"])
@middleware_privilege(roles=["peserta", "super_admin"])
def order_detail(order_pkey):
    try:
        from payment      import payment_proc
        from exam_package import exam_package_proc

        order_result   = payment_proc.get_order_by_id(order_pkey)
        order          = order_result.get("data")
        if not order or order.get("fk_user_id") != g.current_user["user_id"]:
            return redirect("/peserta/riwayat")
        # end if

        package_result = exam_package_proc.get_package_by_id(order.get("fk_package_id", ""))

        return view_payment.html_order_detail(
            order   = order,
            package = package_result.get("data"),
            user    = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@payment_blueprint.route("/peserta/riwayat", methods=["GET"])
@middleware_privilege(roles=["peserta", "super_admin"])
def peserta_history():
    try:
        from exam_engine import exam_engine_proc
        from payment     import payment_proc

        results_data = exam_engine_proc.get_user_results(g.current_user["user_id"])
        orders_data  = payment_proc.get_user_orders(g.current_user["user_id"])

        return view_payment.html_peserta_history(
            results = results_data.get("data", []),
            orders  = orders_data.get("data", []),
            user    = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@payment_blueprint.route("/dashboard/admin/orders", methods=["GET"])
@middleware_privilege(roles=["super_admin"])
def admin_orders():
    try:
        from payment import payment_proc
        status = request.args.get("status", "")
        result = payment_proc.get_all_orders(status=status if status else None)
        return view_payment.html_admin_orders(
            orders = result.get("data", []),
            user   = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@payment_blueprint.route("/api/admin/order/<order_pkey>/confirm", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def confirm_order_api(order_pkey):
    try:
        from payment import payment_proc
        result = payment_proc.confirm_order(order_pkey, g.current_user["user_id"])
        return jsonify(result)
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR"}), 500
    # end try
# end def


@payment_blueprint.route("/api/admin/order/<order_pkey>/cancel", methods=["POST"])
@middleware_privilege(roles=["super_admin"])
def cancel_order_api(order_pkey):
    try:
        from payment import payment_proc
        result = payment_proc.cancel_order(order_pkey)
        return jsonify(result)
    except Exception:
        print(traceback.format_exc())
        return jsonify({"status": "ERROR"}), 500
    # end try
# end def
