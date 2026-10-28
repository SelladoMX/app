"""Tests for the GitHub release check (no network)"""

from unittest.mock import MagicMock, patch

import requests

from selladomx.utils.update_checker import _CheckWorker


def _run(response=None, error=None):
    worker = _CheckWorker()
    results, errors = [], []
    worker.result.connect(results.append)
    worker.error.connect(errors.append)
    with patch("selladomx.utils.update_checker.requests.get") as get:
        if error:
            get.side_effect = error
        else:
            get.return_value = response
        worker.run()
    return get, results, errors


def _response(payload, status=200):
    response = MagicMock()
    response.json.return_value = payload
    if status >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(str(status))
    return response


def test_reports_latest_tag_without_v_prefix():
    get, results, errors = _run(_response({"tag_name": "v0.4.4"}))
    assert results == ["0.4.4"] and errors == []
    assert get.call_args.kwargs["timeout"] == 10


def test_certificate_errors_are_reported_not_raised():
    _, results, errors = _run(error=requests.exceptions.SSLError("bad cert"))
    assert results == [] and errors == ["bad cert"]


def test_http_errors_and_missing_tag_are_reported():
    assert _run(_response({}, status=403))[2] == ["403"]
    assert _run(_response({}))[2] == ["No tag found in latest release"]
