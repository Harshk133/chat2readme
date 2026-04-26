import pytest
from app.extractor import extract_messages


class TestExtractMessages:
    """Test cases for extract_messages function."""

    def test_extract_messages_empty_data(self):
        """Test extraction from empty data."""
        data = {"mapping": {}}
        result = extract_messages(data)
        assert result == []

    def test_extract_messages_no_root(self):
        """Test extraction when no root node exists."""
        data = {"mapping": {"node1": {"parent": "node2"}}}
        result = extract_messages(data)
        assert result == []

    def test_extract_messages_single_message(self):
        """Test extraction of a single message."""
        data = {
            "mapping": {
                "root": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Hello world"]}
                    },
                    "children": []
                }
            }
        }
        result = extract_messages(data)
        expected = [{"role": "user", "content": "Hello world"}]
        assert result == expected

    def test_extract_messages_multiple_messages(self):
        """Test extraction of multiple messages in conversation tree."""
        data = {
            "mapping": {
                "root": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["User message"]}
                    },
                    "children": ["child1"]
                },
                "child1": {
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["Assistant response"]}
                    },
                    "children": []
                }
            }
        }
        result = extract_messages(data)
        expected = [
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Assistant response"}
        ]
        assert result == expected

    def test_extract_messages_skip_empty_content(self):
        """Test that messages with empty content are skipped."""
        data = {
            "mapping": {
                "root": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": [""]}
                    },
                    "children": []
                }
            }
        }
        result = extract_messages(data)
        assert result == []

    def test_extract_messages_non_string_parts(self):
        """Test handling of non-string parts in content."""
        data = {
            "mapping": {
                "root": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Hello", 123, "world"]}
                    },
                    "children": []
                }
            }
        }
        result = extract_messages(data)
        expected = [{"role": "user", "content": "Hello world"}]
        assert result == expected

    def test_extract_messages_complex_tree(self):
        """Test extraction from a more complex conversation tree."""
        data = {
            "mapping": {
                "root": {
                    "message": {
                        "author": {"role": "system"},
                        "content": {"parts": ["System prompt"]}
                    },
                    "children": ["a", "b"]
                },
                "a": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Question 1"]}
                    },
                    "children": ["a1"]
                },
                "a1": {
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["Answer 1"]}
                    },
                    "children": []
                },
                "b": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Question 2"]}
                    },
                    "children": ["b1"]
                },
                "b1": {
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["Answer 2"]}
                    },
                    "children": []
                }
            }
        }
        result = extract_messages(data)
        expected = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Question 1"},
            {"role": "assistant", "content": "Answer 1"},
            {"role": "user", "content": "Question 2"},
            {"role": "assistant", "content": "Answer 2"}
        ]
        assert result == expected