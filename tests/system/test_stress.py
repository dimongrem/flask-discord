from concurrent.futures import ProcessPoolExecutor, as_completed

import pytest

from tests.system.test_once import test_once

RUNS_NUM = 250
PROCESS_NUM = 4


@pytest.mark.usefixtures("app")
@pytest.mark.usefixtures("test_user")
@pytest.mark.usefixtures("user_connection")
@pytest.mark.usefixtures("guild")
def test_sys_stress(app, test_user, user_connection, guild, mocker):
    successes = 0

    with ProcessPoolExecutor(max_workers=PROCESS_NUM) as executor:
        futures = [executor.submit(test_once(app, test_user, user_connection, guild, mocker)) for _ in range(RUNS_NUM)]
        for _ in as_completed(futures):
            successes += 1

    assert successes == RUNS_NUM
