import os
from taxotagger.config import ProjectConfig
from taxotagger.defaults import DEFAULT_CACHE_DIR
from taxotagger.defaults import ENV_MYCOAI_HOME


def test_default_config():
    config = ProjectConfig()
    assert config.mycoai_home == os.path.expanduser(DEFAULT_CACHE_DIR)
    assert config.device == "cpu"
    assert config.force_reload is False
    assert config.log_level == "INFO"
    assert config.log_file == ""
    assert config.log_to_console is True


def test_custom_mycoai_home():
    custom_path = "~/custom_mycoai"
    config = ProjectConfig(mycoai_home=custom_path)
    assert config.mycoai_home == custom_path


def test_custom_device():
    config = ProjectConfig(device="cuda")
    assert config.device == "cuda"


def test_force_reload():
    config = ProjectConfig(force_reload=True)
    assert config.force_reload is True


def test_log_level():
    config = ProjectConfig(log_level="DEBUG")
    assert config.log_level == "DEBUG"


def test_log_file():
    config = ProjectConfig(log_file="log.txt")
    assert config.log_file == "log.txt"


def test_log_to_console():
    config = ProjectConfig(log_to_console=False)
    assert config.log_to_console is False


def test_env_variable_override():
    custom_path = "~/env_mycoai"
    os.environ[ENV_MYCOAI_HOME] = custom_path
    config = ProjectConfig()
    assert config.mycoai_home == os.path.expanduser(custom_path)
