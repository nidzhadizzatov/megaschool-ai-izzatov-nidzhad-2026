def calculate_average(numbers):
    """Calculates the average of a list of numbers."""
    if not numbers:
        return 0  # or return None if preferred
    return sum(numbers) / len(numbers)


# The rest of the file remains unchanged


class IssueSolver:
    """Решает issues - клонирует репо, анализирует файлы, создаёт PR"""
    
    def __init__(self, repo_full_name: str):
        self.repo_full_name = repo_full_name
        self.repo = RepoManager(repo_full_name)
    
    def solve_issue(self, issue_number: int, doc_id: int = None) -> Optional[int]:
        """Обрабатывает один issue.
        
        Args:
            issue_number: Номер issue
            doc_id: ID записи в БД (опционально)
            
        Returns:
            Номер созданного PR или None
        """
        print("=" * 60)
        print(f"📋 Processing issue #{issue_number} from {self.repo_full_name}")
        print("=" * 60)
        
        # Отмечаем как в обработке
        if doc_id:
            db.set_processing(doc_id)
        
        try:
            # Получаем issue из GitHub
            issue = self.repo.get_issue(issue_number)
            title = issue.title
            body = issue.body or ""
            issue_description = f"Title: {title}\n\nDescription:\n{body}"
            
            print(f"📌 Title: {title}")
            print("-" * 40)
            
            # 1. Клонируем/обновляем репо
            repo_path = self.repo.clone_or_pull()
            
            # 2. Создаём ветку
            branch_name = f"fix/issue-{issue_number}"
            self.repo.create_branch(branch_name)
            
            # 3. Получаем файлы
            files = self.repo.get_files()
            print(f"📁 Found {len(files)} files to analyze")
            
            # 4. Анализируем каждый файл с циклом анализ-фикс
            files_fixed = []
            
            for filepath in files:
                content = self.repo.read_file(filepath)
                if not content:
                    continue
                
                # Пропускаем слишком большие файлы
                if len(content) > 50000:
                    print(f"⏭️ Skipping {filepath.name} (too large)")
                    continue
                
                relative_path = filepath.relative_to(repo_path)
                print(f"\n📄 Analyzing: {relative_path}")
                
                # Цикл анализ-фикс (до MAX_FIX_ITERATIONS раз)
                current_content = content
                file_changed = False
                
                for iteration in range(MAX_FIX_ITERATIONS):
                    result = ai_client.analyze_file(
                        filepath=filepath,
                        file_content=current_content,
                        issue_description=issue_description
                    )
                    
                    if result.issue_found and result.code_correction:
                        print(f"  [{iteration + 1}/{MAX_FIX_ITERATIONS}] 🔧 Issue found, applying fix...")
                        print(f"  💡 {result.explanation[:100]}...")
                        current_content = result.code_correction
                        file_changed = True
                    else:
                        if iteration > 0:
                            print(f"  ✅ Fix verified after {iteration} iteration(s)")
                        else:
                            print(f"  ✓ No issues in this file")
                        break
                
                # Если контент изменился, записываем
                if file_changed and current_content != content:
                    self.repo.write_file(filepath, current_content)
                    files_fixed.append(str(relative_path))
            
            # 5. Если есть изменения, коммитим и создаём PR
            if files_fixed:
                print("-" * 40)
                print(f"📝 Fixed {len(files_fixed)} file(s):")
                for f in files_fixed:
                    print(f"  - {f}")
                
                # Коммит
                commit_msg = f"fix: resolve issue #{issue_number}\n\n{title}"
                self.repo.commit(commit_msg)
                
                # Push
                self.repo.push(branch_name)
                
                # Создаём PR
                pr_body = f"""## Fixes #{issue_number}\n\n### Changes\nThis PR automatically fixes the issue described in #{issue_number}.\n\n### Modified files\n{chr(10).join(f"- `{f}`" for f in files_fixed)}\n\n### Issue Description\n> {title}\n> \n> {body[:500] if body else 'No description'}\n\n---\n🤖 Generated by Coding Agent
"""
                pr_number = self.repo.create_pull_request(
                    title=f"Fix #{issue_number}: {title}",
                    body=pr_body,
                    head=branch_name
                )
                
                # Добавляем комментарий к issue
                try:
                    self.repo.add_comment_to_issue(
                        issue_number,
                        f"🤖 I've created PR #{pr_number} to fix this issue.\n\n"
                        f"Modified files:\n" + 
                        "\n".join(f"- `{f}`" for f in files_fixed)
                    )
                except Exception as e:
                    print(f"⚠️ Failed to add comment: {e}")
                
                # Отмечаем успех в БД
                if doc_id:
                    db.set_completed(doc_id, pr_number)
                
                print("=" * 60)
                print(f"✅ Created PR #{pr_number} for issue #{issue_number}")
                print("=" * 60)
                
                # Cleanup local repo
                self.repo.cleanup()
                
                return pr_number
            else:
                print("⚠️ No fixes needed for this issue")
                
                # Добавляем комментарий
                try:
                    self.repo.add_comment_to_issue(
                        issue_number,
                        "🤖 I analyzed the codebase but couldn't find any code changes needed for this issue.\n\n"
                        "This might mean:\n"
                        "- The issue is already fixed\n"
                        "- The issue requires manual intervention\n"
                        "- More context is needed in the issue description"
                    )
                except Exception as e:
                    print(f"⚠️ Failed to add comment: {e}")
                
                if doc_id:
                    db.set_failed(doc_id, "No fixes found")
                
                # Cleanup local repo
                self.repo.cleanup()
                
                return None
                
        except Exception as e:
            print(f"❌ Error processing issue: {e}")
            if doc_id:
                db.set_failed(doc_id, str(e))
            # Cleanup on error too
            try:
                self.repo.cleanup()
            except:
                pass
            raise
    
    def fix_from_review(self, pr_number: int, review_comments: str) -> bool:
        """Исправляет код на основе review комментариев.
        
        Args:
            pr_number: Номер PR
            review_comments: Комментарии ревьюера
            
        Returns:
            True если были внесены изменения
        """
        print(f"🔄 Fixing PR #{pr_number} based on review...")
        
        # TODO: Implement fix from review
        # 1. Получить файлы из PR
        # 2. Проанализировать комментарии
        # 3. Применить исправления
        # 4. Push новый коммит
        
        return False


def process_issue_from_db(issue_data: dict) -> Optional[int]:
    """Обрабатывает issue из БД.
    
    Args:
        issue_data: Данные issue из БД
        
    Returns:
        Номер PR или None
    """
    doc_id = issue_data.get('doc_id')
    repo = issue_data.get('repo')
    issue_number = issue_data.get('issue_number')
    
    solver = IssueSolver(repo)
    return solver.solve_issue(issue_number, doc_id)


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python issue_solver.py <owner/repo> <issue_number>")
        print("\nExample:")
        print("  python issue_solver.py myuser/myrepo 1")
        sys.exit(1)
    
    repo_full_name = sys.argv[1]
    issue_number = int(sys.argv[2])
    
    solver = IssueSolver(repo_full_name)
    pr_number = solver.solve_issue(issue_number)
    
    if pr_number:
        print(f"\n🎉 Successfully created PR #{pr_number}")
    else:
        print("\n⚠️ No changes were made")


if __name__ == "__main__":
    main()