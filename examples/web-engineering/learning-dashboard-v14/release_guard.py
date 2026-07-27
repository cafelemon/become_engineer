"""Small, deterministic release gate used before changing the active image."""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ReleaseDecision:
    allowed: bool
    reason: str

def decide(ready: bool, schema_compatible_with_previous: bool, restore_verified: bool) -> ReleaseDecision:
    if not restore_verified: return ReleaseDecision(False, "restore-not-verified")
    if not schema_compatible_with_previous: return ReleaseDecision(False, "unsafe-database-rollback")
    if not ready: return ReleaseDecision(False, "candidate-not-ready")
    return ReleaseDecision(True, "release-allowed")
