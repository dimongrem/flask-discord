import pytest

from tests.system.test_once import test_once

RUNS_NUM = 250


@pytest.mark.usefixtures("app")
@pytest.mark.usefixtures("test_user")
@pytest.mark.usefixtures("user_connection")
@pytest.mark.usefixtures("guild")
def test_sys_volume(app, test_user, user_connection, guild, mocker):
    successes = 0
    for _ in range(RUNS_NUM):
        try:
            test_once(app, test_user, user_connection, guild, mocker)
            successes += 1
        except:
            pass

    assert successes == RUNS_NUM
