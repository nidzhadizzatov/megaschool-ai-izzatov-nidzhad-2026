"""AI Client - OpenAI API wrapper для анализа кода"""
import os
import json
from pathlib import Path
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@dataclass
class AnalysisResult:
    """Результат анализа файла"""
    issue_found: bool
    code_correction: str
    explanation: str = ""


@dataclass
class ReviewResult:
    """Результат ревью PR"""
    approved: bool
    summary: str
    issues: list[str]
    suggestions: list[str]


ANALYSIS_PROMPT = """You are an expert code reviewer. Analyze this file for the described issue.

## Issue Description:
{issue_description}

## File: {filepath}
```{language}
{file_content}
```

## Your Task:
1. Analyze if this file contains the issue described above
2. If yes, provide the COMPLETE corrected file content
3. If no, indicate that no changes needed

## IMPORTANT:
- Return the ENTIRE file content if changes are needed, not just the changed parts
- Preserve all existing code that doesn't need changes
- Follow best practices (PEP8 for Python, etc.)

## Response Format (JSON only):
{{
    "issue_found": true/false,
    "code_correction": "COMPLETE file content with fixes, or empty string if no changes",
    "explanation": "Brief explanation of what was found/fixed"
}}

Return ONLY valid JSON, no markdown, no additional text."""


REVIEW_PROMPT = """You are an expert code reviewer. Review this Pull Request thoroughly.

{issue_context}

Changed files: {changed_files}

Code diff:
{diff}

Linter results:
{linter_output}

Test results:
{test_output}

Analyze:
1. Does implementation match the issue requirements?
2. Code quality (PEP8, type hints, docstrings)
3. Potential bugs or edge cases
4. Security issues
5. Test coverage

Return ONLY valid JSON:
{{
    "approved": true/false,
    "summary": "2-3 sentence summary",
    "issues": ["critical issues requiring changes"],
    "suggestions": ["non-blocking suggestions"],
    "score": 1-10
}}"""


class AIClient:
    """OpenAI client для анализа кода и ревью"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )
        self.model = MODEL
    
    def _call(self, messages: list, temperature: float = 0.3) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _get_language(self, filepath: Path) -> str:
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "jsx",
            ".tsx": "tsx",
        }
        return ext_map.get(filepath.suffix, "")
    
    def analyze_file(
        self,
        filepath: Path,
        file_content: str,
        issue_description: str
    ) -> AnalysisResult:
        """Анализирует файл на наличие issue."""
        language = self._get_language(filepath)
        
        prompt = ANALYSIS_PROMPT.format(
            issue_description=issue_description,
            filepath=str(filepath),
            language=language,
            file_content=file_content
        )
        
        print(f"🔍 Analyzing {filepath.name}...")
        
        try:
            response = self._call([{"role": "user", "content": prompt}], temperature=0.2)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("\n", 1)[1]
                response = response.rsplit("```", 1)[0]
            
            data = json.loads(response)
            return AnalysisResult(
                issue_found=data.get("issue_found", False),
                code_correction=data.get("code_correction", ""),
                explanation=data.get("explanation", "")
            )
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return AnalysisResult(issue_found=False, code_correction="", explanation=str(e))
    
    def review_pr(
        self,
        diff: str,
        changed_files: list[str],
        issue_context: str = "",
        linter_output: str = "",
        test_output: str = ""
    ) -> ReviewResult:
        """Ревью Pull Request."""
        prompt = REVIEW_PROMPT.format(
            issue_context=issue_context or "No linked issue",
            changed_files=", ".join(changed_files),
            diff=diff[:8000],
            linter_output=linter_output[:2000],
            test_output=test_output[:2000]
        )
        
        try:
            response = self._call([{"role": "user", "content": prompt}], temperature=0.2)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("\n", 1)[1]
                response = response.rsplit("```", 1)[0]
            
            data = json.loads(response)
            return ReviewResult(
                approved=data.get("approved", False),
                summary=data.get("summary", ""),
                issues=data.get("issues", []),
                suggestions=data.get("suggestions", [])
            )
        except Exception as e:
            print(f"❌ Review failed: {e}")
            return ReviewResult(approved=False, summary=str(e), issues=[], suggestions=[])
    
    def generate_code(
        self,
        file_path: str,
        requirements: str,
        existing_code: str = "",
        issue_context: str = ""
    ) -> str:
        """Генерирует или модифицирует код."""
        system_prompt = """You are an expert Python developer. 
Generate clean, production-ready code.
Follow PEP8, use type hints, add docstrings.
Return ONLY the code, no explanations or markdown."""
        
        user_prompt = f"""Generate/modify code for: {file_path}

Requirements: {requirements}

Issue context: {issue_context}

{"Existing code:" if existing_code else "Create new file:"}
{existing_code}

Return ONLY the complete Python code."""
        
        response = self._call([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.2)
        
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[1]
            response = response.rsplit("```", 1)[0]
        
        return response


# Singleton instance
ai_client = AIClient()
