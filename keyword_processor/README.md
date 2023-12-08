# Reworked FlashText Keyword Processor

## Overview

This module presents a reworked and optimized version of the [FlashText](https://pypi.org/project/flashtext/) library for Python. It aims to provide a modern, efficient, and easy-to-maintain implementation for keyword extraction in large texts.

## Features

- **Case Sensitivity**: Supports both case-sensitive and case-insensitive keyword processing.
- **Efficient Extraction**: Offers efficient extraction of keywords from large text datasets.
- **Flexible Keyword Addition**: Allows adding keywords from various sources including files, dictionaries, or directly as strings.
- **Optimized Trie Structure**: Utilizes a custom Trie data structure for optimized search performance.

## Usage

Here is a basic example of how to use the reworked KeywordProcessor:

```python
from keyword_processor import KeywordProcessor

# Initialize the processor with case sensitivity preference
processor = KeywordProcessor(case_sensitive=False)

# Add keywords and their respective clean names
processor.add_keyword("Python", "Python Programming")
processor.add_keyword("Java", "Java Programming")

# Extract keywords from text
text = "I love Python and Java programming languages."
extracted_keywords = processor.extract_keywords(text)

print(extracted_keywords)  # Output: ['Python Programming', 'Java Programming']
```
