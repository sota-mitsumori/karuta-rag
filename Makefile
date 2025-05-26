.PHONY: install run index test
install:
	pip install -r requirements.txt

index:
	python -m src.indexer

run:
	python -m src.qa_chain

test:
	pytest --maxfail=1 --disable-warnings -q
