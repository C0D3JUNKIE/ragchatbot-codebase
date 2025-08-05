import pytest
from unittest.mock import Mock, MagicMock
from typing import List, Dict, Any
import tempfile
import os

# Import the models and classes we'll be testing
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Course, Lesson, CourseChunk
from vector_store import SearchResults
from config import Config


@pytest.fixture
def sample_course():
    """Create a sample course for testing"""
    lessons = [
        Lesson(lesson_number=1, title="Introduction", lesson_link="https://example.com/lesson1"),
        Lesson(lesson_number=2, title="Advanced Topics", lesson_link="https://example.com/lesson2"),
        Lesson(lesson_number=3, title="Conclusion", lesson_link="https://example.com/lesson3")
    ]
    
    return Course(
        title="Building Towards Computer Use with Anthropic",
        course_link="https://example.com/course",
        instructor="Colt Steele",
        lessons=lessons
    )


@pytest.fixture
def sample_course_chunks():
    """Create sample course chunks for testing"""
    return [
        CourseChunk(
            content="Welcome to Building Toward Computer Use with Anthropic. This course covers computer automation.",
            course_title="Building Towards Computer Use with Anthropic",
            lesson_number=1,
            chunk_index=0
        ),
        CourseChunk(
            content="In this lesson, we'll explore advanced topics including tool calling and agent workflows.",
            course_title="Building Towards Computer Use with Anthropic", 
            lesson_number=2,
            chunk_index=1
        ),
        CourseChunk(
            content="Computer use capability is built by using many features of large language models.",
            course_title="Building Towards Computer Use with Anthropic",
            lesson_number=1,
            chunk_index=2
        )
    ]


@pytest.fixture
def sample_search_results():
    """Create sample search results for testing"""
    return SearchResults(
        documents=[
            "Welcome to Building Toward Computer Use with Anthropic. This course covers computer automation.",
            "In this lesson, we'll explore advanced topics including tool calling and agent workflows."
        ],
        metadata=[
            {"course_title": "Building Towards Computer Use with Anthropic", "lesson_number": 1, "chunk_index": 0},
            {"course_title": "Building Towards Computer Use with Anthropic", "lesson_number": 2, "chunk_index": 1}
        ],
        distances=[0.1, 0.2]
    )


@pytest.fixture
def empty_search_results():
    """Create empty search results for testing"""
    return SearchResults(
        documents=[],
        metadata=[],
        distances=[]
    )


@pytest.fixture
def error_search_results():
    """Create error search results for testing"""
    return SearchResults.empty("Search error: Database connection failed")


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store for testing"""
    mock = Mock()
    mock.search.return_value = SearchResults(
        documents=["Sample document content"],
        metadata=[{"course_title": "Test Course", "lesson_number": 1}],
        distances=[0.1]
    )
    mock._resolve_course_name.return_value = "Test Course"
    mock.get_lesson_link.return_value = "https://example.com/lesson1"
    return mock


@pytest.fixture
def mock_anthropic_client():
    """Create a mock Anthropic client for testing"""
    mock_client = Mock()
    
    # Mock response for direct text response
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = "This is a test response from Claude."
    mock_response.stop_reason = "end_turn"
    
    # Mock response for tool use
    mock_tool_response = Mock()
    mock_tool_response.stop_reason = "tool_use"
    mock_tool_content = Mock()
    mock_tool_content.type = "tool_use"
    mock_tool_content.name = "search_course_content"
    mock_tool_content.id = "tool_123"
    mock_tool_content.input = {"query": "test query"}
    mock_tool_response.content = [mock_tool_content]
    
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_tool_manager():
    """Create a mock tool manager for testing"""
    mock = Mock()
    mock.get_tool_definitions.return_value = [
        {
            "name": "search_course_content",
            "description": "Search course materials",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for"}
                },
                "required": ["query"]
            }
        }
    ]
    mock.execute_tool.return_value = "Mock search result"
    mock.get_last_sources.return_value = ["Test Course - Lesson 1"]
    mock.get_last_source_links.return_value = ["https://example.com/lesson1"]
    return mock


@pytest.fixture
def test_config():
    """Create a test configuration with proper settings"""
    return Config(
        ANTHROPIC_API_KEY="test-api-key",
        ANTHROPIC_MODEL="claude-sonnet-4-20250514",
        EMBEDDING_MODEL="all-MiniLM-L6-v2",
        CHUNK_SIZE=800,
        CHUNK_OVERLAP=100,
        MAX_RESULTS=5,  # Set to proper value, not 0
        MAX_HISTORY=2,
        CHROMA_PATH="./test_chroma_db"
    )


@pytest.fixture
def broken_config():
    """Create a configuration with the broken MAX_RESULTS=0 setting"""
    return Config(
        ANTHROPIC_API_KEY="test-api-key",
        ANTHROPIC_MODEL="claude-sonnet-4-20250514",
        EMBEDDING_MODEL="all-MiniLM-L6-v2",
        CHUNK_SIZE=800,
        CHUNK_OVERLAP=100,
        MAX_RESULTS=0,  # This is the broken setting
        MAX_HISTORY=2,
        CHROMA_PATH="./test_chroma_db"
    )


@pytest.fixture
def temp_chroma_db():
    """Create a temporary ChromaDB directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_chroma_collection():
    """Create a mock ChromaDB collection for testing"""
    mock = Mock()
    mock.query.return_value = {
        'documents': [["Sample document"]],
        'metadatas': [[{"course_title": "Test Course", "lesson_number": 1}]],
        'distances': [[0.1]]
    }
    mock.get.return_value = {
        'ids': ["test_course_1"],
        'metadatas': [{
            "title": "Test Course",
            "instructor": "Test Instructor",
            "course_link": "https://example.com/course",
            "lessons_json": '[{"lesson_number": 1, "lesson_title": "Test Lesson", "lesson_link": "https://example.com/lesson1"}]',
            "lesson_count": 1
        }]
    }
    return mock


# Test data constants
SAMPLE_COURSE_TEXT = """Course Title: Building Towards Computer Use with Anthropic
Course Link: https://www.deeplearning.ai/short-courses/building-toward-computer-use-with-anthropic/
Course Instructor: Colt Steele

Lesson 1: Introduction
Lesson Link: https://learn.deeplearning.ai/courses/building-toward-computer-use-with-anthropic/lesson/1/introduction
Welcome to Building Toward Computer Use with Anthropic. This course covers computer automation.

Lesson 2: Advanced Topics  
Lesson Link: https://learn.deeplearning.ai/courses/building-toward-computer-use-with-anthropic/lesson/2/advanced
In this lesson, we'll explore advanced topics including tool calling and agent workflows.
"""

SAMPLE_QUERY_RESPONSES = {
    "general": "This is a general knowledge response.",
    "course_specific": "Based on the search results, here is information about the course content.",
    "tool_use": "I'll search for that information in the course materials."
}