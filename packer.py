from transformers import AutoModelWithLMHead, AutoTokenizer
from service import SummarizerService

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

pack_summarizer()