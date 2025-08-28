"""
Tests for TranscriptExtractor module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from transcript_extractor import TranscriptExtractor


class TestTranscriptExtractor:
    """Test cases for TranscriptExtractor class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.extractor = TranscriptExtractor()
    
    def test_extract_video_id_youtube_watch_url(self):
        """Test extracting video ID from standard YouTube watch URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = self.extractor.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_youtu_be_url(self):
        """Test extracting video ID from youtu.be short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = self.extractor.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_embed_url(self):
        """Test extracting video ID from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        result = self.extractor.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_with_parameters(self):
        """Test extracting video ID from URL with additional parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s&list=PLrAXtmRdnEQy6nuLMHjMZOz59FYxp5VES"
        result = self.extractor.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_plain_id(self):
        """Test extracting video ID when input is already a video ID."""
        video_id = "dQw4w9WgXcQ"
        result = self.extractor.extract_video_id(video_id)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_invalid_url(self):
        """Test extracting video ID from invalid URL."""
        url = "https://www.example.com/not-a-youtube-url"
        result = self.extractor.extract_video_id(url)
        assert result is None
    
    def test_extract_video_id_invalid_id(self):
        """Test extracting video ID from invalid ID format."""
        invalid_id = "invalid-id-format"
        result = self.extractor.extract_video_id(invalid_id)
        assert result is None
    
    @patch('transcript_extractor.YouTubeTranscriptApi.list_transcripts')
    def test_get_available_transcripts_success(self, mock_list_transcripts):
        """Test getting available transcripts successfully."""
        # Mock transcript objects
        mock_transcript1 = Mock()
        mock_transcript1.language = "English"
        mock_transcript1.language_code = "en"
        mock_transcript1.is_generated = False
        mock_transcript1.is_translatable = True
        
        mock_transcript2 = Mock()
        mock_transcript2.language = "Spanish"
        mock_transcript2.language_code = "es"
        mock_transcript2.is_generated = True
        mock_transcript2.is_translatable = False
        
        mock_list_transcripts.return_value = [mock_transcript1, mock_transcript2]
        
        result = self.extractor.get_available_transcripts("test_video_id")
        
        assert len(result) == 2
        assert result[0]['language'] == "English"
        assert result[0]['language_code'] == "en"
        assert result[0]['is_generated'] == False
        assert result[0]['is_translatable'] == True
        
        assert result[1]['language'] == "Spanish"
        assert result[1]['language_code'] == "es"
        assert result[1]['is_generated'] == True
        assert result[1]['is_translatable'] == False
    
    @patch('transcript_extractor.YouTubeTranscriptApi.list_transcripts')
    def test_get_available_transcripts_error(self, mock_list_transcripts):
        """Test getting available transcripts with error."""
        mock_list_transcripts.side_effect = Exception("API Error")
        
        result = self.extractor.get_available_transcripts("test_video_id")
        
        assert result == []
    
    @patch('transcript_extractor.YouTubeTranscriptApi.get_transcript')
    def test_extract_transcript_success(self, mock_get_transcript):
        """Test extracting transcript successfully."""
        mock_transcript_data = [
            {'text': 'Hello world', 'start': 0.0, 'duration': 2.0},
            {'text': 'This is a test', 'start': 2.0, 'duration': 3.0}
        ]
        mock_get_transcript.return_value = mock_transcript_data
        
        result = self.extractor.extract_transcript("test_video_id")
        
        assert result is not None
        assert "Hello world" in result
        assert "This is a test" in result
        mock_get_transcript.assert_called_once_with("test_video_id", languages=['en'])
    
    @patch('transcript_extractor.YouTubeTranscriptApi.get_transcript')
    def test_extract_transcript_with_custom_languages(self, mock_get_transcript):
        """Test extracting transcript with custom language preferences."""
        mock_transcript_data = [
            {'text': 'Hola mundo', 'start': 0.0, 'duration': 2.0}
        ]
        mock_get_transcript.return_value = mock_transcript_data
        
        result = self.extractor.extract_transcript("test_video_id", ['es', 'en'])
        
        assert result is not None
        assert "Hola mundo" in result
        mock_get_transcript.assert_called_once_with("test_video_id", languages=['es', 'en'])
    
    @patch('transcript_extractor.YouTubeTranscriptApi.list_transcripts')
    @patch('transcript_extractor.YouTubeTranscriptApi.get_transcript')
    def test_extract_transcript_fallback(self, mock_get_transcript, mock_list_transcripts):
        """Test transcript extraction with fallback to any available language."""
        # First call fails
        mock_get_transcript.side_effect = Exception("Language not available")
        
        # Mock available transcripts for fallback
        mock_transcript = Mock()
        mock_transcript_data = [
            {'text': 'Fallback text', 'start': 0.0, 'duration': 2.0}
        ]
        mock_transcript.fetch.return_value = mock_transcript_data
        mock_transcript.language = "French"
        
        mock_list_transcripts.return_value = [mock_transcript]
        
        result = self.extractor.extract_transcript("test_video_id")
        
        assert result is not None
        assert "Fallback text" in result
    
    @patch('transcript_extractor.YouTubeTranscriptApi.get_transcript')
    def test_get_transcript_with_timestamps(self, mock_get_transcript):
        """Test getting transcript with timestamps."""
        mock_transcript_data = [
            {'text': 'Hello world', 'start': 0.0, 'duration': 2.0},
            {'text': 'This is a test', 'start': 2.0, 'duration': 3.0}
        ]
        mock_get_transcript.return_value = mock_transcript_data
        
        result = self.extractor.get_transcript_with_timestamps("test_video_id")
        
        assert result == mock_transcript_data
        assert len(result) == 2
        assert result[0]['text'] == 'Hello world'
        assert result[0]['start'] == 0.0
        assert result[0]['duration'] == 2.0
    
    def test_clean_transcript(self):
        """Test transcript cleaning functionality."""
        dirty_transcript = """
        This is a test   transcript with [Music] and (inaudible) parts.
        It has    excessive    whitespace and [Applause] markers.
        Also some punctuation issues , like this !
        """
        
        result = self.extractor.clean_transcript(dirty_transcript)
        
        assert "[Music]" not in result
        assert "(inaudible)" not in result
        assert "[Applause]" not in result
        assert "excessive    whitespace" not in result
        assert " ," not in result
        assert " !" not in result
        assert result.startswith("This is a test transcript")
    
    def test_clean_transcript_empty(self):
        """Test cleaning empty transcript."""
        result = self.extractor.clean_transcript("")
        assert result == ""
    
    def test_clean_transcript_none(self):
        """Test cleaning None transcript."""
        result = self.extractor.clean_transcript(None)
        assert result == ""


@pytest.fixture
def sample_transcript_data():
    """Sample transcript data for testing."""
    return [
        {'text': 'Welcome to this video', 'start': 0.0, 'duration': 2.5},
        {'text': 'Today we will learn about Python', 'start': 2.5, 'duration': 3.0},
        {'text': 'Python is a great programming language', 'start': 5.5, 'duration': 3.5},
        {'text': 'Thank you for watching', 'start': 9.0, 'duration': 2.0}
    ]


def test_transcript_extractor_integration(sample_transcript_data):
    """Integration test for transcript extractor with sample data."""
    extractor = TranscriptExtractor()
    
    # Test video ID extraction
    video_id = extractor.extract_video_id("https://youtube.com/watch?v=test123")
    assert video_id == "test123"
    
    # Test transcript cleaning
    dirty_text = "This is [Music] a test (inaudible) transcript"
    clean_text = extractor.clean_transcript(dirty_text)
    assert "[Music]" not in clean_text
    assert "(inaudible)" not in clean_text

