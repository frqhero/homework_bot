import requests
import pytest
import exceptions


class TestMine:
    def test_get_api_answer(self, caplog, monkeypatch):
        import homework

        class MockClass:
            status_code = 404

            def __init__(self, *args, **kwargs):
                pass

        monkeypatch.setattr(requests, 'get', MockClass)

        with pytest.raises(exceptions.Not200StatusCodeResponse):
            homework.get_api_answer(0)
