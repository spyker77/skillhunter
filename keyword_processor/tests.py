import pytest

from keyword_processor import KeywordProcessor


class TestKeywordProcessor:
    @pytest.fixture
    def processor(self):
        return KeywordProcessor(case_sensitive=False)

    @pytest.mark.parametrize(
        "case_sensitive, keyword, expected_node_path",
        [
            (False, "Python", "python"),
            (True, "Python", "Python"),
        ],
    )
    def test_add_keyword_with_case_sensitivity(self, case_sensitive, keyword, expected_node_path):
        processor = KeywordProcessor(case_sensitive=case_sensitive)
        processor.add_keyword(keyword, "Python Programming")

        node = processor.root
        for char in expected_node_path:
            assert char in node.children
            node = node.children[char]

        assert node.is_end_of_word
        assert node.clean_name == "Python Programming"

    def test_add_keywords_from_dict(self, processor):
        keyword_dict = {"Programming": ["Python", "Java", "C++"]}
        processor.add_keywords_from_dict(keyword_dict)
        # Check if the keywords are correctly added to the Trie.
        for lang in ["Python", "Java", "C++"]:
            node = processor.root
            for char in processor._normalize(lang):
                assert char in node.children
                node = node.children[char]
            assert node.is_end_of_word
            assert node.clean_name == "Programming"

    def test_extract_keywords(self, processor):
        processor.add_keyword("python", "Python Programming")
        processor.add_keyword("java", "Java Programming")
        extracted_keywords = processor.extract_keywords("I love Python and Java.")
        assert extracted_keywords == ["Python Programming", "Java Programming"]

    def test_extract_keywords_with_span_info(self, processor):
        processor.add_keyword("python", "Python Programming")
        extracted_keywords = processor.extract_keywords("I love Python.", span_info=True)
        assert extracted_keywords == [("Python Programming", 7, 13)]
        extracted_keywords = processor.extract_keywords("I love Python.", span_info=True)
        assert extracted_keywords == [("Python Programming", 7, 13)]
