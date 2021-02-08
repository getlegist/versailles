# 🏛 legist/versailles
This repository contains the files and modules that do
- [x] Text summarization (DistilBART-CNN)
- [ ] Named entity recognition (BERT-Large)
- [ ] Zero-shot Categorization (BART-Large)

Stack: BentoML + HuggingFace

### Packing ML Models
```bash
$ python packer.py
Summarizer service packed: /Users/jzhao/bentoml/repository/SummarizerService/20210201215955_676FE1
```

### Running via CLI
```bash
$ bentoml run SummarizerService:latest predict --input '{"text": "..."}'
A shorter response
```

### Running Inference Server
```bash
$ bentoml serve SummarizerService:latest
[2021-02-01 22:22:18,865] INFO - Getting latest version SummarizerService:20210201221702_B4C7AA
[2021-02-01 22:22:18,866] INFO - Starting BentoML API server in development mode..
 * Serving Flask app "SummarizerService" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

$ curl -i \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{"text": "Some extended text..."}' \
  http://localhost:5000/predict

127.0.0.1 - - [01/Feb/2021 22:24:40] "POST /predict HTTP/1.1" 200 -
```

### With Docker
```bash
$ bentoml containerize SummarizerService:latest -t versailles-summarize
$ docker run -p 5000:5000 versailles-summarize:latest --workers=1 --enable-microbatch
```