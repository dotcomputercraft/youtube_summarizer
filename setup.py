"""
Setup script for YouTube Video Summarizer
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

setup(
    name="youtube-summarizer",
    version="1.0.0",
    author="YouTube Summarizer Team",
    author_email="contact@example.com",
    description="Extract and summarize YouTube video transcripts using GPT-4o",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/youtube-summarizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "youtube-transcript-api>=0.6.2",
        "openai>=1.0.0",
        "click>=8.0.0",
        "python-dotenv>=1.0.0",
        "colorama>=0.4.6",
        "tqdm>=4.65.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ]
    },
    entry_points={
        "console_scripts": [
            "yt-summarizer=src.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

