from collections import defaultdict


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

    def insert(self, keyword: str, clean_name: str | None = None) -> None:
        """
        Inserts a keyword into the Trie with its associated clean name.

        This method iteratively traverses the Trie along the path of the word. If a
        character from the word does not exist in the Trie, it creates a new node for
        that character. The method marks the last node corresponding to the last
        character of the word as the end of the word and stores the clean name.

        Args:
            keyword (str): The keyword to be inserted into the Trie.
            clean_name (str | None): The clean name associated with the keyword.
                                    If None, the keyword itself is used as the clean name.
        """
        node = self

        for char in keyword:
            node = node.children[char]

        node.is_end_of_word = True
        node.clean_name = clean_name


class KeywordProcessor:
    """Processes and extracts keywords from text using a Trie structure.

    This class provides methods to add keywords, normalize text, and extract keywords from text.

    Attributes:
        case_sensitive (bool): Determines if keyword matching is case-sensitive.
        root (TrieNode): The root node of the Trie structure.

    Args:
        case_sensitive (bool): Specifies if the keyword matching should be case-sensitive. Defaults to False.
    """

    def __init__(self, case_sensitive: bool = False):
        self.root = TrieNode()
        self.case_sensitive = case_sensitive

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
        self.root.insert(keyword, clean_name)

    def add_keywords_from_dict(self, keyword_dict: dict[str, list[str]]) -> None:
        """
        Adds multiple keywords from a dictionary.

        Args:
            keyword_dict (dict[str, list[str]]): Dictionary where each key is a clean name and associated value is a list of keywords.
        """
        for clean_name, keywords in keyword_dict.items():
            for keyword in keywords:
                self.add_keyword(keyword, clean_name)

    def extract_keywords(self, text: str, span_info=False) -> list[str | tuple[str, int, int]]:
        """
        Extracts keywords from a text. This method navigates through the Trie structure
        to identify and retrieve keywords found in the input text.

        The method iterates through each character of the text. For each character,
        it checks if the character is a part of any keyword stored in the Trie.
        When a keyword is found (denoted by `is_end_of_word`), it checks if the keyword
        is correctly bounded by non-alphanumeric characters (or text boundaries),
        ensuring that only whole words are matched.

        If `span_info` is set to True, the method also returns the start and end
        positions of each keyword in the text, providing additional context about
        where each keyword is located.

        Args:
            text (str): The text to extract keywords from. The text is normalized
                        based on the case sensitivity setting of the processor.
            span_info (bool): If True, the method returns a list of tuples, each
                            containing the extracted keyword and its start and
                            end indices in the text. If False, only the keywords
                            are returned. Defaults to False.

        Returns:
            list[str | tuple[str, int, int]]: A list of extracted keywords, or tuples
                                            containing the keyword and its span
                                            (start and end indices) in the text.
        """
        normalized_text = self._normalize(text)
        results = []
        node = self.root
        start_idx = 0

        for idx, char in enumerate(normalized_text):
            if char in node.children:
                node = node.children[char]
                if node.is_end_of_word and (idx == len(normalized_text) - 1 or not normalized_text[idx + 1].isalnum()):
                    end_idx = idx + 1
                    match = (node.clean_name, start_idx, end_idx) if span_info else node.clean_name
                    results.append(match)
                    node = self.root
                    start_idx = end_idx
            else:
                node = self.root
                start_idx = idx + 1

        return results
