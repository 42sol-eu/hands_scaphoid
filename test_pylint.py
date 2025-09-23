#!/usr/bin/env python3
"""Test file for pylint configuration."""

import logging

logger = logging.getLogger(__name__)

def test_function():
    """Test function with f-string logging that would trigger W1203."""
    name = "test"
    value = 42
    
    # This would normally trigger W1203 warning
    logger.info(f"Processing {name} with value {value}")
    logger.debug(f"Debug message for {name}: {value}")
    logger.warning(f"Warning about {name}")
    
    print("Test function completed")

if __name__ == "__main__":
    test_function()