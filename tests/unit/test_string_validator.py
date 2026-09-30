import pytest
from src.utils.assertion_helpers import assert_fields_match


class TestAssertFieldsMatch:

    def test_all_fields_match_no_exception(self):
        actual = {"name": "my-repo", "visibility": "public"}
        expected = {"name": "my-repo", "visibility": "public"}
        # Should simply return None / not raise
        assert assert_fields_match(actual, expected) is None

    def test_extra_keys_in_actual_are_ignored(self):
        # actual has more fields than expected — should still pass,
        # since the function only checks that expected is a subset of actual
        actual = {"name": "my-repo", "visibility": "public", "id": 12345}
        expected = {"name": "my-repo"}
        assert assert_fields_match(actual, expected) is None

    def test_empty_expected_never_raises(self):
        # Vacuous truth: nothing to check, nothing to fail
        actual = {"name": "my-repo"}
        expected = {}
        assert assert_fields_match(actual, expected) is None

    def test_missing_key_raises_assertion_error(self):
        actual = {"name": "my-repo"}
        expected = {"visibility": "public"}

        with pytest.raises(AssertionError) as exc_info:
            assert_fields_match(actual, expected, context="repo check")

        message = str(exc_info.value)
        assert "repo check" in message
        assert "visibility" in message

    def test_value_mismatch_raises_assertion_error(self):
        actual = {"visibility": "private"}
        expected = {"visibility": "public"}

        with pytest.raises(AssertionError) as exc_info:
            assert_fields_match(actual, expected, context="visibility check")

        message = str(exc_info.value)
        assert "visibility check" in message
        assert "public" in message
        assert "private" in message

    def test_context_defaults_to_empty_string(self):
        # context is optional — make sure omitting it doesn't blow up,
        # and that the error message is still readable without it
        actual = {"name": "wrong"}
        expected = {"name": "right"}

        with pytest.raises(AssertionError) as exc_info:
            assert_fields_match(actual, expected)

        assert "name" in str(exc_info.value)

    def test_type_mismatch_counts_as_a_failure(self):
        # "5" != 5 in Python — document that this function does NOT coerce types.
        # This matters for GitHub API responses where a field might come back
        # as an int (e.g. id) vs. a string you hardcoded in a test fixture.
        actual = {"count": "5"}
        expected = {"count": 5}

        with pytest.raises(AssertionError):
            assert_fields_match(actual, expected)

    def test_nested_dict_requires_exact_match_not_partial(self):
        # Documents current behavior: if expected_value is itself a dict,
        # equality is checked with ==, meaning the nested dict must match
        # EXACTLY (extra keys inside the nested dict will fail the comparison).
        # This is different from the top-level "subset" behavior tested above.
        actual = {"owner": {"login": "Aferuza", "id": 1, "type": "User"}}
        expected = {"owner": {"login": "Aferuza", "id": 1}}

        with pytest.raises(AssertionError):
            assert_fields_match(actual, expected)

    @pytest.mark.parametrize("actual, expected", [
        ({"a": 1, "b": 2}, {"a": 1}),
        ({"a": 1, "b": 2}, {"a": 1, "b": 2}),
        ({"a": None}, {"a": None}),
        ({"a": 0}, {"a": 0}),
        ({"a": False}, {"a": False}),
    ])
    def test_various_passing_combinations(self, actual, expected):
        assert assert_fields_match(actual, expected) is None

    @pytest.mark.parametrize("actual, expected, missing_key", [
        ({}, {"a": 1}, "a"),
        ({"b": 2}, {"a": 1}, "a"),
        ({"a": 1}, {"a": 1, "b": 2}, "b"),
    ])
    def test_various_missing_key_combinations(self, actual, expected, missing_key):
        with pytest.raises(AssertionError) as exc_info:
            assert_fields_match(actual, expected)
        assert missing_key in str(exc_info.value)