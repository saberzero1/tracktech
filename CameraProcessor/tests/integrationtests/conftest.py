import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname((__file__))))
import pytest
from async_timeout import timeout


class TimeOut(int):

    @staticmethod
    def with_timeout(t):
        def wrapper(corofunc):
            async def run(*args, **kwargs):
                with timeout(t):
                    return await corofunc(*args, **kwargs)
            return run
        return wrapper


@pytest.fixture
def time_out(t):
    return TimeOut(t)
