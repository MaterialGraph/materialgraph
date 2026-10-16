# Objective fixtures

`cs01-objective-explore-coverage-v1.json` is the frozen production Case Study 01
post-deploy Objective Explore response
(`docs/product/literature-case-study-01/qualification/production-2026-10-09/post-deploy-20261009T034841Z/cs01_response.json`,
SHA-256 `0ae32ba2…73ac`) with an `objective_coverage` object added by running the
backend `build_objective_coverage` (contract version 1, PR #56) over that response.

The frozen capture predates the coverage field, so `ranked_material_pool_count`
(not recorded in the capture) is set equal to the returned ranked-material count.
Tests must not treat that value as a production observation.
