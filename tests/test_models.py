import os
import pytest
from taxotagger import ProjectConfig
from taxotagger.models import ModelFactory
from taxotagger.models import MycoAIBERTEmbedModel
from taxotagger.models import MycoAICNNEmbedModel
from . import DATA_DIR


if os.getenv("CI"):
    pytest.skip("Skipping tests in this file on CI environment", allow_module_level=True)


@pytest.fixture
def config():
    return ProjectConfig(mycoai_home=str(DATA_DIR))


def test_get_model_mycoai_cnn(config):
    model = ModelFactory.get_model("MycoAI-CNN", config)
    assert isinstance(model, MycoAICNNEmbedModel)


def test_get_model_mycoai_bert(config):
    model = ModelFactory.get_model("MycoAI-BERT", config)
    assert isinstance(model, MycoAIBERTEmbedModel)


def test_get_model_invalid(config):
    with pytest.raises(ValueError, match="Invalid model id"):
        ModelFactory.get_model("InvalidModel", config)
