"""Public API surface for frappe_hr_ui.

Whitelisted endpoints live in domain modules under this package; everything is
re-exported here so existing call paths (``frappe_hr_ui.api.<name>``) and imports
keep working unchanged. Domain modules are carved out of ``core`` incrementally.
"""

from .core import *  # noqa: F401, F403
from .core import COMPANY_NAME, _require_hr  # noqa: F401  helpers other modules import
from .reports import *  # noqa: F401, F403
