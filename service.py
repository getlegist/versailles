import bentoml
from bentoml.adapters import JsonInput
from bentoml.frameworks.transformers import TransformersModelArtifact
from bentoml.types import JsonSerializable, InferenceError, InferenceResult

@bentoml.env(pip_packages=[
    "transformers==3.1.0",
    "torch==1.6.0"
])
@bentoml.artifacts([TransformersModelArtifact("model")])
class SummarizerService(bentoml.BentoService):
    @bentoml.api(input=JsonInput(), batch=False)
    def predict(self, parsed_json: JsonSerializable):
        text = parsed_json.get("text")

        # pull model and tokenizer from preloaded artifacts
        model = self.artifacts.model.get("model")
        tokenizer = self.artifacts.model.get("tokenizer")

        # tokenize
        inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512)

        # invalidate token lengths of less than 10
        if len(inputs) < 10:
            return InferenceError(err_msg="text too short", http_status=400)

        # summarize text, top 4 results
        output = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)

        # decode most likely
        output = tokenizer.decode(output[0], skip_special_tokens=True)

        return InferenceResult(
            data=output,
            http_status=200,
            http_headers={"Content-Type": "application/json"},
        )