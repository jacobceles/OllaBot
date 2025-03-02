import os
import pytest
from api.services.log_analysis_llm import summarize_errors

# Generate a list of test files dynamically from test log files
log_files = [os.path.join("tests/assets/error_logs", f"error_log_{i}.txt") for i in range(1, 6)]


@pytest.mark.parametrize("log_file", log_files)
def test_summarize_errors_output_type(log_file: str) -> None:
    """
    Test that summarize_errors() returns a string and is not empty for different log files.
    """
    # Ensure the file exists before running the test
    assert os.path.exists(log_file), f"Test log file not found: {log_file}"

    # Read the log file content
    with open(log_file, encoding="utf-8") as file:
        log_content = file.read()

    # Call the log analysis function
    summary = summarize_errors(log_content, is_local=True)  # Assuming local test

    # Assertions: Check if the function returns the expected type and is not empty
    assert isinstance(summary, str), "summarize_errors() should return a string"
    assert summary.strip() != "", "Summary output should not be empty"
