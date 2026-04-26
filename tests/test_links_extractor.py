import pytest
from app.links_extractor import extract_urls_from_json, group_by_domain


class TestExtractUrlsFromJson:
    """Test cases for extract_urls_from_json function."""

    def test_extract_urls_empty_data(self):
        """Test extraction from empty data."""
        data = {}
        result = extract_urls_from_json(data)
        assert result == {}

    def test_extract_urls_no_widget_state(self):
        """Test extraction when no widget_state is present."""
        data = {"some": {"nested": {"data": "value"}}}
        result = extract_urls_from_json(data)
        assert result == {}

    def test_extract_urls_invalid_widget_state(self):
        """Test extraction with invalid widget_state JSON."""
        data = {
            "mapping": {
                "node": {
                    "widget_state": "invalid json"
                }
            }
        }
        result = extract_urls_from_json(data)
        assert result == {}

    def test_extract_urls_valid_widget_state(self):
        """Test extraction with valid widget_state containing URLs."""
        import json
        widget_state = {
            "report_message": {
                "metadata": {
                    "content_references": [
                        {
                            "url": "https://example.com/page",
                            "title": "Example Page",
                            "snippet": "An example page",
                            "attribution": "Example Source"
                        }
                    ]
                }
            }
        }
        data = {
            "mapping": {
                "node": {
                    "widget_state": json.dumps(widget_state)
                }
            }
        }
        result = extract_urls_from_json(data)
        expected = {
            "https://example.com/page": {
                "url": "https://example.com/page",
                "title": "Example Page",
                "snippet": "An example page",
                "source": "Example Source"
            }
        }
        assert result == expected

    def test_extract_urls_multiple_urls(self):
        """Test extraction of multiple URLs."""
        import json
        widget_state = {
            "report_message": {
                "metadata": {
                    "content_references": [
                        {
                            "url": "https://site1.com",
                            "title": "Site 1",
                            "snippet": "Snippet 1"
                        },
                        {
                            "url": "https://site2.com",
                            "title": "Site 2",
                            "snippet": "Snippet 2"
                        }
                    ]
                }
            }
        }
        data = {
            "mapping": {
                "node": {
                    "widget_state": json.dumps(widget_state)
                }
            }
        }
        result = extract_urls_from_json(data)
        assert len(result) == 2
        assert "https://site1.com" in result
        assert "https://site2.com" in result

    def test_extract_urls_skip_invalid_refs(self):
        """Test that invalid references are skipped."""
        import json
        widget_state = {
            "report_message": {
                "metadata": {
                    "content_references": [
                        {
                            "url": "https://valid.com",
                            "title": "Valid",
                            "invalid": False
                        },
                        {
                            "url": "https://invalid.com",
                            "title": "Invalid",
                            "invalid": True
                        }
                    ]
                }
            }
        }
        data = {
            "mapping": {
                "node": {
                    "widget_state": json.dumps(widget_state)
                }
            }
        }
        result = extract_urls_from_json(data)
        assert len(result) == 1
        assert "https://valid.com" in result
        assert "https://invalid.com" not in result

    def test_extract_urls_strip_fragments_and_slashes(self):
        """Test URL cleaning (strip fragments and trailing slashes)."""
        import json
        widget_state = {
            "report_message": {
                "metadata": {
                    "content_references": [
                        {
                            "url": "https://example.com/page/#anchor",
                            "title": "Page with anchor"
                        },
                        {
                            "url": "https://example.com/path/",
                            "title": "Path with slash"
                        }
                    ]
                }
            }
        }
        data = {
            "mapping": {
                "node": {
                    "widget_state": json.dumps(widget_state)
                }
            }
        }
        result = extract_urls_from_json(data)
        assert "https://example.com/page" in result
        assert "https://example.com/path" in result

    def test_extract_urls_non_http_urls(self):
        """Test that non-HTTP URLs are skipped."""
        import json
        widget_state = {
            "report_message": {
                "metadata": {
                    "content_references": [
                        {
                            "url": "ftp://example.com",
                            "title": "FTP URL"
                        }
                    ]
                }
            }
        }
        data = {
            "mapping": {
                "node": {
                    "widget_state": json.dumps(widget_state)
                }
            }
        }
        result = extract_urls_from_json(data)
        assert result == {}

    def test_extract_urls_first_occurrence_only(self):
        """Test that only the first occurrence of a URL is kept."""
        import json
        widget_state1 = {
            "report_message": {
                "metadata": {
                    "content_references": [
                        {
                            "url": "https://example.com",
                            "title": "First title",
                            "snippet": "First snippet"
                        }
                    ]
                }
            }
        }
        widget_state2 = {
            "report_message": {
                "metadata": {
                    "content_references": [
                        {
                            "url": "https://example.com",
                            "title": "Second title",
                            "snippet": "Second snippet"
                        }
                    ]
                }
            }
        }
        data = {
            "mapping": {
                "node1": {
                    "widget_state": json.dumps(widget_state1)
                },
                "node2": {
                    "widget_state": json.dumps(widget_state2)
                }
            }
        }
        result = extract_urls_from_json(data)
        assert len(result) == 1
        assert result["https://example.com"]["title"] == "First title"


class TestGroupByDomain:
    """Test cases for group_by_domain function."""

    def test_group_by_domain_empty(self):
        """Test grouping with empty input."""
        result = group_by_domain({})
        assert result == {}

    def test_group_by_domain_single_domain(self):
        """Test grouping URLs from the same domain."""
        refs = {
            "https://example.com/page1": {"title": "Page 1"},
            "https://example.com/page2": {"title": "Page 2"}
        }
        result = group_by_domain(refs)
        assert "example.com" in result
        assert len(result["example.com"]) == 2

    def test_group_by_domain_multiple_domains(self):
        """Test grouping URLs from different domains."""
        refs = {
            "https://site1.com": {"title": "Site 1"},
            "https://site2.com": {"title": "Site 2"},
            "https://sub.site1.com": {"title": "Sub Site 1"}
        }
        result = group_by_domain(refs)
        assert len(result) == 3
        assert "site1.com" in result
        assert "site2.com" in result
        assert "sub.site1.com" in result
        assert len(result["site1.com"]) == 2  # site1.com and sub.site1.com

    def test_group_by_domain_with_www(self):
        """Test grouping handles www prefix."""
        refs = {
            "https://www.example.com": {"title": "With www"},
            "https://example.com": {"title": "Without www"}
        }
        result = group_by_domain(refs)
        assert "example.com" in result
        assert len(result["example.com"]) == 2