source := ${wildcard ./arxiv/*.py}
tests := ${wildcard tests/*.py}

.PHONY: run lint deploy

lint: $(source) $(tests)
	flake8 . --count --max-complexity=10 --statistics

run:
	functions-framework --source "main.py" --target "main"

deploy:
	gcloud functions deploy "github-issue-pr-feeds" --entry-point "main" --runtime "python37" --trigger-http

