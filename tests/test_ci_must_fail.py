# Throwaway: proves Backend Tests fails when a test fails. Never merge.
def test_ci_must_fail():
    assert False, "deliberate failure to verify the CI gate"
