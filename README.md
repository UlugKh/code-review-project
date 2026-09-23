# Code Review Research

This project studies how traditional machine-learning models and large language models can support software code review. It uses GitHub pull-request data to examine merge prediction and review-comment generation for both human-written and AI-generated code.

The reports cover four stages:

- collecting and analyzing pull-request and review data;
- predicting whether human-written pull requests will be merged with SVM and Random Forest models;
- evaluating LLM-based review of human-written code; and
- testing how context and prompting affect LLM review of AI-generated code.

The results show that traditional classifiers are better suited to binary merge prediction, while LLM review quality improves when models receive repository-level context and task-specific prompts.

## Repository layout

```text
data/       Collected CSV and JSON research data
notebooks/  Interactive experiment notebooks
scripts/    Collection, analysis, and experiment code
reports/    Reports, figures, and recorded experiment results
```

Python 3.14 is configured in `mise.toml`. The scripts use common data-science and notebook packages, including pandas, NumPy, matplotlib, scikit-learn, PyGithub, and Jupyter.