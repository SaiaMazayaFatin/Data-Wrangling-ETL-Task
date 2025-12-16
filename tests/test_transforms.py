import pandas as pd
import pytest
from src.utils import parse_timestamp, standardize_uid

# Test Fungsi Timestamp
def test_parse_timestamp_unix():
    assert parse_timestamp("1760923200") == "2025-10-20T12:00:00Z"

def test_parse_timestamp_european():
    # Asumsi UTC untuk kesederhanaan tes
    res = parse_timestamp("20/10/2025 10:00:00")
    assert "2025-10-20" in res

def test_parse_timestamp_invalid():
    assert parse_timestamp("invalid_date") is None

# Test Fungsi User ID
def test_standardize_uid_integer():
    assert standardize_uid(12345) == "U-12345"

def test_standardize_uid_string():
    assert standardize_uid("U-54321") == "U-54321"