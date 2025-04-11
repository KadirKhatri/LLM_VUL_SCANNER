import pytest
from app.scanner import LLMSecurityScanner
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_model():
    model = MagicMock()
    tokenizer = MagicMock()
    tokenizer.pad_token = None
    tokenizer.eos_token = '<|endoftext|>'
    return model, tokenizer


def test_model_loading(mock_model):
    model, tokenizer = mock_model
    with patch('transformers.AutoTokenizer.from_pretrained', return_value=tokenizer), \
            patch('transformers.AutoModelForCausalLM.from_pretrained', return_value=model):
        scanner = LLMSecurityScanner('mock/model')
        assert scanner.tokenizer == tokenizer
        assert scanner.model == model
        assert scanner.tokenizer.pad_token == '<|endoftext|>'


def test_scan_without_loading():
    scanner = LLMSecurityScanner('mock/model')
    scanner.model = None  # Simulate failed loading
    with pytest.raises(RuntimeError, match="Model not loaded"):
        scanner.scan()


def test_severity_calculation():
    scanner = LLMSecurityScanner('mock/model')

    test_cases = [
        ({'prompt_injection': {'severity': 'low'}}, 'low'),
        ({'prompt_injection': {'severity': 'high'}, 'bias': {'severity': 'medium'}}, 'high'),
        ({'prompt_injection': {'severity': 'none'}, 'backdoor': {'severity': 'critical'}}, 'critical'),
        ({'prompt_injection': {'severity': 'medium'}, 'bias': {'severity': 'low'}, 'backdoor': {'severity': 'medium'}},
         'medium')
    ]

    for results, expected in test_cases:
        assert scanner._calculate_overall_severity(results) == expected