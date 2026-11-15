import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback
from urllib.parse import quote
from flask import Blueprint, request, redirect, g, jsonify, session

from middleware import middleware_privilege
from view.payment import view_payment
import sanitize

payment_blueprint = Blueprint("payment_blueprint", __name__)


@payment_blueprint.route("/catalog", methods=["GET"])
def catalog_legacy():
    # katalog per-item sudah dipensiunkan → arahkan ke struktur baru
    if session.get("session_id") and session.get("role") in ("peserta", "super_admin"):
        return redirect("/student")
    # end if
    return redirect("/#harga")
# end def


@payment_blueprint.route("/checkout/<package_pkey>/<tier>", methods=["GET"])
@middleware_privilege(roles=["peserta", "super_admin"])
def checkout_legacy(package_pkey, tier):
    # pembelian per paket diganti langganan
    return redirect("/student/preise")
# end def


@payment_blueprint.route("/order/create", methods=["POST"])
@middleware_privilege(roles=["peserta", "super_admin"])
def create_order_legacy():
    return redirect("/student/preise")
# end def


@payment_blueprint.route("/student/abo/subscribe", methods=["POST"])
@middleware_privilege(roles=["peserta", "super_admin"])
def subscribe_post():
    try:
        params    = sanitize.clean_html_dic(request.form.to_dict())
        plan_code = params.get("plan_code", "")
        cycle     = params.get("cycle", "MONTHLY")

        from payment import payment_proc
        result = payment_proc.create_subscription_order(
            user_pkey = g.current_user["user_id"],
            plan_code = plan_code,
            cycle     = cycle,
        )

        if result["status"] != "OK":
            return redirect("/student/preise?error=" + quote(result.get("message", "Gagal membuat order")))
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
            return redirect("/student/verlauf")
        # end if

        package = None
        if order.get("order_type") != "SUBSCRIPTION":
            package_result = exam_package_proc.get_package_by_id(order.get("fk_package_id", ""))
            package        = package_result.get("data")
        # end if

        return view_payment.html_order_detail(
            order   = order,
            package = package,
            user    = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@payment_blueprint.route("/peserta/riwayat", methods=["GET"])
def peserta_history_legacy():
    return redirect("/student/verlauf")
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
