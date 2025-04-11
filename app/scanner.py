import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from .vulnerabilities import prompt_injection, bias_detection, backdoor
import json
import time
from pathlib import Path


class LLMSecurityScanner:
    def __init__(self, model_path, device=None):
        self.model_path = model_path
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.tokenizer = None
        self.load_model()

    def load_model(self):
        """Load the model and tokenizer from HuggingFace"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path).to(self.device)
            if not self.tokenizer.pad_token:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        except Exception as e:
            raise ValueError(f"Failed to load model: {str(e)}")

    def scan(self):
        """Run all vulnerability scans"""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded")

        results = {
            'model': self.model_path,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'results': {}
        }

        results['results']['prompt_injection'] = prompt_injection.scan(self.model, self.tokenizer, self.device)
        results['results']['bias'] = bias_detection.scan(self.model, self.tokenizer, self.device)
        results['results']['backdoor'] = backdoor.scan(self.model, self.tokenizer, self.device)

        results['overall_severity'] = self._calculate_overall_severity(results['results'])

        return results

    def _calculate_overall_severity(self, results):
        """Determine overall severity based on individual scans"""
        severity_map = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'none': 0}
        max_severity = 0

        for scan in results.values():
            current = severity_map.get(scan.get('severity', 'none'), 0)
            if current > max_severity:
                max_severity = current

        severity_reverse_map = {v: k for k, v in severity_map.items()}
        return severity_reverse_map.get(max_severity, 'none')

    def generate_html_report(self, scan_results, output_path='report.html'):
        """Generate HTML report from scan results"""
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(Path(__file__).parent / 'templates'))
        template = env.get_template('report.html')
        html = template.render(**scan_results)

        with open(output_path, 'w') as f:
            f.write(html)

        return output_path