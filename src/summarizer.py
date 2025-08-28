"""
GPT-4o Summarizer

This module handles summarizing transcripts using OpenAI's GPT-4o API.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from openai import OpenAI
from enum import Enum


class SummaryStyle(Enum):
    """Different summary styles available."""
    BRIEF = "brief"
    DETAILED = "detailed"
    BULLET_POINTS = "bullet_points"
    KEY_INSIGHTS = "key_insights"
    ACADEMIC = "academic"
    CASUAL = "casual"


class Summarizer:
    """Handles summarization of transcripts using GPT-4o."""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize the summarizer.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            api_base: OpenAI API base URL (defaults to environment variable)
            model: Model to use for summarization
        """
        self.logger = logging.getLogger(__name__)
        
        # Use provided values or fall back to environment variables
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.api_base = api_base or os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )
        
        # Summary style templates
        self.style_prompts = {
            SummaryStyle.BRIEF: """
                Provide a brief, concise summary of this video transcript in 2-3 sentences.
                Focus on the main topic and key takeaway.
            """,
            SummaryStyle.DETAILED: """
                Provide a comprehensive summary of this video transcript.
                Include the main topics, key points, important details, and conclusions.
                Organize the summary in clear paragraphs.
            """,
            SummaryStyle.BULLET_POINTS: """
                Summarize this video transcript using bullet points.
                - Start with the main topic
                - List key points and important information
                - Include any conclusions or takeaways
                Use clear, concise bullet points.
            """,
            SummaryStyle.KEY_INSIGHTS: """
                Extract and summarize the key insights from this video transcript.
                Focus on:
                - Main insights and learnings
                - Important facts or data mentioned
                - Actionable advice or recommendations
                - Notable quotes or statements
            """,
            SummaryStyle.ACADEMIC: """
                Provide an academic-style summary of this video transcript.
                Structure it with:
                - Abstract/Overview
                - Main arguments or points
                - Supporting evidence or examples
                - Conclusions
                Use formal, scholarly language.
            """,
            SummaryStyle.CASUAL: """
                Summarize this video transcript in a casual, conversational tone.
                Make it easy to read and understand, as if explaining to a friend.
                Include the main points and interesting details in a relaxed style.
            """
        }
    
    def summarize(
        self, 
        transcript: str, 
        style: SummaryStyle = SummaryStyle.DETAILED,
        max_length: Optional[int] = None,
        custom_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Summarize a transcript using GPT-4o.
        
        Args:
            transcript: The transcript text to summarize
            style: Summary style to use
            max_length: Maximum length constraint for summary
            custom_prompt: Custom prompt to override style template
            
        Returns:
            Summary text if successful, None otherwise
        """
        try:
            # Prepare the prompt
            if custom_prompt:
                system_prompt = custom_prompt
            else:
                system_prompt = self.style_prompts[style].strip()
            
            # Add length constraint if specified
            if max_length:
                system_prompt += f"\n\nKeep the summary under {max_length} words."
            
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Please summarize this video transcript:\n\n{transcript}"
                }
            ]
            
            self.logger.info(f"Sending summarization request to {self.model}")
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            summary = response.choices[0].message.content.strip()
            
            self.logger.info("Successfully generated summary")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return None
    
    def summarize_with_questions(self, transcript: str) -> Optional[Dict[str, str]]:
        """
        Generate a summary along with key questions answered in the video.
        
        Args:
            transcript: The transcript text to analyze
            
        Returns:
            Dictionary with 'summary' and 'questions' keys, None if failed
        """
        try:
            system_prompt = """
                Analyze this video transcript and provide:
                1. A comprehensive summary of the main content
                2. A list of key questions that this video answers
                
                Format your response as:
                SUMMARY:
                [Your summary here]
                
                KEY QUESTIONS ANSWERED:
                - [Question 1]
                - [Question 2]
                - [etc.]
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Transcript:\n\n{transcript}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the response
            parts = content.split("KEY QUESTIONS ANSWERED:")
            if len(parts) == 2:
                summary = parts[0].replace("SUMMARY:", "").strip()
                questions = parts[1].strip()
                
                return {
                    "summary": summary,
                    "questions": questions
                }
            else:
                # Fallback if parsing fails
                return {
                    "summary": content,
                    "questions": "Could not extract specific questions."
                }
                
        except Exception as e:
            self.logger.error(f"Error generating summary with questions: {e}")
            return None
    
    def extract_key_topics(self, transcript: str, num_topics: int = 5) -> Optional[List[str]]:
        """
        Extract key topics from the transcript.
        
        Args:
            transcript: The transcript text to analyze
            num_topics: Number of key topics to extract
            
        Returns:
            List of key topics, None if failed
        """
        try:
            system_prompt = f"""
                Extract the {num_topics} most important topics discussed in this video transcript.
                Return only the topics, one per line, without numbers or bullets.
                Focus on the main themes and subjects covered.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Transcript:\n\n{transcript}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            topics = [topic.strip() for topic in content.split('\n') if topic.strip()]
            
            return topics[:num_topics]  # Ensure we don't exceed requested number
            
        except Exception as e:
            self.logger.error(f"Error extracting key topics: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model configuration."""
        return {
            "model": self.model,
            "api_base": self.api_base,
            "api_key_set": bool(self.api_key)
        }

