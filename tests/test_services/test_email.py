import pytest
from unittest.mock import patch
from app.services.email import send_email

@patch("app.services.email.requests.post")
def test_send_email_success(mock_post):
    mock_post.return_value.status_code = 200

    subject = "Test Subject"
    to_email = "test@example.com"
    body = "Test Body"

    send_email(subject, to_email, body)

    mock_post.assert_called_once()

@patch("app.services.email.requests.post")
def test_send_email_failure(mock_post):
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad Request"

    subject = "Test Subject"
    to_email = "test@example.com"
    body = "Test Body"

    send_email(subject, to_email, body)

    mock_post.assert_called_once()
