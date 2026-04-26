import pytest
from unittest.mock import Mock, patch
from app.fetcher import fetch_chatgpt_share


class TestFetchChatgptShare:
    """Test cases for fetch_chatgpt_share function."""

    @patch('app.fetcher.requests.Session')
    def test_fetch_chatgpt_share_standard_url(self, mock_session_class):
        """Test fetching with standard share URL."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"title": "Test", "mapping": {}}
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        url = "https://chatgpt.com/share/abc123"
        result = fetch_chatgpt_share(url)

        # Check that session was created
        mock_session_class.assert_called_once()

        # Check that share page was visited first
        mock_session.get.assert_any_call("https://chatgpt.com/share/abc123", timeout=20)

        # Check that API was called
        mock_session.get.assert_any_call(
            "https://chatgpt.com/backend-api/share/abc123",
            headers={
                "Accept": "application/json",
                "Referer": "https://chatgpt.com/share/abc123",
            },
            timeout=20,
        )

        assert result == {"title": "Test", "mapping": {}}

    @patch('app.fetcher.requests.Session')
    def test_fetch_chatgpt_share_backend_url(self, mock_session_class):
        """Test fetching with backend API URL directly."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        url = "https://chatgpt.com/backend-api/share/xyz789"
        result = fetch_chatgpt_share(url)

        # Should not modify the URL
        mock_session.get.assert_any_call(url, headers={"Accept": "application/json", "Referer": "https://chatgpt.com/share/xyz789"}, timeout=20)
        assert result == {"data": "test"}

    @patch('app.fetcher.requests.Session')
    def test_fetch_chatgpt_share_with_trailing_slash(self, mock_session_class):
        """Test fetching URL with trailing slash."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        url = "https://chatgpt.com/share/def456/"
        result = fetch_chatgpt_share(url)

        # Should strip trailing slash
        mock_session.get.assert_any_call(
            "https://chatgpt.com/backend-api/share/def456",
            headers={
                "Accept": "application/json",
                "Referer": "https://chatgpt.com/share/def456",
            },
            timeout=20,
        )

    @patch('app.fetcher.requests.Session')
    def test_fetch_chatgpt_share_request_failure(self, mock_session_class):
        """Test handling of request failure."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Request failed")
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        url = "https://chatgpt.com/share/test"

        with pytest.raises(Exception, match="Request failed"):
            fetch_chatgpt_share(url)

    @patch('app.fetcher.requests.Session')
    def test_fetch_chatgpt_share_timeout(self, mock_session_class):
        """Test handling of timeout."""
        mock_session = Mock()
        mock_session.get.side_effect = TimeoutError("Timeout")
        mock_session_class.return_value = mock_session

        url = "https://chatgpt.com/share/test"

        with pytest.raises(TimeoutError):
            fetch_chatgpt_share(url)