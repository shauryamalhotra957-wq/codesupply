# Contributing to CodeSupply

First off, thank you for considering contributing to CodeSupply! It's people like you that make the open-source community such a great place to learn, inspire, and create.

## 💻 Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (optional, for full stack local testing)

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the dev server: `uvicorn app.main:app --reload`

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Run the dev server: `npm run dev`

## 🎨 Code Style

We enforce strict code formatting to keep the codebase clean and readable.

- **Python (Backend)**: We use **Ruff** for formatting and linting.
  - Run `ruff check .` to lint.
  - Run `ruff format .` to auto-format.
- **TypeScript (Frontend)**: We use **ESLint** and **Prettier**.
  - Run `npm run lint` to check for issues.
  - Run `npm run format` to auto-format.

## 🧪 Testing Requirements

All new features and bug fixes **must** include tests.

- **Backend**: Use `pytest`. Place tests in `backend/tests/`. Ensure you cover both success paths and edge cases (especially malicious archive structures).
- **Frontend**: Use Jest and React Testing Library. Place tests alongside components or in `frontend/__tests__/`.

Run tests before submitting a PR to ensure nothing is broken.

## 📝 Pull Request Guidelines

1. **Fork the repository** and create your branch from `main`.
2. **Use descriptive branch names**: e.g., `feat/add-ruby-support` or `fix/sbom-date-format`.
3. **Write clear commit messages**.
4. **Update documentation**: If you are adding a feature, update `README.md`, `docs/API.md`, or component documentation as needed.
5. **Open a Draft PR** if you want feedback early.
6. Ensure CI checks pass (formatting, linting, tests).

## 🏗️ Architecture Overview for New Contributors

If you're looking to contribute but don't know where to start, here is a quick map of the codebase:

- **Adding a new ecosystem parser?** Look at `backend/app/services/scanners/`. Each ecosystem (npm, pypi) implements a base interface to extract dependencies from manifests.
- **Improving risk models?** Check `backend/app/core/risk.py`. This is where CVSS scores are translated into CodeSupply's proprietary risk assessment.
- **Frontend UI changes?** We use Next.js App Router (`frontend/app/`) and Shadcn UI (`frontend/components/ui/`). The main dashboard logic is in `frontend/components/dashboard/`.
- **API Endpoints**: Located in `backend/app/api/v1/`.

If you have any questions, feel free to open a Discussion on GitHub!
