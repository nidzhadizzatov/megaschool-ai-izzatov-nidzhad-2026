"""Repository Manager - Git и GitHub операции"""
import os
import shutil
import uuid
from pathlib import Path
from git import Repo, GitCommandError
from github import Github, GithubException
from dotenv import load_dotenv
import fnmatch

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BASE_DIR = Path(__file__).parent
REPOS_DIR = Path(os.getenv("REPOS_DIR", BASE_DIR / "repos"))

REPOS_DIR.mkdir(parents=True, exist_ok=True)


class RepoManager:
    """Управление Git репозиториями - клонирование, commits, PRs"""
    
    def __init__(self, repo_full_name: str, unique_id: str = None):
        """
        Args:
            repo_full_name: owner/repo формат
            unique_id: Уникальный ID для папки (UUID), если не указан - генерируется
        """
        self.repo_full_name = repo_full_name
        # Используем UUID для уникальной папки (repos/{UUID}/)
        self.unique_id = unique_id or str(uuid.uuid4())[:8]
        self.repo_path = REPOS_DIR / self.unique_id
        self.repo: Repo = None
        self.github = Github(GITHUB_TOKEN)
        self.gh_repo = self.github.get_repo(repo_full_name)
    
    @property
    def clone_url(self) -> str:
        """URL для клонирования с токеном"""
        return f"https://x-access-token:{GITHUB_TOKEN}@github.com/{self.repo_full_name}.git"
    
    def clone_or_pull(self) -> Path:
        """Клонирует репо или делает pull если существует."""
        if self.repo_path.exists():
            print(f"⬇️ Pulling {self.repo_full_name}...")
            try:
                self.repo = Repo(self.repo_path)
                self.repo.git.reset("--hard", "HEAD")
                self.repo.git.clean("-fd")
                default_branch = self._get_default_branch()
                self.repo.git.checkout(default_branch)
                self.repo.remotes.origin.pull()
                print(f"✅ Pulled {self.repo_full_name}")
            except GitCommandError as e:
                print(f"⚠️ Pull failed, re-cloning: {e}")
                shutil.rmtree(self.repo_path)
                return self.clone_or_pull()
        else:
            print(f"📥 Cloning {self.repo_full_name}...")
            self.repo_path.parent.mkdir(parents=True, exist_ok=True)
            self.repo = Repo.clone_from(self.clone_url, self.repo_path)
            print(f"✅ Cloned {self.repo_full_name}")
        
        return self.repo_path
    
    def _get_default_branch(self) -> str:
        """Определяет default branch (main или master)"""
        try:
            return self.gh_repo.default_branch
        except:
            return "main"
    
    def create_branch(self, branch_name: str) -> None:
        """Создаёт новую ветку."""
        if self.repo is None:
            self.repo = Repo(self.repo_path)
        
        try:
            if branch_name in [b.name for b in self.repo.branches]:
                print(f"ℹ️ Branch {branch_name} exists, checking out")
                self.repo.git.checkout(branch_name)
            else:
                print(f"🌿 Creating branch {branch_name}")
                self.repo.git.checkout("-b", branch_name)
        except GitCommandError as e:
            print(f"❌ Failed to create branch: {e}")
            raise
    
    def get_files(self, extensions: list[str] = None) -> list[Path]:
        """Получает список файлов в репо с учётом .github/agent_ignore.txt."""
        if extensions is None:
            extensions = [".py", ".js", ".ts", ".jsx", ".tsx"]
        
        # Загружаем ignore patterns из .github/agent_ignore.txt
        ignore_patterns = self._load_agent_ignore()
        
        files = []
        for ext in extensions:
            files.extend(self.repo_path.rglob(f"*{ext}"))
        
        # Базовые исключения
        excluded = {".git", "__pycache__", "node_modules", ".venv", "venv", ".tox", "dist", "build"}
        
        # Фильтруем файлы
        filtered_files = []
        for f in files:
            # Проверяем базовые исключения
            if any(ex in f.parts for ex in excluded):
                continue
            
            # Проверяем agent_ignore patterns
            relative_path = f.relative_to(self.repo_path)
            if self._should_ignore(relative_path, ignore_patterns):
                continue
            
            filtered_files.append(f)
        
        return sorted(filtered_files)
    
    def _load_agent_ignore(self) -> list[str]:
        """Загружает patterns из .github/agent_ignore.txt."""
        ignore_file = self.repo_path / ".github" / "agent_ignore.txt"
        patterns = []
        
        if ignore_file.exists():
            try:
                content = ignore_file.read_text(encoding="utf-8")
                for line in content.splitlines():
                    line = line.strip()
                    # Пропускаем комментарии и пустые строки
                    if line and not line.startswith("#"):
                        patterns.append(line)
                print(f"📋 Loaded {len(patterns)} ignore patterns from agent_ignore.txt")
            except Exception as e:
                print(f"⚠️ Failed to load agent_ignore.txt: {e}")
        
        return patterns
    
    def _should_ignore(self, path: Path, patterns: list[str]) -> bool:
        """Проверяет, нужно ли игнорировать файл по patterns."""
        path_str = str(path).replace("\\", "/")
        
        for pattern in patterns:
            # Поддержка директорий (заканчиваются на /)
            if pattern.endswith("/"):
                if path_str.startswith(pattern.rstrip("/")):
                    return True
            # Поддержка glob patterns
            elif fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path.name, pattern):
                return True
        
        return False
    
    def read_file(self, filepath: Path) -> str:
        """Читает содержимое файла."""
        try:
            return filepath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"❌ Failed to read {filepath}: {e}")
            return ""
    
    def write_file(self, filepath: Path, content: str) -> None:
        """Записывает содержимое в файл."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")
        print(f"✅ Written: {filepath.relative_to(self.repo_path)}")
    
    def commit(self, message: str) -> str:
        """Коммитит изменения."""
        if self.repo is None:
            self.repo = Repo(self.repo_path)
        
        self.repo.git.add("-A")
        self.repo.git.commit("-m", message)
        sha = self.repo.head.commit.hexsha
        print(f"✅ Committed: {sha[:8]}")
        return sha
    
    def push(self, branch_name: str) -> None:
        """Push изменений в remote."""
        if self.repo is None:
            self.repo = Repo(self.repo_path)
        
        print(f"⬆️ Pushing {branch_name}...")
        self.repo.git.push("--set-upstream", "origin", branch_name, "--force")
        print(f"✅ Pushed {branch_name}")
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = None
    ) -> int:
        """Создаёт Pull Request."""
        if base is None:
            base = self._get_default_branch()
        
        try:
            existing = list(self.gh_repo.get_pulls(state='open', head=f"{self.gh_repo.owner.login}:{head}"))
            if existing:
                print(f"ℹ️ PR already exists: #{existing[0].number}")
                return existing[0].number
        except:
            pass
        
        pr = self.gh_repo.create_pull(
            title=title,
            body=body,
            head=head,
            base=base
        )
        print(f"✅ Created PR #{pr.number}")
        return pr.number
    
    def get_issue(self, issue_number: int):
        """Получает issue из GitHub."""
        return self.gh_repo.get_issue(issue_number)
    
    def add_comment_to_issue(self, issue_number: int, comment: str):
        """Добавляет комментарий к issue."""
        issue = self.get_issue(issue_number)
        issue.create_comment(comment)
    
    def get_file_content_from_github(self, file_path: str, ref: str = "main") -> str:
        """Получает содержимое файла напрямую из GitHub."""
        try:
            content = self.gh_repo.get_contents(file_path, ref=ref)
            return content.decoded_content.decode()
        except GithubException:
            return ""
    
    def list_files_from_github(self, path: str = "", ref: str = "main") -> list[str]:
        """Получает список файлов из GitHub."""
        files = []
        try:
            contents = self.gh_repo.get_contents(path, ref=ref)
            while contents:
                item = contents.pop(0)
                if item.type == "dir":
                    contents.extend(self.gh_repo.get_contents(item.path, ref=ref))
                else:
                    files.append(item.path)
        except GithubException:
            pass
        return files
    
    def cleanup(self) -> None:
        """Удаляет локальную папку репозитория после работы."""
        if self.repo_path.exists():
            print(f"🧹 Cleaning up {self.repo_path}")
            try:
                # Закрываем git repo если открыт
                if self.repo:
                    self.repo.close()
                    self.repo = None
                shutil.rmtree(self.repo_path)
                print(f"✅ Cleaned up {self.unique_id}")
            except Exception as e:
                print(f"⚠️ Cleanup error: {e}")


# Singleton-like access for current repo
_current_repo = None

def get_repo_manager(repo_full_name: str = None) -> RepoManager:
    """Получает или создаёт RepoManager."""
    global _current_repo
    if repo_full_name:
        _current_repo = RepoManager(repo_full_name)
    elif _current_repo is None:
        repo = os.getenv("GITHUB_REPO")
        if repo:
            _current_repo = RepoManager(repo)
        else:
            raise ValueError("GITHUB_REPO not set")
    return _current_repo
