.DEFAULT_GOAL := help

help: ## Show all Makefile targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

pack: ## Pack all BentoServices
	python packer.py summarizer ner categorization
docker-c: ## Containerize categorization
	bentoml containerize CategorizationService:latest -t legist/categorization:latest
docker-n: ## Containerize NER service
	bentoml containerize NERService:latest -t legist/ner:latest
docker-s: ## Containerize summarization service
	bentoml containerize SummarizerService:latest -t legist/summarization:latest
docker: docker-c docker-n docker-s ## Containerize all services
	echo "done!"

compose: ## Run all services
	docker-compose up --build