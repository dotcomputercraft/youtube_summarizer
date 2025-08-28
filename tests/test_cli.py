"""
Tests for CLI module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
import os
import sys
import json
import tempfile

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cli import cli, Config, print_success, print_error, print_warning, print_info


class TestCLI:
    """Test cases for CLI functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "YouTube Video Summarizer" in result.output
        assert "Extract and summarize YouTube video transcripts" in result.output
    
    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "1.0.0" in result.output
    
    @patch('cli.TranscriptExtractor')
    @patch('cli.Summarizer')
    def test_summarize_command_success(self, mock_summarizer_class, mock_extractor_class):
        """Test successful summarize command."""
        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_video_id.return_value = "test123"
        mock_extractor.extract_transcript.return_value = "Test transcript content"
        mock_extractor_class.return_value = mock_extractor
        
        # Mock summarizer
        mock_summarizer = Mock()
        mock_summarizer.summarize.return_value = "Test summary content"
        mock_summarizer_class.return_value = mock_summarizer
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            result = self.runner.invoke(cli, [
                'summarize', 
                'https://youtube.com/watch?v=test123',
                '--style', 'brief'
            ])
        
        assert result.exit_code == 0
        assert "Test summary content" in result.output
        mock_extractor.extract_video_id.assert_called_once()
        mock_extractor.extract_transcript.assert_called_once()
        mock_summarizer.summarize.assert_called_once()
    
    @patch('cli.TranscriptExtractor')
    @patch('cli.Summarizer')
    def test_summarize_command_with_output_file(self, mock_summarizer_class, mock_extractor_class):
        """Test summarize command with output file."""
        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_video_id.return_value = "test123"
        mock_extractor.extract_transcript.return_value = "Test transcript"
        mock_extractor_class.return_value = mock_extractor
        
        # Mock summarizer
        mock_summarizer = Mock()
        mock_summarizer.summarize.return_value = "Test summary"
        mock_summarizer_class.return_value = mock_summarizer
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            output_file = tmp_file.name
        
        try:
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                result = self.runner.invoke(cli, [
                    'summarize', 
                    'test123',
                    '--output', output_file
                ])
            
            assert result.exit_code == 0
            
            # Check that file was created and contains summary
            with open(output_file, 'r') as f:
                content = f.read()
                assert "Test summary" in content
        
        finally:
            os.unlink(output_file)
    
    @patch('cli.TranscriptExtractor')
    @patch('cli.Summarizer')
    def test_summarize_command_json_format(self, mock_summarizer_class, mock_extractor_class):
        """Test summarize command with JSON output format."""
        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_video_id.return_value = "test123"
        mock_extractor.extract_transcript.return_value = "Test transcript content"
        mock_extractor_class.return_value = mock_extractor
        
        # Mock summarizer
        mock_summarizer = Mock()
        mock_summarizer.summarize.return_value = "Test summary content"
        mock_summarizer_class.return_value = mock_summarizer
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            result = self.runner.invoke(cli, [
                'summarize', 
                'test123',
                '--format', 'json'
            ])
        
        assert result.exit_code == 0
        
        # Extract JSON from output using regex to handle progress bars and ANSI codes
        import re
        json_match = re.search(r'\{[\s\S]*\}', result.output)
        assert json_match, f"No JSON found in output: {result.output}"
        
        json_output = json_match.group(0)
        output_data = json.loads(json_output)
        
        assert output_data['video_id'] == 'test123'
        assert output_data['summary'] == 'Test summary content'
        assert 'transcript_length' in output_data
        assert 'summary_length' in output_data
    
    @patch('cli.TranscriptExtractor')
    def test_summarize_command_invalid_video_id(self, mock_extractor_class):
        """Test summarize command with invalid video ID."""
        mock_extractor = Mock()
        mock_extractor.extract_video_id.return_value = None
        mock_extractor_class.return_value = mock_extractor
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            result = self.runner.invoke(cli, [
                'summarize', 
                'invalid-url'
            ])
        
        assert result.exit_code == 1
        assert "Could not extract video ID" in result.output
    
    @patch('cli.TranscriptExtractor')
    def test_extract_command_success(self, mock_extractor_class):
        """Test successful extract command."""
        mock_extractor = Mock()
        mock_extractor.extract_video_id.return_value = "test123"
        mock_extractor.extract_transcript.return_value = "Test transcript content"
        mock_extractor_class.return_value = mock_extractor
        
        result = self.runner.invoke(cli, [
            'extract', 
            'https://youtube.com/watch?v=test123'
        ])
        
        assert result.exit_code == 0
        assert "Test transcript content" in result.output
        mock_extractor.extract_video_id.assert_called_once()
        mock_extractor.extract_transcript.assert_called_once()
    
    @patch('cli.TranscriptExtractor')
    def test_extract_command_with_timestamps(self, mock_extractor_class):
        """Test extract command with timestamps."""
        mock_extractor = Mock()
        mock_extractor.extract_video_id.return_value = "test123"
        mock_extractor.get_transcript_with_timestamps.return_value = [
            {'text': 'Hello world', 'start': 0.0, 'duration': 2.0},
            {'text': 'This is a test', 'start': 2.0, 'duration': 3.0}
        ]
        mock_extractor_class.return_value = mock_extractor
        
        result = self.runner.invoke(cli, [
            'extract', 
            'test123',
            '--timestamps'
        ])
        
        assert result.exit_code == 0
        assert "[0.00s] Hello world" in result.output
        assert "[2.00s] This is a test" in result.output
        mock_extractor.get_transcript_with_timestamps.assert_called_once()
    
    @patch('cli.TranscriptExtractor')
    def test_extract_command_srt_format(self, mock_extractor_class):
        """Test extract command with SRT format."""
        mock_extractor = Mock()
        mock_extractor.extract_video_id.return_value = "test123"
        mock_extractor.get_transcript_with_timestamps.return_value = [
            {'text': 'Hello world', 'start': 0.0, 'duration': 2.0}
        ]
        mock_extractor_class.return_value = mock_extractor
        
        result = self.runner.invoke(cli, [
            'extract', 
            'test123',
            '--format', 'srt'
        ])
        
        assert result.exit_code == 0
        assert "1" in result.output
        assert "00:00:00,000 --> 00:00:02,000" in result.output
        assert "Hello world" in result.output
    
    @patch('cli.TranscriptExtractor')
    def test_info_command_success(self, mock_extractor_class):
        """Test successful info command."""
        mock_extractor = Mock()
        mock_extractor.extract_video_id.return_value = "test123"
        mock_extractor.get_available_transcripts.return_value = [
            {
                'language': 'English',
                'language_code': 'en',
                'is_generated': False,
                'is_translatable': True
            },
            {
                'language': 'Spanish',
                'language_code': 'es',
                'is_generated': True,
                'is_translatable': False
            }
        ]
        mock_extractor_class.return_value = mock_extractor
        
        result = self.runner.invoke(cli, [
            'info', 
            'test123'
        ])
        
        assert result.exit_code == 0
        assert "Found 2 available transcript(s)" in result.output
        assert "English (en)" in result.output
        assert "Spanish (es)" in result.output
        assert "Manual" in result.output
        assert "Auto-generated" in result.output
    
    @patch('cli.TranscriptExtractor')
    def test_info_command_no_transcripts(self, mock_extractor_class):
        """Test info command with no available transcripts."""
        mock_extractor = Mock()
        mock_extractor.extract_video_id.return_value = "test123"
        mock_extractor.get_available_transcripts.return_value = []
        mock_extractor_class.return_value = mock_extractor
        
        result = self.runner.invoke(cli, [
            'info', 
            'test123'
        ])
        
        assert result.exit_code == 0
        assert "No transcripts available" in result.output
    
    @patch('cli.TranscriptExtractor')
    @patch('cli.Summarizer')
    def test_batch_command_success(self, mock_summarizer_class, mock_extractor_class):
        """Test successful batch command."""
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            tmp_file.write("https://youtube.com/watch?v=test1\n")
            tmp_file.write("https://youtube.com/watch?v=test2\n")
            input_file = tmp_file.name
        
        try:
            # Mock extractor
            mock_extractor = Mock()
            mock_extractor.extract_video_id.side_effect = ["test1", "test2"]
            mock_extractor.extract_transcript.side_effect = ["Transcript 1", "Transcript 2"]
            mock_extractor_class.return_value = mock_extractor
            
            # Mock summarizer
            mock_summarizer = Mock()
            mock_summarizer.summarize.side_effect = ["Summary 1", "Summary 2"]
            mock_summarizer_class.return_value = mock_summarizer
            
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                result = self.runner.invoke(cli, [
                    'batch', 
                    input_file,
                    '--style', 'brief'
                ])
            
            assert result.exit_code == 0
            assert "Successfully processed 2 videos" in result.output
            assert mock_extractor.extract_video_id.call_count == 2
            assert mock_extractor.extract_transcript.call_count == 2
            assert mock_summarizer.summarize.call_count == 2
        
        finally:
            os.unlink(input_file)
    
    def test_config_info_command(self):
        """Test config-info command."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            result = self.runner.invoke(cli, ['config-info'])
        
        assert result.exit_code == 0
        assert "Current Configuration" in result.output
        assert "Model: gpt-4o" in result.output
        assert "API Key: Set" in result.output
    
    def test_config_info_command_no_api_key(self):
        """Test config-info command without API key."""
        with patch.dict(os.environ, {}, clear=True):
            result = self.runner.invoke(cli, ['config-info'])
        
        assert result.exit_code == 0
        assert "API Key: Not set" in result.output
        assert "Set OPENAI_API_KEY environment variable" in result.output


class TestConfig:
    """Test cases for Config class."""
    
    def test_config_init(self):
        """Test Config initialization."""
        config = Config()
        assert config.verbose == False
        assert config.quiet == False
        assert config.output_format == 'text'
        assert config.model == 'gpt-4o'
    
    def test_config_setup_logging_verbose(self):
        """Test logging setup in verbose mode."""
        config = Config()
        config.verbose = True
        
        with patch('cli.logging.basicConfig') as mock_basic_config:
            config.setup_logging()
            mock_basic_config.assert_called_once()
            args, kwargs = mock_basic_config.call_args
            assert kwargs['level'] == 10  # DEBUG level
    
    def test_config_setup_logging_quiet(self):
        """Test logging setup in quiet mode."""
        config = Config()
        config.quiet = True
        
        with patch('cli.logging.basicConfig') as mock_basic_config:
            config.setup_logging()
            mock_basic_config.assert_called_once()
            args, kwargs = mock_basic_config.call_args
            assert kwargs['level'] == 40  # ERROR level


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_print_functions(self):
        """Test print utility functions."""
        runner = CliRunner()
        
        # These functions use click.echo, so we test they don't raise exceptions
        print_success("Test success message")
        print_error("Test error message")
        print_warning("Test warning message")
        print_info("Test info message")
    
    def test_save_output_to_file(self):
        """Test saving output to file."""
        from cli import save_output
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            output_file = tmp_file.name
        
        try:
            content = "Test content"
            save_output(content, output_file, 'text')
            
            with open(output_file, 'r') as f:
                saved_content = f.read()
                assert saved_content == content
        
        finally:
            os.unlink(output_file)
    
    def test_save_output_json_format(self):
        """Test saving output in JSON format."""
        from cli import save_output
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
            output_file = tmp_file.name
        
        try:
            content = {"test": "data", "number": 42}
            save_output(json.dumps(content), output_file, 'json')
            
            with open(output_file, 'r') as f:
                saved_data = json.load(f)
                assert saved_data == content
        
        finally:
            os.unlink(output_file)


@pytest.fixture
def sample_urls_file():
    """Create a temporary file with sample YouTube URLs."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
        tmp_file.write("https://youtube.com/watch?v=test1\n")
        tmp_file.write("https://youtube.com/watch?v=test2\n")
        tmp_file.write("test3\n")  # Just video ID
        yield tmp_file.name
    os.unlink(tmp_file.name)


def test_cli_integration(sample_urls_file):
    """Integration test for CLI with sample data."""
    runner = CliRunner()
    
    # Test help command
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert "YouTube Video Summarizer" in result.output
    
    # Test individual command help
    result = runner.invoke(cli, ['summarize', '--help'])
    assert result.exit_code == 0
    assert "Summarize a YouTube video" in result.output

