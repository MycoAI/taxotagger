import pytest
from src.taxotagger.config import ProjectConfig
from src.taxotagger.taxotagger import TaxoTagger
from . import DATA_DIR


DATABASE_FASTA = str(DATA_DIR / "database.fasta")
QUERY_FASTA = str(DATA_DIR / "query.fasta")
MODEL_ID = "MycoAI-CNN"


@pytest.fixture
def config():
    return ProjectConfig(mycoai_home=str(DATA_DIR))


@pytest.fixture
def taxotagger(config):
    return TaxoTagger(config)


@pytest.mark.order(1)
def test_embed(taxotagger):
    result = taxotagger.embed(QUERY_FASTA, MODEL_ID)

    assert "phylum" in result
    assert len(result["phylum"]) == 2
    assert result["phylum"][0]["id"] == "KY106088"
    assert result["phylum"][1]["id"] == "KY106087"


@pytest.mark.order(3)
def test_search(taxotagger):
    result = taxotagger.search(QUERY_FASTA, model_id=MODEL_ID, limit=3)

    assert "phylum" in result
    assert len(result["phylum"]) == 2  # 2 sequences
    assert len(result["phylum"][0]) == 3  # 3 hits
    assert result["phylum"][0][0]["id"] == "KY106088"  # first hit for the first sequence


@pytest.mark.order(2)
def test_create_db(taxotagger):
    taxotagger.create_db(DATABASE_FASTA, MODEL_ID)
    expected_output = DATA_DIR / "MycoAI-CNN.db"
    assert expected_output.exists()
