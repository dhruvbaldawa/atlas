"""Tests for database model classes and utilities."""

from backend.db.models import generate_ulid


def test_generate_ulid():
    """Test ULID generation.

    Given: No specific input
    When: Generating a ULID
    Then: The result should be a string of correct length (26 chars)
    """
    # When
    result = generate_ulid()

    # Then
    assert isinstance(result, str)
    assert len(result) == 26  # ULIDs are 26 characters long


def test_generate_ulid_uniqueness():
    """Test ULID uniqueness.

    Given: Multiple calls to generate_ulid
    When: Generating multiple ULIDs
    Then: Each ULID should be unique
    """
    # When
    ulids = [generate_ulid() for _ in range(100)]

    # Then
    assert len(set(ulids)) == 100  # All should be unique
