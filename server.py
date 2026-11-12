import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from datetime import timedelta
from flask import Flask

import config

app = Flask(__name__)
app.secret_key         = config.G_FLASK_SECRET
app.permanent_session_lifetime = timedelta(days=7)

# ─── Blueprints: Landing Page ─────────────────────────────────────────────────
from landingpage.landingpage_blueprint import landingpage_blueprint
app.register_blueprint(landingpage_blueprint, url_prefix="/")

# ─── Blueprints: Auth ─────────────────────────────────────────────────────────
from auth.auth_blueprint import auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix="/")

# ─── Blueprints: Dashboard ────────────────────────────────────────────────────
from dashboard.dashboard_blueprint import dashboard_blueprint
app.register_blueprint(dashboard_blueprint, url_prefix="/")

# ─── Blueprints: Question Bank ────────────────────────────────────────────────
from question_bank.question_bank_blueprint import question_bank_blueprint
app.register_blueprint(question_bank_blueprint, url_prefix="/")

# ─── Blueprints: Exam Package ─────────────────────────────────────────────────
from exam_package.exam_package_blueprint import exam_package_blueprint
app.register_blueprint(exam_package_blueprint, url_prefix="/")

# ─── Blueprints: Exam Engine ──────────────────────────────────────────────────
from exam_engine.exam_engine_blueprint import exam_engine_blueprint
app.register_blueprint(exam_engine_blueprint, url_prefix="/")

# ─── Blueprints: Payment ──────────────────────────────────────────────────────
from payment.payment_blueprint import payment_blueprint
app.register_blueprint(payment_blueprint, url_prefix="/")

# ─── Context: lencana sidebar (order menunggu konfirmasi) ────────────────────
import traceback
from flask import session as flask_session

@app.context_processor
def inject_pending_orders():
    try:
        if flask_session.get("role") == "super_admin":
            import database
            mgdDB   = database.get_db_conn(config.mainDB)
            pending = mgdDB.db_toefl_order.count_documents(
                {"status": "PENDING", "is_deleted": False}
            )
            return {"pending_orders": pending}
        # end if
    except Exception:
        print(traceback.format_exc())
    # end try
    return {"pending_orders": 0}
# end def

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
# end if
