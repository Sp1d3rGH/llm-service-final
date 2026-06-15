import pytest
from fakeredis.aioredis import FakeRedis


@pytest.fixture(autouse=True)
def mock_get_redis(mocker):
    """
    Автоматически подменяет get_redis в модуле handlers на FakeRedis.
    Возвращает экземпляр FakeRedis для использования в тестах.
    """
    fake_redis = FakeRedis(decode_responses=True)
    mocker.patch("app.bot.handlers.get_redis", return_value=fake_redis)
    return fake_redis
