"""
Tests for the agent modules.

These tests verify that each agent correctly processes its input
and produces the expected output. We mock the OpenAI API calls
so tests are fast, free, and don't need a real API key.
"""

from unittest.mock import patch, MagicMock
from agents.router import detect_regulations, router_agent
from agents.state import AgentState


# --- Router Agent Tests ---

class TestDetectRegulations:
    """Test the keyword-based regulation detection."""

    def test_detects_sr_11_7(self):
        assert detect_regulations("What does SR 11-7 say?") == ["SR 11-7"]

    def test_detects_sr_11_7_no_space(self):
        assert detect_regulations("SR11-7 requirements") == ["SR 11-7"]

    def test_detects_nist(self):
        result = detect_regulations("NIST AI RMF guidelines")
        assert "NIST AI RMF" in result

    def test_detects_multiple(self):
        result = detect_regulations("Compare SR 11-7 and NIST frameworks")
        assert "SR 11-7" in result
        assert "NIST AI RMF" in result

    def test_detects_colorado(self):
        result = detect_regulations("Colorado SB21-169 insurance rules")
        assert "Colorado SB21-169" in result

    def test_detects_naic(self):
        result = detect_regulations("NAIC model bulletin on AI")
        assert "NAIC Model Bulletin" in result

    def test_no_regulation_mentioned(self):
        assert detect_regulations("What is model risk?") == []


class TestRouterAgent:
    """Test the router agent with mocked LLM."""

    def _make_state(self, query: str) -> AgentState:
        return {
            "query": query,
            "query_type": "",
            "target_regulations": [],
            "retrieved_docs": [],
            "answer": "",
            "verification": {},
            "retry_count": 0,
        }

    @patch("agents.router.llm")
    def test_classifies_lookup(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "LOOKUP"
        mock_llm.invoke.return_value = mock_response

        state = self._make_state("What does SR 11-7 say about validation?")
        result = router_agent(state)

        assert result["query_type"] == "LOOKUP"
        assert "SR 11-7" in result["target_regulations"]

    @patch("agents.router.llm")
    def test_classifies_compare(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "COMPARE"
        mock_llm.invoke.return_value = mock_response

        state = self._make_state("How do SR 11-7 and NIST differ?")
        result = router_agent(state)

        assert result["query_type"] == "COMPARE"
        assert len(result["target_regulations"]) == 2

    @patch("agents.router.llm")
    def test_defaults_to_explain_on_invalid(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "INVALID_TYPE"
        mock_llm.invoke.return_value = mock_response

        state = self._make_state("Some random question")
        result = router_agent(state)

        assert result["query_type"] == "EXPLAIN"
