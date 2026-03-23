"""Tests for ContentGenerator"""

import pytest
from scripts.generator import ContentGenerator


class TestContentGenerator:
    """Test cases for ContentGenerator"""
    
    @pytest.fixture
    def generator(self):
        return ContentGenerator()
    
    def test_generate_title_returns_list(self, generator):
        """Test generate_title returns a list"""
        result = generator.generate_title("护肤精华")
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_generate_title_contains_topic(self, generator):
        """Test generated titles contain the topic"""
        topic = "护肤精华"
        result = generator.generate_title(topic)
        for title in result:
            assert topic in title
    
    def test_generate_title_different_styles(self, generator):
        """Test different title styles"""
        styles = ["viral", "question", "list", "story", "benefit"]
        topic = "测试主题"
        
        for style in styles:
            result = generator.generate_title(topic, style=style)
            assert isinstance(result, list)
            assert len(result) > 0
    
    def test_generate_title_invalid_style_fallback(self, generator):
        """Test fallback to viral style for invalid style"""
        result = generator.generate_title("测试", style="invalid")
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_generate_body_returns_string(self, generator):
        """Test generate_body returns a string"""
        result = generator.generate_body("护肤精华", format="product")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_generate_body_contains_topic(self, generator):
        """Test generated body contains the topic"""
        topic = "护肤精华"
        result = generator.generate_body(topic, format="product")
        assert topic in result
    
    def test_generate_body_different_formats(self, generator):
        """Test different body formats"""
        formats = ["product", "activity", "story"]
        topic = "测试主题"
        
        for format_type in formats:
            result = generator.generate_body(topic, format=format_type)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_generate_script_returns_dict(self, generator):
        """Test generate_script returns a dictionary"""
        result = generator.generate_script("护肤精华", duration=60)
        assert isinstance(result, dict)
    
    def test_generate_script_structure(self, generator):
        """Test script has correct structure"""
        result = generator.generate_script("护肤精华", duration=60)
        
        assert "metadata" in result
        assert "scenes" in result
        assert "hooks" in result
        assert "call_to_action" in result
        assert "hashtags" in result
        
        assert isinstance(result["scenes"], list)
        assert len(result["scenes"]) > 0
        
        assert isinstance(result["hooks"], list)
        assert len(result["hooks"]) > 0
    
    def test_generate_script_scene_structure(self, generator):
        """Test each scene has required fields"""
        result = generator.generate_script("护肤精华", duration=60)
        
        for scene in result["scenes"]:
            assert "scene_number" in scene
            assert "timestamp" in scene
            assert "duration" in scene
            assert "type" in scene
            assert "visual" in scene
            assert "narration" in scene
    
    def test_generate_script_duration(self, generator):
        """Test script respects duration parameter"""
        duration = 60
        result = generator.generate_script("护肤精华", duration=duration)
        assert result["metadata"]["duration"] == duration
