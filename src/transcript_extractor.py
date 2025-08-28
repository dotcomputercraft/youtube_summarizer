"""
YouTube Transcript Extractor

This module handles extracting transcripts from YouTube videos using the youtube-transcript-api.
"""

import re
import logging
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


class TranscriptExtractor:
    """Handles extraction of transcripts from YouTube videos."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.formatter = TextFormatter()
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various YouTube URL formats.
        
        Args:
            url: YouTube URL in various formats
            
        Returns:
            Video ID if found, None otherwise
        """
        # Handle different YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If it's already just a video ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        return None
    
    def get_available_transcripts(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get list of available transcripts for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of available transcript information
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available = []
            
            for transcript in transcript_list:
                available.append({
                    'language': transcript.language,
                    'language_code': transcript.language_code,
                    'is_generated': transcript.is_generated,
                    'is_translatable': transcript.is_translatable
                })
            
            return available
            
        except Exception as e:
            self.logger.error(f"Error getting available transcripts: {e}")
            return []
    
    def extract_transcript(self, video_id: str, language_codes: Optional[List[str]] = None) -> Optional[str]:
        """
        Extract transcript from a YouTube video.
        
        Args:
            video_id: YouTube video ID
            language_codes: Preferred language codes (e.g., ['en', 'es'])
            
        Returns:
            Transcript text if successful, None otherwise
        """
        try:
            # Default to English if no language specified
            if language_codes is None:
                language_codes = ['en']
            
            self.logger.info(f"Attempting to extract transcript for video {video_id} in languages: {language_codes}")
            
            # Try to get transcript in preferred languages
            transcript_data = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=language_codes
            )
            
            # Format transcript as plain text
            transcript_text = self.formatter.format_transcript(transcript_data)
            
            self.logger.info(f"Successfully extracted transcript for video {video_id}")
            return transcript_text
            
        except Exception as e:
            self.logger.error(f"Error extracting transcript for video {video_id}: {e}")
            
            # Try to get any available transcript if preferred languages fail
            try:
                self.logger.info(f"Attempting fallback transcript extraction for video {video_id}")
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Get the first available transcript
                for transcript in transcript_list:
                    try:
                        self.logger.info(f"Trying transcript in {transcript.language} ({transcript.language_code})")
                        transcript_data = transcript.fetch()
                        transcript_text = self.formatter.format_transcript(transcript_data)
                        
                        self.logger.info(f"Successfully extracted transcript in {transcript.language} for video {video_id}")
                        return transcript_text
                    except Exception as transcript_error:
                        self.logger.warning(f"Failed to fetch transcript in {transcript.language}: {transcript_error}")
                        continue
                        
                # If we get here, no transcripts worked
                self.logger.error(f"No working transcripts found for video {video_id}")
                return None
                    
            except Exception as fallback_error:
                self.logger.error(f"Fallback transcript extraction failed for video {video_id}: {fallback_error}")
                
                # Check if it's a common error and provide helpful message
                error_str = str(fallback_error).lower()
                if "no element found" in error_str:
                    self.logger.error("This appears to be an XML parsing error. The video may not have transcripts available.")
                elif "transcript" in error_str and "disabled" in error_str:
                    self.logger.error("Transcripts are disabled for this video.")
                elif "video unavailable" in error_str:
                    self.logger.error("The video is unavailable or private.")
                elif "video does not exist" in error_str:
                    self.logger.error("The video does not exist or the video ID is invalid.")
                
            return None
    
    def get_transcript_with_timestamps(self, video_id: str, language_codes: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Extract transcript with timestamp information.
        
        Args:
            video_id: YouTube video ID
            language_codes: Preferred language codes
            
        Returns:
            List of transcript segments with timestamps, None if failed
        """
        try:
            if language_codes is None:
                language_codes = ['en']
            
            transcript_data = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=language_codes
            )
            
            return transcript_data
            
        except Exception as e:
            self.logger.error(f"Error extracting timestamped transcript: {e}")
            return None
    
    def clean_transcript(self, transcript: str) -> str:
        """
        Clean and format transcript text.
        
        Args:
            transcript: Raw transcript text
            
        Returns:
            Cleaned transcript text
        """
        if not transcript:
            return ""
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', transcript)
        
        # Remove common transcript artifacts
        cleaned = re.sub(r'\[.*?\]', '', cleaned)  # Remove [Music], [Applause], etc.
        cleaned = re.sub(r'\(.*?\)', '', cleaned)  # Remove (inaudible), etc.
        
        # Clean up punctuation
        cleaned = re.sub(r'\s+([,.!?])', r'\1', cleaned)
        
        return cleaned.strip()

