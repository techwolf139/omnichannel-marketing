"""Tests for note_publisher module."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.note_publisher import NotePublisher


class TestNotePublisher:
    """Test cases for NotePublisher class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.publisher = NotePublisher()
        self.valid_content = {
            "title": "测试标题",
            "content": "测试内容",
            "topics": ["测试"]
        }
        self.valid_images = ["image1.jpg"]
    
    def test_create_note_success(self):
        """Test creating a note successfully."""
        note_id = self.publisher.create_note(self.valid_content, self.valid_images)
        
        assert isinstance(note_id, str)
        assert note_id.startswith("note_")
        
        # Verify draft was stored
        draft = self.publisher.get_draft(note_id)
        assert draft is not None
        assert draft["title"] == "测试标题"
    
    def test_create_note_missing_title(self):
        """Test creating note without title raises error."""
        content = {"content": "No title"}
        
        with pytest.raises(ValueError) as exc_info:
            self.publisher.create_note(content, self.valid_images)
        
        assert "Title is required" in str(exc_info.value)
    
    def test_create_note_title_too_long(self):
        """Test creating note with title exceeding max length."""
        content = {"title": "这" * 21}
        
        with pytest.raises(ValueError) as exc_info:
            self.publisher.create_note(content, self.valid_images)
        
        assert "Title too long" in str(exc_info.value)
    
    def test_create_note_no_images(self):
        """Test creating note without images raises error."""
        with pytest.raises(ValueError) as exc_info:
            self.publisher.create_note(self.valid_content, [])
        
        assert "image required" in str(exc_info.value)
    
    def test_create_note_too_many_images(self):
        """Test creating note with too many images raises error."""
        images = [f"image{i}.jpg" for i in range(20)]
        
        with pytest.raises(ValueError) as exc_info:
            self.publisher.create_note(self.valid_content, images)
        
        assert "Max 18 images" in str(exc_info.value)
    
    def test_publish_note_success(self):
        """Test publishing a note successfully."""
        note_id = self.publisher.create_note(self.valid_content, self.valid_images)
        result = self.publisher.publish_note(note_id)
        
        assert isinstance(result, dict)
        assert result["status"] == "published"
        assert result["note_id"] == note_id
        assert "published_at" in result
        assert "url" in result
    
    def test_publish_note_not_found(self):
        """Test publishing non-existent note raises error."""
        with pytest.raises(ValueError) as exc_info:
            self.publisher.publish_note("non_existent_note")
        
        assert "not found" in str(exc_info.value)
    
    def test_get_draft_not_found(self):
        """Test getting non-existent draft returns None."""
        draft = self.publisher.get_draft("non_existent")
        assert draft is None
    
    def test_delete_draft_success(self):
        """Test deleting a draft successfully."""
        note_id = self.publisher.create_note(self.valid_content, self.valid_images)
        
        result = self.publisher.delete_draft(note_id)
        assert result is True
        
        # Verify draft was deleted
        draft = self.publisher.get_draft(note_id)
        assert draft is None
    
    def test_delete_draft_not_found(self):
        """Test deleting non-existent draft returns False."""
        result = self.publisher.delete_draft("non_existent")
        assert result is False
