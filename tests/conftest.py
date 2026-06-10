"""Pytest configuration for fpx tests."""
import sys
from pathlib import Path
import site

try:
    import fpx
except ImportError:
    for p in site.getsitepackages() + [site.getusersitepackages()]:
        if p and (Path(p) / 'fpx').exists():
            sys.path.insert(0, str(p))
            break

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_client():
    """Returns a mock fpx client for testing model methods."""
    client = MagicMock()
    client._account.chat.send_message = AsyncMock(return_value=True)
    client._account.review.review_answer = AsyncMock(return_value=True)
    return client
