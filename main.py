from github_service import fetch_issues


issues = fetch_issues("python", "good first issue", 10)

print("\nOPEN SOURCE PYTHON ISSUES")
print("=" * 50)

for index, issue in enumerate(issues, start=1):

    repository = issue["repository_url"].split("/repos/")[-1]

    labels = [label["name"] for label in issue["labels"]]

    print(f"\n{index}. {issue['title']}")
    print("Repository:", repository)
    print("Labels:", ", ".join(labels))
    print("URL:", issue["html_url"])

print("\nTotal issues:", len(issues))