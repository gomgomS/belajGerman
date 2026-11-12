import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import uuid


def _get_api_call_id():
    return str(uuid.uuid4()).replace("-", "")[:16].upper()
# end def


def _get_unique_id():
    return str(uuid.uuid4()).replace("-", "")
# end def


def _get_short_id():
    return str(uuid.uuid4()).replace("-", "")[:8].upper()
# end def
