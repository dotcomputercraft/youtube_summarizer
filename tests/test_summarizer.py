"""
Tests for Summarizer module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from summarizer import Summarizer, SummaryStyle


class TestSummarizer:
    """Test cases for Summarizer class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Mock environment variables
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-api-key'}):
            self.summarizer = Summarizer()
    
    def test_init_with_api_key(self):
        """Test initializing summarizer with API key."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            summarizer = Summarizer()
            assert summarizer.api_key == 'test-key'
            assert summarizer.model == 'gpt-4o'
    
    def test_init_with_custom_parameters(self):
        """Test initializing summarizer with custom parameters."""
        summarizer = Summarizer(
            api_key='custom-key',
            api_base='https://custom-api.com/v1',
            model='gpt-4'
        )
        assert summarizer.api_key == 'custom-key'
        assert summarizer.api_base == 'https://custom-api.com/v1'
        assert summarizer.model == 'gpt-4'
    
    def test_init_without_api_key(self):
        """Test initializing summarizer without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                Summarizer()
    
    @patch('summarizer.OpenAI')
    def test_summarize_success(self, mock_openai_class):
        """Test successful summarization."""
        # Mock OpenAI client and response
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a test summary."
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            summarizer = Summarizer()
            
        transcript = "This is a long transcript that needs to be summarized."
        result = summarizer.summarize(transcript, SummaryStyle.BRIEF)
        
        assert result == "This is a test summary."
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('summarizer.OpenAI')
    def test_summarize_with_custom_prompt(self, mock_openai_class):
        """Test summarization with custom prompt."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Custom summary result."
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            summarizer = Summarizer()
        
        transcript = "Test transcript"
        custom_prompt = "Summarize this in a very specific way"
        result = summarizer.summarize(transcript, custom_prompt=custom_prompt)
        
        assert result == "Custom summary result."
        
        # Check that custom prompt was used
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        assert custom_prompt in messages[0]['content']
    
    @patch('summarizer.OpenAI')
    def test_summarize_with_max_length(self, mock_openai_class):
        """Test summarization with maximum length constraint."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Short summary."
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            summarizer = Summarizer()
        
        transcript = "Test transcript"
        result = summarizer.summarize(transcript, max_length=50)
        
        assert result == "Short summary."
        
        # Check that length constraint was added to prompt
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        assert "under 50 words" in messages[0]['content']
    
    @patch('summarizer.OpenAI')
    def test_summarize_api_error(self, mock_openai_class):
        """Test summarization with API error."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            summarizer = Summarizer()
        
        transcript = "Test transcript"
        result = summarizer.summarize(transcript)
        
        assert result is None
    
    @patch('summarizer.OpenAI')
    def test_summarize_with_questions_success(self, mock_openai_class):
        """Test summarization with questions extraction."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """SUMMARY:
This video explains Python programming basics.

KEY QUESTIONS ANSWERED:
- What is Python?
- How to write your first program?
- Why use Python for beginners?"""
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            summarizer = Summarizer()
        
        transcript = "Python tutorial transcript"
        result = summarizer.summarize_with_questions(transcript)
        
        assert result is not None
        assert 'summary' in result
        assert 'questions' in result
        assert "Python programming basics" in result['summary']
        assert "What is Python?" in result['questions']
    
    @patch('summarizer.OpenAI')
    def test_summarize_with_questions_parsing_error(self, mock_openai_class):
        """Test summarization with questions when parsing fails."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Malformed response without proper sections"
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            summarizer = Summarizer()
        
        transcript = "Test transcript"
        result = summarizer.summarize_with_questions(transcript)
        
        assert result is not None
        assert result['summary'] == "Malformed response without proper sections"
        assert result['questions'] == "Could not extract specific questions."
    
    @patch('summarizer.OpenAI')
    def test_extract_key_topics_success(self, mock_openai_class):
        """Test extracting key topics successfully."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """Python Programming
Machine Learning
Data Science
Web Development
Automation"""
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            summarizer = Summarizer()
        
        transcript = "Comprehensive Python tutorial transcript"
        result = summarizer.extract_key_topics(transcript, num_topics=5)
        
        assert result is not None
        assert len(result) == 5
        assert "Python Programming" in result
        assert "Machine Learning" in result
        assert "Data Science" in result
    
    @patch('summarizer.OpenAI')
    def test_extract_key_topics_with_limit(self, mock_openai_class):
        """Test extracting key topics with limit enforcement."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """Topic 1
Topic 2
Topic 3
Topic 4
Topic 5
Topic 6
Topic 7"""
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            summarizer = Summarizer()
        
        transcript = "Test transcript"
        result = summarizer.extract_key_topics(transcript, num_topics=3)
        
        assert result is not None
        assert len(result) == 3  # Should be limited to requested number
    
    @patch('summarizer.OpenAI')
    def test_extract_key_topics_error(self, mock_openai_class):
        """Test extracting key topics with API error."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            summarizer = Summarizer()
        
        transcript = "Test transcript"
        result = summarizer.extract_key_topics(transcript)
        
        assert result is None
    
    def test_get_model_info(self):
        """Test getting model information."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            summarizer = Summarizer(model='gpt-4', api_base='https://custom.api.com/v1')
        
        info = summarizer.get_model_info()
        
        assert info['model'] == 'gpt-4'
        assert info['api_base'] == 'https://custom.api.com/v1'
        assert info['api_key_set'] == True
    
    def test_summary_style_enum(self):
        """Test SummaryStyle enum values."""
        assert SummaryStyle.BRIEF.value == "brief"
        assert SummaryStyle.DETAILED.value == "detailed"
        assert SummaryStyle.BULLET_POINTS.value == "bullet_points"
        assert SummaryStyle.KEY_INSIGHTS.value == "key_insights"
        assert SummaryStyle.ACADEMIC.value == "academic"
        assert SummaryStyle.CASUAL.value == "casual"
    
    def test_style_prompts_exist(self):
        """Test that all style prompts are defined."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            summarizer = Summarizer()
        
        for style in SummaryStyle:
            assert style in summarizer.style_prompts
            assert len(summarizer.style_prompts[style].strip()) > 0


@pytest.fixture
def sample_transcript():
    """Sample transcript for testing."""
    return """
    Welcome to this comprehensive tutorial on Python programming.
    In this video, we will cover the basics of Python syntax,
    data types, control structures, and functions.
    Python is a versatile programming language that is widely used
    in web development, data science, and automation.
    By the end of this tutorial, you will have a solid understanding
    of Python fundamentals and be ready to start building your own projects.
    """


def test_summarizer_integration(sample_transcript):
    """Integration test for summarizer with sample data."""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        with patch('summarizer.OpenAI') as mock_openai_class:
            mock_client = Mock()
            mock_openai_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Python tutorial summary"
            mock_client.chat.completions.create.return_value = mock_response
            
            summarizer = Summarizer()
            
            # Test different summary styles
            for style in SummaryStyle:
                result = summarizer.summarize(sample_transcript, style)
                assert result == "Python tutorial summary"
            
            # Test model info
            info = summarizer.get_model_info()
            assert 'model' in info
            assert 'api_key_set' in info

