from collections import defaultdict
from pathlib import Path


class TrieNode:
    """A node in the Trie structure used for efficient keyword searching.

    Attributes:
        children (dict): A dictionary mapping characters to their corresponding TrieNode.
        is_end_of_word (bool): Indicates if the node represents the end of a keyword.
        clean_name (str | None): The associated clean name for the keyword represented by this node.
    """

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = defaultdict(TrieNode)
        self.is_end_of_word: bool = False
        self.clean_name: str | None = None


class KeywordProcessor:
    """Processes and extracts keywords from text using a Trie structure.

    This class provides methods to add keywords, normalize text, and extract keywords from sentences.

    Attributes:
        case_sensitive (bool): Determines if keyword matching is case-sensitive.
        root (TrieNode): The root node of the Trie structure.
        keyword_map (dict): A map from keywords to their clean names.

    Args:
        case_sensitive (bool): Specifies if the keyword matching should be case-sensitive. Defaults to False.
    """

    def __init__(self, case_sensitive: bool = False) -> None:
        self.case_sensitive: bool = case_sensitive
        self.root: TrieNode = TrieNode()
        self.keyword_map: dict[str, str] = {}

    def _normalize(self, text: str) -> str:
        """
        Normalizes the text based on case sensitivity.

        Args:
            text (str): The text to normalize.

        Returns:
            str: Normalized text.
        """
        return text if self.case_sensitive else text.lower()

    def add_keyword(self, keyword: str, clean_name: str | None = None) -> None:
        """
        Adds a keyword to the trie and keyword map.

        Args:
            keyword (str): The keyword to add.
            clean_name (str | None): The clean name associated with the keyword. Defaults to None.
        """
        clean_name = clean_name or keyword
        keyword = self._normalize(keyword)
        self.keyword_map[keyword] = clean_name

        node = self.root
        for char in keyword:
            node = node.children[char]

        node.is_end_of_word = True
        node.clean_name = clean_name

    def add_keyword_from_file(self, keyword_file: str, encoding: str = "utf-8") -> None:
        """
        Adds keywords from a file.

        Args:
            keyword_file (str): Path to the file containing keywords.
            encoding (str): The encoding of the file. Defaults to "utf-8".
        """
        file_path = Path(keyword_file)

        if not file_path.is_file():
            raise OSError(f"Invalid file path {keyword_file}")

        with file_path.open(encoding=encoding) as file:
            for line in file:
                parts = line.split("=>")
                keyword = parts[0].strip()
                clean_name = parts[1].strip() if len(parts) > 1 and parts[1] else None
                self.add_keyword(keyword, clean_name)

    def add_keywords_from_dict(self, keyword_dict: dict[str, list[str]]) -> None:
        """
        Adds multiple keywords from a dictionary.

        Args:
            keyword_dict (dict[str, list[str]]): Dictionary where each key is a clean name and associated value is a list of keywords.
        """
        for clean_name, keywords in keyword_dict.items():
            for keyword in keywords:
                self.add_keyword(keyword, clean_name)

    def _is_word_boundary(self, sentence: str, start_idx: int, end_idx: int) -> bool:
        """
        Checks if a given index is a word boundary in the sentence.

        Args:
            sentence (str): The sentence to check within.
            start_idx (int): The starting index of the word.
            end_idx (int): The ending index of the word.

        Returns:
            bool: True if the indices represent a word boundary, False otherwise.
        """
        if start_idx > 0 and sentence[start_idx - 1].isalnum():
            return False
        if end_idx < len(sentence) and sentence[end_idx].isalnum():
            return False
        return True

    def extract_keywords(self, sentence: str, span_info: bool = False) -> list[str | tuple[str, int, int]]:
        """
        Extracts keywords from a sentence.

        Args:
            sentence (str): The sentence to extract keywords from.
            span_info (bool): If True, returns a list of tuples with the keyword, start index, and end index. Defaults to False.

        Returns:
            list[str | tuple[str, int, int]]: A list of extracted keywords or tuples containing the keyword and its span in the sentence.
        """
        sentence = self._normalize(sentence)
        results = []

        for start_pos in range(len(sentence)):
            node = self.root
            for end_pos in range(start_pos, len(sentence)):
                char = sentence[end_pos]
                if char in node.children:
                    node = node.children[char]
                    if node.is_end_of_word and self._is_word_boundary(sentence, start_pos, end_pos + 1):
                        clean_name = node.clean_name
                        match = (clean_name, start_pos, end_pos + 1) if span_info else clean_name
                        results.append(match)
                        break
                else:
                    break

        return results
