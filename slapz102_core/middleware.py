import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import time
import traceback
from functools import wraps
from flask import session, redirect, g

import database
import config


def middleware_privilege(roles=None):
    if roles is None:
        roles = []
    # end if

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session_id = session.get("session_id")

            if not session_id:
                return redirect("/login")
            # end if

            try:
                mgdDB = database.get_db_conn(config.mainDB)
                sess  = mgdDB.db_toefl_session.find_one({
                    "session_id" : session_id,
                    "is_active"  : True,
                })

                if not sess:
                    session.clear()
                    return redirect("/login")
                # end if

                if sess.get("expire_time", 0) < int(time.time() * 1000):
                    session.clear()
                    mgdDB.db_toefl_session.update_one(
                        {"session_id": session_id},
                        {"$set": {"is_active": False}}
                    )
                    return redirect("/login")
                # end if

                if roles and sess.get("role") not in roles:
                    return redirect("/unauthorized")
                # end if

                g.current_user = {
                    "user_id"   : sess.get("fk_user_id", ""),
                    "username"  : sess.get("username", ""),
                    "role"      : sess.get("role", ""),
                    "full_name" : sess.get("full_name", ""),
                }

            except Exception:
                print(traceback.format_exc())
                return redirect("/login")
            # end try

            return f(*args, **kwargs)
        # end def

        return decorated_function
    # end def

    return decorator
# end def
