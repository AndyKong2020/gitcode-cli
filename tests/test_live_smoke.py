import os
import uuid

import pytest
from typer.testing import CliRunner

from gitcode_cli.main import app


runner = CliRunner()


@pytest.mark.skipif(not os.getenv("GITCODE_LIVE_E2E"), reason="set GITCODE_LIVE_E2E=1 to enable live smoke tests")
def test_live_repo_issue_release_smoke():
    repo_name = f"gc-live-smoke-{uuid.uuid4().hex[:8]}"
    create_repo = runner.invoke(app, ["repo", "create", repo_name, "--private", "--auto-init", "--json"])
    assert create_repo.exit_code == 0
    try:
        create_issue = runner.invoke(app, ["issue", "create", f"AndyKong2020/{repo_name}", "--title", "smoke", "--body", "smoke", "--json"])
        assert create_issue.exit_code == 0

        create_release = runner.invoke(app, ["release", "create", f"AndyKong2020/{repo_name}", "--tag", "v0.0.1", "--title", "v0.0.1", "--notes", "smoke", "--json"])
        assert create_release.exit_code == 0
    finally:
        delete_repo = runner.invoke(app, ["repo", "delete", f"AndyKong2020/{repo_name}", "--yes"])
        assert delete_repo.exit_code == 0
