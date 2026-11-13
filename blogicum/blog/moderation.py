from functools import cache

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from core.constants import TOXICITY_THRESHOLD

MODEL_NAME = 'cointegrated/rubert-tiny-toxicity'


@cache
def load_model():
    """Загрузить токенизатор и модель при первом обращении."""
    return (
        AutoTokenizer.from_pretrained(MODEL_NAME),
        AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).eval(),
    )


def get_toxicity_score(text: str) -> float:
    """Вернуть оценку токсичности от 0 до 1."""
    tokenizer, model = load_model()
    inputs = tokenizer(
        text,
        return_tensors='pt',
        truncation=True,
        padding=True,
    )

    with torch.inference_mode():
        logits = model(**inputs).logits[0]
        probabilities = torch.sigmoid(logits).cpu()

    non_toxic_probability = probabilities[0].item()
    dangerous_probability = probabilities[-1].item()

    return 1 - non_toxic_probability * (1 - dangerous_probability)


def is_toxic(text: str) -> bool:
    """Определить, достигла ли оценка заданного порога."""
    return get_toxicity_score(text) >= TOXICITY_THRESHOLD
