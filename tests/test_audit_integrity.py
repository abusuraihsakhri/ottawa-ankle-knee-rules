"""Audit chain authenticity, not just linked hashes."""
from agents.base import AuditTrail


def test_tamper_evident_hmac():
    trail = AuditTrail(secret_key="non-production-test-secret")
    trail.log("tester", "test", "event", {"status": "OK"})
    trail.log("tester", "test", "event", {"status": "DONE"})
    assert trail.verify_integrity()
    snapshot = trail.get_trail()
    snapshot[0]["actor"] = "modified"
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "modified"
    assert not trail.verify_integrity()
