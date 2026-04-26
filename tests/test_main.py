import pytest
from app.main import get_share_id, append_links_section


class TestGetShareId:
    """Test cases for get_share_id function."""

    def test_get_share_id_standard_url(self):
        """Test extraction from standard share URL."""
        url = "https://chatgpt.com/share/69ecfbba-0344-8323-9451-3ca4d223069b"
        result = get_share_id(url)
        assert result == "69ecfbba-0344-8323-9451-3ca4d223069b"

    def test_get_share_id_url_with_trailing_slash(self):
        """Test extraction from URL with trailing slash."""
        url = "https://chatgpt.com/share/abc123/"
        result = get_share_id(url)
        assert result == "abc123"

    def test_get_share_id_backend_api_url(self):
        """Test extraction from backend API URL."""
        url = "https://chatgpt.com/backend-api/share/xyz789"
        result = get_share_id(url)
        assert result == "xyz789"

    def test_get_share_id_custom_domain(self):
        """Test extraction from custom domain URL."""
        url = "https://custom.com/share/def456"
        result = get_share_id(url)
        assert result == "def456"


class TestAppendLinksSection:
    """Test cases for append_links_section function."""

    def test_append_links_section_empty_links(self):
        """Test appending with no links."""
        markdown = "# Title\n\nContent"
        result = append_links_section(markdown, {})
        assert result == markdown

    def test_append_links_section_with_links(self):
        """Test appending with links present."""
        markdown = "# Title\n\nContent"
        links = {
            "https://example.com": {
                "title": "Example",
                "snippet": "An example site"
            },
            "https://test.com": {
                "title": "Test",
                "snippet": ""
            }
        }
        result = append_links_section(markdown, links)
        expected = (
            "# Title\n\nContent\n\n---\n\n## References\n\n"
            "- [Example](https://example.com)\n  - An example site\n\n"
            "- [Test](https://test.com)\n\n"
        )
        assert result == expected

    def test_append_links_section_no_snippet(self):
        """Test appending links without snippets."""
        markdown = "Content"
        links = {
            "https://example.com": {
                "title": "Example"
            }
        }
        result = append_links_section(markdown, links)
        expected = (
            "Content\n\n---\n\n## References\n\n"
            "- [Example](https://example.com)\n\n"
        )
        assert result == expected

    def test_append_links_section_url_as_title_fallback(self):
        """Test using URL as title when title is missing."""
        markdown = "Content"
        links = {
            "https://example.com": {
                "snippet": "Snippet"
            }
        }
        result = append_links_section(markdown, links)
        expected = (
            "Content\n\n---\n\n## References\n\n"
            "- [https://example.com](https://example.com)\n  - Snippet\n\n"
        )
        assert result == expected