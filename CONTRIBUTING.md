# Contributing to CodeSupply

Thank you for your interest in contributing to **CodeSupply**! We welcome contributions to our SBOM generator and supply-chain risk analysis engine.

## Development Workflow

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Set up the backend environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   pip install pytest httpx
   ```

3. Set up the frontend environment:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. Run the test suite before submitting:
   ```bash
   pytest tests/ -v
   ```

5. Open a Pull Request with a clear description of your changes and test coverage.

## Code Standards
- Python: Follow PEP 8 guidelines. Include type hints where applicable.
- TypeScript / React: Use strict typing and clean component decomposition.
- Security: Maintain zero-code-execution guarantees on all file parsers.
