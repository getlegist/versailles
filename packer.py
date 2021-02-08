import sys
from transformers import (
    AutoModelWithLMHead,
    AutoTokenizer,
    AutoModelForTokenClassification
)
from service import SummarizerService, NERService

def pack_summarizer():
    svc = SummarizerService()
    model_name = "sshleifer/distilbart-cnn-12-6"
    model = AutoModelWithLMHead.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    artifact = {
        "model": model,
        "tokenizer": tokenizer
    }
    svc.pack("model", artifact)
    print(f"Summarizer service packed: {svc.save()}")

def pack_ner():
    svc = NERService()
    model_name = "dbmdz/bert-large-cased-finetuned-conll03-english"
    tokenizer_name = "bert-base-cased"
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

    artifact = {
        "model": model,
        "tokenizer": tokenizer
    }
    svc.pack("model", artifact)
    print(f"NER service packed: {svc.save()}")

if __name__ == "__main__":
    args = sys.argv[1:]

    print(f"Parsed services to pack: {', '.join(args)}")

    if "summarizer" in args:
        print("Packing Summarizer service...")
        pack_summarizer()
    if "ner" in args:
        print("Packing NER service...")
        pack_ner()
