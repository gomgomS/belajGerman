import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback
import time
from flask import Blueprint, request, redirect, g, session as flask_session

from middleware import middleware_privilege
from view.student import view_student

student_blueprint = Blueprint("student_blueprint", __name__)


@student_blueprint.app_context_processor
def _inject_header_abo():
    """Suntik info paket & kredit AI untuk chip di header student shell."""
    try:
        if not flask_session.get("session_id") or flask_session.get("role") not in ("peserta", "super_admin"):
            return {}
        # end if
        current_user = g.get("current_user") or {}
        user_pkey    = current_user.get("user_id", "")
        if not user_pkey:
            return {}
        # end if
        from payment import payment_proc
        subscription = _decorate_subscription(
            payment_proc.get_active_subscription(user_pkey).get("data")
        )
        if subscription:
            plan = subscription.get("plan_data") or {}
            payment_proc.ensure_subscription_credit_backfill(user_pkey)
            credits = payment_proc.get_credit_balance(user_pkey)
            return {"header_abo": {
                "active"    : True,
                "plan_label": plan.get("label", subscription.get("tier", "")),
                "credits"   : credits,
                "expire_str": subscription.get("expire_at_str", ""),
            }}
        # end if

        # tanpa langganan → tampilkan kuota paket Free
        import database
        import config
        mgdDB  = database.get_db_conn(config.mainDB)
        free   = mgdDB.db_subscription_plan.find_one({"code": "FREE", "is_deleted": False}) or {}
        return {"header_abo": {
            "active"    : False,
            "plan_label": free.get("label", "Free"),
            "credits"   : int(free.get("ai_credits_monthly", 0) or 0),
            "expire_str": "",
        }}
    except Exception:
        print(traceback.format_exc())
        return {}
    # end try
# end def


def _decorate_subscription(subscription):
    """Tambah field turunan (sisa hari, tanggal expire) ke record langganan."""
    if not subscription:
        return subscription
    # end if
    expire_at = subscription.get("expire_at", 0) or 0
    if expire_at:
        subscription["expire_at_str"] = time.strftime("%d %b %Y", time.gmtime(expire_at / 1000.0))
        subscription["days_left"] = max(0, int((expire_at - time.time() * 1000) / 86400000))
    else:
        subscription["expire_at_str"] = ""
        subscription["days_left"] = 0
    # end if
    return subscription
# end def


@student_blueprint.route("/student", methods=["GET"])
@middleware_privilege(roles=["peserta", "super_admin"])
def student_dashboard():
    """Übersicht — dasbor siswa (istilah Jerman, penjelasan Indonesia)."""
    try:
        from app_settings import app_settings_proc
        from dashboard     import dashboard_proc
        from exam_engine   import exam_engine_proc
        from exam_package  import exam_package_proc
        from payment       import payment_proc

        stats       = dashboard_proc.get_peserta_stats(g.current_user["user_id"])
        results     = exam_engine_proc.get_user_results(g.current_user["user_id"]).get("data", [])
        packages    = exam_package_proc.get_all_packages(status="PUBLISHED").get("data", [])
        subscription = _decorate_subscription(payment_proc.get_active_subscription(g.current_user["user_id"]).get("data"))
        plans       = app_settings_proc.get_public_sub_plans().get("data", [])

        scores = [r.get("total_score", 0) or 0 for r in results]
        stats["avg_score"] = int(round(sum(scores) / float(len(scores)))) if scores else 0
        stats["best_score"] = max(scores) if scores else 0

        # kredit + status buka paket premium
        payment_proc.ensure_subscription_credit_backfill(g.current_user["user_id"])
        credit_balance = payment_proc.get_credit_balance(g.current_user["user_id"])
        unlocked = set()
        if packages:
            import database
            import config
            mgdDB = database.get_db_conn(config.mainDB)
            for row in mgdDB.db_credit_ledger.find({
                "fk_user_id": g.current_user["user_id"], "trx_type": "EXAM_UNLOCK",
            }, {"fk_package_id": 1}):
                unlocked.add(row.get("fk_package_id", ""))
            # end for
        # end if
        for pkg in packages:
            if pkg.get("is_premium"):
                pkg["premium_locked"] = bool(subscription) and pkg["pkey"] not in unlocked
                pkg["balance_after"]  = credit_balance - int(pkg.get("premium_credit_cost", 10) or 10)
            else:
                pkg["premium_locked"] = False
            # end if
        # end for

        # pisahkan ujian reguler vs premium
        regular_packages = [p for p in packages if not p.get("is_premium")]
        premium_packages = [p for p in packages if p.get("is_premium")]

        return view_student.html_student_dashboard(
            stats            = stats,
            results          = results[:5],
            packages         = packages,
            regular_packages = regular_packages,
            premium_packages = premium_packages,
            subscription     = subscription,
            sub_plans        = plans,
            credit_balance   = credit_balance,
            credit_error     = request.args.get("credit_error", ""),
            credit_ok        = request.args.get("credit_ok", ""),
            user             = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@student_blueprint.route("/student/preise", methods=["GET"])
@middleware_privilege(roles=["peserta", "super_admin"])
def student_pricing():
    """Abo & Preise — pilih paket langganan + durasi (bulanan / 3 bulan / tahunan)."""
    try:
        from app_settings import app_settings_proc
        from payment      import payment_proc

        plans        = app_settings_proc.get_public_sub_plans().get("data", [])
        subscription = _decorate_subscription(payment_proc.get_active_subscription(g.current_user["user_id"]).get("data"))

        return view_student.html_student_pricing(
            sub_plans    = plans,
            subscription = subscription,
            error        = request.args.get("error", ""),
            user         = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@student_blueprint.route("/student/abo", methods=["GET"])
@middleware_privilege(roles=["peserta", "super_admin"])
def student_subscription():
    """Mein Abo — status langganan berjalan."""
    try:
        from app_settings import app_settings_proc
        from payment      import payment_proc

        subscription = _decorate_subscription(payment_proc.get_active_subscription(g.current_user["user_id"]).get("data"))
        plans        = app_settings_proc.get_public_sub_plans().get("data", [])

        return view_student.html_student_subscription(
            subscription = subscription,
            sub_plans    = plans,
            user         = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def


@student_blueprint.route("/student/verlauf", methods=["GET"])
@middleware_privilege(roles=["peserta", "super_admin"])
def student_history():
    """Verlauf — riwayat ujian & pembayaran.
    Abo aktif → semua hasil terlihat. Abo berakhir → hasil terkunci ( teaser 2 terakhir, tanggal tetap tampil);
    berlangganan lagi → seluruh hasil masa lalu terbuka kembali."""
    try:
        from exam_engine import exam_engine_proc
        from payment     import payment_proc

        results = exam_engine_proc.get_user_results(g.current_user["user_id"]).get("data", [])
        orders  = payment_proc.get_user_orders(g.current_user["user_id"]).get("data", [])
        subscription = _decorate_subscription(
            payment_proc.get_active_subscription(g.current_user["user_id"]).get("data")
        )

        results_locked = False
        teaser_results = []
        if not subscription:
            results_locked = True
            # teaser: 2 hasil terakhir — judul & tanggal tampil, skor terkunci
            teaser_results = results[:2]
        # end if

        return view_student.html_student_history(
            results         = results,
            orders          = orders,
            results_locked  = results_locked,
            teaser_results  = teaser_results,
            total_results   = len(results),
            user            = g.current_user,
        )
    except Exception:
        print(traceback.format_exc())
        return "Terjadi kesalahan", 500
    # end try
# end def
