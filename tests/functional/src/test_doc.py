from http import HTTPStatus

from flask import url_for

from tests.functional.conftest import ERROR_INFO


class TestDocAPI:
    def test_doc_redoc_get(self, test_client):
        url = url_for("openapi_v1/doc_redoc")
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(url)
        assert response.status_code == status, (
            ERROR_INFO.format(method=method, url=url, status=status)
        )

    def test_doc_get(self, test_client):
        url = url_for("openapi_v1/doc_swagger")
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(url)
        assert response.status_code == status, (
            ERROR_INFO.format(method=method, url=url, status=status)
        )
