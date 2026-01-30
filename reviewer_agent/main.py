import os
import sys
import json
import subprocess
from github import Github
from openai import OpenAI

def run_linter() -> str:
    try:
        result = subprocess.run(
            ["ruff", "check", ".", "--output-format=json"],
            capture_output=True, text=True, timeout=60
        )
        return result.stdout if result.stdout else "No issues"
    except Exception as e:
        return str(e)

def run_tests() -> str:
    try:
        result = subprocess.run(
            ["pytest", "tests/", "-v", "--tb=short"],
            capture_output=True, text=True, timeout=120
        )
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

def get_issue_from_pr(pr) -> tuple[str, str]:
    body = pr.body or ""
    if "#" in body:
        try:
            parts = body.split("#")[1].split()
            issue_num = int(parts[0])
            repo = pr.base.repo
            issue = repo.get_issue(issue_num)
            return issue.title, issue.body or ""
        except:
            pass
    return "", ""

def main():
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = int(os.getenv("PR_NUMBER", 0))
    
    if not pr_number:
        print("❌ PR_NUMBER not set")
        sys.exit(1)
    
    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    print(f"🔍 Reviewing PR #{pr_number}: {pr.title}")
    
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    )
    
    diff = ""
    changed_files = []
    for file in pr.get_files():
        changed_files.append(file.filename)
        diff += f"\n## {file.filename}\n{file.patch or 'Binary file'}\n"
    
    issue_title, issue_body = get_issue_from_pr(pr)
    issue_context = f"Issue: {issue_title}\n{issue_body}" if issue_title else "No linked issue"
    
    linter_output = run_linter()
    test_output = run_tests()
    
    prompt = f"""You are an expert code reviewer. Review this Pull Request thoroughly.

{issue_context}

Changed files: {', '.join(changed_files)}

Code diff:
{diff[:8000]}

Linter results:
{linter_output[:2000]}

Test results:
{test_output[:2000]}

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
    
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    
    content = response.choices[0].message.content.strip()
    content = content.replace("```json", "").replace("```", "").strip()
    
    try:
        result = json.loads(content)
    except:
        result = {"approved": False, "summary": content, "issues": [], "suggestions": [], "score": 5}
    
    review_body = f"""## Code Review

**Score:** {result.get('score', '?')}/10

### Summary
{result.get('summary', 'No summary')}

"""
    
    if result.get('issues'):
        review_body += "### ❌ Issues (require fixes)\n"
        for issue in result['issues']:
            review_body += f"- {issue}\n"
        review_body += "\n"
    
    if result.get('suggestions'):
        review_body += "### 💡 Suggestions\n"
        for sug in result['suggestions']:
            review_body += f"- {sug}\n"
        review_body += "\n"
    
    review_body += f"""### CI Results
- **Linter:** {'✅ Pass' if 'No issues' in linter_output else '⚠️ Issues found'}
- **Tests:** {'✅ Pass' if 'passed' in test_output.lower() else '⚠️ Check logs'}
"""
    
    if result.get('approved', False) and result.get('score', 0) >= 7:
        pr.create_review(body=review_body, event="APPROVE")
        print("✅ PR Approved")
    else:
        pr.create_review(body=review_body, event="REQUEST_CHANGES")
        print("❌ Changes requested")
        
        # Trigger Code Agent to fix if there are issues
        if result.get('issues'):
            pr.create_issue_comment("🔄 @code-agent please fix the issues above")

if __name__ == "__main__":
    main()
