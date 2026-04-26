import pytest
from app.markdowns import to_markdown


class TestToMarkdown:
    """Test cases for to_markdown function."""

    def test_to_markdown_basic(self):
        """Test basic markdown conversion."""
        data = {
            "title": "Test Conversation",
            "mapping": {
                "root": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Hello"]}
                    },
                    "children": ["child"]
                },
                "child": {
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["Hi there"]}
                    },
                    "children": []
                }
            }
        }
        result = to_markdown(data)
        expected_lines = [
            "# Test Conversation",
            "",
            "### 🧑 User",
            "Hello",
            "",
            "### 🤖 Assistant",
            "Hi there",
            "",
        ]
        expected = "\n".join(expected_lines)
        assert result == expected

    def test_to_markdown_no_title(self):
        """Test markdown conversion without title."""
        data = {
            "mapping": {
                "root": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Message"]}
                    },
                    "children": []
                }
            }
        }
        result = to_markdown(data)
        expected_lines = [
            "# ChatGPT Conversation",
            "",
            "### 🧑 User",
            "Message",
            "",
        ]
        expected = "\n".join(expected_lines)
        assert result == expected

    def test_to_markdown_different_roles(self):
        """Test markdown conversion with different message roles."""
        data = {
            "title": "Multi-role Conversation",
            "mapping": {
                "root": {
                    "message": {
                        "author": {"role": "system"},
                        "content": {"parts": ["System message"]}
                    },
                    "children": ["user"]
                },
                "user": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["User message"]}
                    },
                    "children": ["assistant"]
                },
                "assistant": {
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["Assistant message"]}
                    },
                    "children": []
                }
            }
        }
        result = to_markdown(data)
        expected_lines = [
            "# Multi-role Conversation",
            "",
            "### ⚙️ System",
            "System message",
            "",
            "### 🧑 User",
            "User message",
            "",
            "### 🤖 Assistant",
            "Assistant message",
            "",
        ]
        expected = "\n".join(expected_lines)
        assert result == expected

    def test_to_markdown_unknown_role(self):
        """Test markdown conversion with unknown role."""
        data = {
            "title": "Unknown Role",
            "mapping": {
                "root": {
                    "message": {
                        "author": {"role": "unknown"},
                        "content": {"parts": ["Unknown message"]}
                    },
                    "children": []
                }
            }
        }
        result = to_markdown(data)
        expected_lines = [
            "# Unknown Role",
            "",
            "### Unknown",
            "Unknown message",
            "",
        ]
        expected = "\n".join(expected_lines)
        assert result == expected

    def test_to_markdown_empty_messages(self):
        """Test markdown conversion with no messages."""
        data = {
            "title": "Empty Conversation",
            "mapping": {}
        }
        result = to_markdown(data)
        expected = "# Empty Conversation\n"
        assert result == expected