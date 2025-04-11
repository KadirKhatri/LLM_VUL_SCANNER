from flask import Flask, request, jsonify, send_file
from .scanner import LLMSecurityScanner
import tempfile
import os

app = Flask(__name__)


@app.route('/scan', methods=['POST'])
def scan_model():
    """Scan a model for vulnerabilities"""
    data = request.get_json()

    if not data or 'model_path' not in data:
        return jsonify({'error': 'model_path is required'}), 400

    try:
        scanner = LLMSecurityScanner(data['model_path'])
        results = scanner.scan()

        if data.get('format', 'json') == 'html':
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
                report_path = scanner.generate_html_report(results, f.name)
            return send_file(report_path, as_attachment=True, download_name='security_report.html')

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)