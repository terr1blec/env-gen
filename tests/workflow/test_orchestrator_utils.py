import pathlib
import sys


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from workflow.orchestrator import _is_approved, _dataset_revision_requested


def test_is_approved_accepts_plain_text():
    assert _is_approved("APPROVED: looks good")


def test_is_approved_handles_markdown_prefix():
    assert _is_approved("**APPROVED:** all good")


def test_is_approved_rejects_non_approved():
    assert not _is_approved("REVISIONS_NEEDED: fix")


def test_dataset_revision_requested_detects_issues():
    feedback = "Dataset mismatch: calendars key missing"
    assert _dataset_revision_requested(feedback)


def test_dataset_revision_requested_ignores_unrelated_feedback():
    feedback = "Server tool needs better validation"
    assert not _dataset_revision_requested(feedback)

