# trainers/helpers/replicate_helpers.py
from functools import lru_cache
import os

from replicate.client import Client
from replicate.exceptions import ReplicateError
from dotenv import load_dotenv

load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
REPLICATE_MODEL = os.getenv("REPLICATE_MODEL")
REPLICATE_MODEL_VERSION = os.getenv("REPLICATE_MODEL_VERSION")


@lru_cache
def get_replicate_client():
    return Client(api_token=REPLICATE_API_TOKEN)


@lru_cache
def get_replicate_model_version():
    rep_model = get_replicate_client().models.get(REPLICATE_MODEL)
    return rep_model.versions.get(REPLICATE_MODEL_VERSION)


def generate_image(prompt, require_trigger_word=True, trigger_word="TOK"):
    if require_trigger_word and trigger_word not in prompt:
        raise Exception(f"{trigger_word} was not included in the prompt")

    input_args = {
        "prompt": prompt,
        "num_outputs": 2,
        "output_format": "jpg",
    }
    rep_version = get_replicate_model_version()
    return get_replicate_client().predictions.create(
        version=rep_version, input=input_args
    )


def list_prediction_results(
    model=REPLICATE_MODEL, version=REPLICATE_MODEL_VERSION, status=None, max_size=500
):
    preds = get_replicate_client().predictions.list()
    results = list(preds.results)
    while preds.next:
        _preds = get_replicate_client().predictions.list(preds.next)
        results += list(_preds.results)
        if len(results) > max_size:
            break
    results = [x for x in results if x.model == model and x.version == version]
    if status:
        results = [x for x in results if x.status == status]
    return results


def get_prediction_detail(prediction_id):
    try:
        return get_replicate_client().predictions.get(prediction_id), 200
    except ReplicateError:
        return None, 404
    except Exception:
        return None, 500
