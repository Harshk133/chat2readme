import pytest
from app.image_extractor import extract_images, build_image_url, build_readme


class TestExtractImages:
    """Test cases for extract_images function."""

    def test_extract_images_empty_data(self):
        """Test extraction from empty data."""
        data = {}
        result = extract_images(data)
        assert result == []

    def test_extract_images_no_images(self):
        """Test extraction when no images are present."""
        data = {
            "mapping": {
                "node": {
                    "message": {
                        "content": {"parts": ["Text only"]}
                    }
                }
            }
        }
        result = extract_images(data)
        assert result == []

    def test_extract_images_single_image(self):
        """Test extraction of a single image."""
        data = {
            "conversation_id": "default-conv",
            "mapping": {
                "node": {
                    "message": {
                        "content": {
                            "parts": [
                                {
                                    "content_type": "image_asset_pointer",
                                    "asset_pointer": "sediment://file_abc123?shared_conversation_id=conv456",
                                    "metadata": {
                                        "dalle": {
                                            "gen_id": "gen789",
                                            "prompt": "A beautiful landscape"
                                        }
                                    },
                                    "width": 1024,
                                    "height": 768,
                                    "size_bytes": 123456
                                }
                            ]
                        }
                    }
                }
            }
        }
        result = extract_images(data)
        assert len(result) == 1
        img = result[0]
        assert img["file_id"] == "file_abc123"
        assert img["conv_id"] == "conv456"
        assert img["gen_id"] == "gen789"
        assert img["prompt"] == "A beautiful landscape"
        assert img["width"] == 1024
        assert img["height"] == 768
        assert img["size_bytes"] == 123456
        assert not img["is_error"]

    def test_extract_images_with_title_and_error(self):
        """Test extraction with title from metadata and error flag."""
        data = {
            "mapping": {
                "node": {
                    "message": {
                        "content": {
                            "parts": [
                                {
                                    "content_type": "image_asset_pointer",
                                    "asset_pointer": "sediment://file_def456?shared_conversation_id=conv789",
                                    "metadata": {}
                                }
                            ]
                        },
                        "metadata": {
                            "response_message_id": "file_def456",
                            "async_task_title": "Test Image",
                            "is_error": True
                        }
                    }
                }
            }
        }
        result = extract_images(data)
        assert len(result) == 1
        img = result[0]
        assert img["file_id"] == "file_def456"
        assert img["title"] == "Test Image"
        assert img["is_error"]

    def test_extract_images_duplicate_removal(self):
        """Test that duplicate images are removed."""
        data = {
            "mapping": {
                "node1": {
                    "message": {
                        "content": {
                            "parts": [
                                {
                                    "content_type": "image_asset_pointer",
                                    "asset_pointer": "sediment://file_abc123?shared_conversation_id=conv",
                                    "metadata": {}
                                }
                            ]
                        }
                    }
                },
                "node2": {
                    "message": {
                        "content": {
                            "parts": [
                                {
                                    "content_type": "image_asset_pointer",
                                    "asset_pointer": "sediment://file_abc123?shared_conversation_id=conv",
                                    "metadata": {}
                                }
                            ]
                        }
                    }
                }
            }
        }
        result = extract_images(data)
        assert len(result) == 1

    def test_extract_images_malformed_asset_pointer(self):
        """Test handling of malformed asset pointers."""
        data = {
            "mapping": {
                "node": {
                    "message": {
                        "content": {
                            "parts": [
                                {
                                    "content_type": "image_asset_pointer",
                                    "asset_pointer": "malformed",
                                    "metadata": {}
                                }
                            ]
                        }
                    }
                }
            }
        }
        result = extract_images(data)
        assert result == []


class TestBuildImageUrl:
    """Test cases for build_image_url function."""

    def test_build_image_url_basic(self):
        """Test basic URL construction."""
        result = build_image_url("file_abc123", "conv456")
        expected = (
            "https://files.oaiusercontent.com/file_abc123?"
            "se=shared&sp=r&spr=https&sv=2021-08-06&sr=b&shared_conversation_id=conv456"
        )
        assert result == expected

    def test_build_image_url_special_chars(self):
        """Test URL construction with special characters in IDs."""
        result = build_image_url("file_abc-123_def", "conv-456_789")
        expected = (
            "https://files.oaiusercontent.com/file_abc-123_def?"
            "se=shared&sp=r&spr=https&sv=2021-08-06&sr=b&shared_conversation_id=conv-456_789"
        )
        assert result == expected


class TestBuildReadme:
    """Test cases for build_readme function."""

    def test_build_readme_empty_images(self):
        """Test README building with no images."""
        result = build_readme([])
        expected = (
            "# ChatGPT Generated Images\n\n"
            "> Images generated by ChatGPT in this conversation.\n"
            "> Total images: **0**\n\n"
            "---\n\n"
            "*No successfully generated images found in this conversation.*"
        )
        assert result == expected

    def test_build_readme_with_title(self):
        """Test README building with custom title."""
        images = []
        result = build_readme(images, "Custom Title")
        expected = (
            "# Custom Title\n\n"
            "> Images generated by ChatGPT in this conversation.\n"
            "> Total images: **0**\n\n"
            "---\n\n"
            "*No successfully generated images found in this conversation.*"
        )
        assert result == expected

    def test_build_readme_single_image(self):
        """Test README building with a single image."""
        images = [
            {
                "file_id": "file_abc123",
                "conv_id": "conv456",
                "gen_id": "gen789",
                "prompt": "A test image",
                "title": "Test Image",
                "width": 512,
                "height": 512,
                "size_bytes": 12345,
                "orientation": "square",
                "is_error": False
            }
        ]
        result = build_readme(images, "Test Chat")
        assert "# Test Chat" in result
        assert "Images generated by ChatGPT in this conversation" in result
        assert "Total images: **1**" in result
        assert "![Test Image](https://files.oaiusercontent.com/file_abc123?" in result
        assert "512 × 512 px" in result

    def test_build_readme_skip_error_images(self):
        """Test that error images are skipped."""
        images = [
            {
                "file_id": "file_good",
                "conv_id": "conv",
                "is_error": False,
                "prompt": "Good image",
                "title": "",
                "width": 100,
                "height": 100,
                "size_bytes": 1000,
                "orientation": "",
                "gen_id": ""
            },
            {
                "file_id": "file_bad",
                "conv_id": "conv",
                "is_error": True,
                "prompt": "Bad image",
                "title": "",
                "width": 100,
                "height": 100,
                "size_bytes": 1000,
                "orientation": "",
                "gen_id": ""
            }
        ]
        result = build_readme(images)
        assert "file_good" in result
        assert "file_bad" not in result
        assert "Total images: **1**" in result