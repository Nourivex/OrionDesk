from core.argument_extractor import ArgumentExtractor


def test_argument_extractor_extracts_target_and_path() -> None:
    extractor = ArgumentExtractor()

    payload = extractor.extract("delete C:/temp/file.txt").to_dict()

    assert payload["keyword"] == "delete"
    assert payload["target"] == "C:/temp/file.txt"
    assert payload["path"] == "C:/temp/file.txt"


def test_argument_extractor_extracts_mode_and_flags() -> None:
    extractor = ArgumentExtractor()

    payload = extractor.extract("mode focus --silent").to_dict()

    assert payload["keyword"] == "mode"
    assert payload["mode"] == "focus"
    assert "--silent" in payload["flags"]
