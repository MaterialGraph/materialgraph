from scripts.check_automation_pins import (
    configured_gitleaks_images,
    validate_action_references,
    validate_gitleaks_images,
    workflow_action_references,
)


def test_every_third_party_action_uses_a_full_commit_sha():
    references = workflow_action_references()

    assert references
    assert validate_action_references() == []


def test_ci_and_local_hook_share_one_immutable_gitleaks_image():
    images = configured_gitleaks_images()

    assert len(images) == 2
    assert len(set(images)) == 1
    assert images[0].endswith(
        "@sha256:75bdb2b2f4db213cde0b8295f13a88d6b333091bbfbf3012a4e083d00d31caba"
    )
    assert validate_gitleaks_images() == []
