import pytest
import os

from pullman.utils import get_pull_at_head

@pytest.mark.skipif(
    not 'HAMSTER_GITHUB_API_TOKEN' in os.environ.keys(),
    reason='This test makes a webservice call that needs ot be mocked'
)
def test_pull_from_sha():
    pass