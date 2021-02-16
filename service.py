import bentoml
import torch
import json
from bentoml.adapters import JsonInput
from bentoml.frameworks.transformers import TransformersModelArtifact
from bentoml.types import JsonSerializable, InferenceError, InferenceResult

@bentoml.env(pip_packages=[
    "transformers==4.2.1",
    "torch==1.7.1"
])
@bentoml.artifacts([TransformersModelArtifact("model")])
class VersaillesService(bentoml.BentoService):
    def get_artifacts(self):
        return self.artifacts.model.get("model"), self.artifacts.model.get("tokenizer")


class SummarizerService(VersaillesService):
    @bentoml.api(input=JsonInput(), batch=False)
    def predict(self, parsed_json: JsonSerializable):
        text = parsed_json.get("text")
        model, tokenizer = self.get_artifacts()

        # tokenize
        inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512)

        # invalidate token lengths of less than 10
        if len(inputs[0]) < 10:
            return InferenceError(err_msg="text too short", http_status=400)

        # summarize text, top 4 results
        output = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)

        # decode most likely
        output = tokenizer.decode(output[0], skip_special_tokens=True).replace(" .", ".")
        json_out = json.dumps({
            "result": output
        })
        return InferenceResult(
            data=json_out,
            http_status=200,
            http_headers={"Content-Type": "application/json"},
        )


class NERService(VersaillesService):
    label_list = [
        "O",       # Outside of a named entity
        "B-MISC",  # Beginning of a miscellaneous entity right after another miscellaneous entity
        "I-MISC",  # Miscellaneous entity
        "B-PER",   # Beginning of a person's name right after another person's name
        "I-PER",   # Person's name
        "B-ORG",   # Beginning of an organisation right after another organisation
        "I-ORG",   # Organisation
        "B-LOC",   # Beginning of a location right after another location
        "I-LOC"    # Location
    ]

    @bentoml.api(input=JsonInput(), batch=False)
    def predict(self, parsed_json: JsonSerializable):
        text = parsed_json.get("text")
        model, tokenizer = self.get_artifacts()

        # tokenize
        tokens = tokenizer.tokenize(tokenizer.decode(tokenizer.encode(text)))
        inputs = tokenizer.encode(text, return_tensors="pt")

        # invalidate token lengths of less than 10
        if len(inputs[0]) < 10:
            return InferenceError(err_msg="text too short", http_status=400)

        # get logits and argmax
        outputs = model(inputs).logits
        output = torch.argmax(outputs, dim=2)[0].numpy()

        # token fragment grouping
        res = []
        prev_decoded = 'O'
        for token, prediction in zip(tokens, output):
            decoded = self.label_list[prediction]
            if decoded != 'O':
                if decoded == prev_decoded:
                    if token.startswith('##'):
                        new_token = res[-1][0] + token[2:]
                    else:
                        new_token = res[-1][0] + ' ' + token
                    res[-1] = (new_token, decoded)
                else:
                    res.append((token, decoded))
            prev_decoded = decoded

        json_out = json.dumps({
            "result": res
        })
        return InferenceResult(
            data=json_out,
            http_status=200,
            http_headers={"Content-Type": "application/json"},
        )


class CategorizationService(VersaillesService):
    categories = [
        "environmental",
        "defence",
        "education",
        "economy",
        "legal",
        "energy",
        "healthcare",
        "indigenous",
        "technology",
        "parliament",
        "infrastructure",
        "transportation",
        "agriculture",
        "media"
    ]

    def _get_hypotheses(self):
        return [f'This example is about {label}.' for label in self.categories]

    @bentoml.api(input=JsonInput(), batch=False)
    def predict(self, parsed_json: JsonSerializable):
        text = parsed_json.get("text")
        model, tokenizer = self.get_artifacts()

        def encode(hypothesis):
            return tokenizer.encode(
                text,
                hypothesis,
                padding='longest',
                return_tensors='pt',
                truncation_strategy='only_first'
            )

        hypotheses = self._get_hypotheses()
        inputs = [encode(hypothesis) for hypothesis in hypotheses]
        stacked = torch.stack(inputs, dim=1)
        logits = model(stacked[0])[0]
        entail_contradiction_logits = logits[:, [0,2]]
        probs = entail_contradiction_logits.softmax(dim=1)[:,1]

        res = {}
        for label, prob in zip(self.categories, probs):
            res[label] = prob.item()

        json_out = json.dumps({
            "result": res
        })
        return InferenceResult(
            data=json_out,
            http_status=200,
            http_headers={"Content-Type": "application/json"},
        )