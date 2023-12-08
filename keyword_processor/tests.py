import pytest

from .processor import KeywordProcessor


class TestKeywordProcessor:
    @pytest.fixture
    def processor(self):
        return KeywordProcessor(case_sensitive=False)

    def test_add_keyword(self, processor):
        processor.add_keyword("Python", "Python Programming")
        assert "python" in processor.keyword_map
        assert processor.keyword_map["python"] == "Python Programming"

    def test_case_sensitivity(self):
        processor = KeywordProcessor(case_sensitive=True)
        processor.add_keyword("Python", "Python Programming")
        assert "Python" in processor.keyword_map
        assert "python" not in processor.keyword_map

    def test_extract_keywords(self, processor):
        processor.add_keyword("python", "Python Programming")
        processor.add_keyword("java", "Java Programming")
        extracted_keywords = processor.extract_keywords("I love Python and Java.")
        assert extracted_keywords == ["Python Programming", "Java Programming"]

    def test_add_keywords_from_dict(self, processor):
        keyword_dict = {"Programming": ["Python", "Java", "C++"]}
        processor.add_keywords_from_dict(keyword_dict)
        assert "python" in processor.keyword_map
        assert "java" in processor.keyword_map
        assert "c++" in processor.keyword_map
        assert processor.keyword_map["python"] == "Programming"

    def test_add_keyword_from_file(self, processor, tmpdir):
        # Create a temporary keyword file
        keyword_file = tmpdir.join("keywords.txt")
        keyword_file.write("Python=>Python Programming\nJava=>Java Programming")
        processor.add_keyword_from_file(str(keyword_file))
        assert "python" in processor.keyword_map
        assert "java" in processor.keyword_map
        assert processor.keyword_map["python"] == "Python Programming"
        assert processor.keyword_map["java"] == "Java Programming"

    def test_add_keyword_from_file_with_invalid_path(self, processor):
        invalid_path = "invalid/path/to/file.txt"
        with pytest.raises(IOError) as excinfo:
            processor.add_keyword_from_file(invalid_path)
        assert str(excinfo.value) == f"Invalid file path {invalid_path}"

    def test_extract_keywords_with_span_info(self, processor):
        processor.add_keyword("python", "Python Programming")
        extracted_keywords = processor.extract_keywords("I love Python.", span_info=True)
        assert extracted_keywords == [("Python Programming", 7, 13)]
