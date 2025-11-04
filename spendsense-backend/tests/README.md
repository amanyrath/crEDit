# Test Categories
# 
# Essential Tests (must pass):
# - test_main.py - Basic health checks
# - test_env.py - Environment configuration
# - test_rbac.py - Core RBAC logic (unit tests)
# - At least one successful endpoint test per API route
#
# Optional Tests (can skip for MVP):
# - Edge case tests (invalid inputs, boundary conditions)
# - Duplicate functionality tests
# - Integration tests for seeding scripts
#
# To run only essential tests:
#   pytest -m "not skip"
#
# To skip specific tests:
#   @pytest.mark.skip(reason="Edge case - can fix later")

