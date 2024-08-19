from __future__ import annotations
import os
from pydantic import BaseModel
from pydantic import Field
from .defaults import DEFAULT_CACHE_DIR
from .defaults import ENV_MYCOAI_HOME


class ProjectConfig(BaseModel, validate_assignment=True):
    """Configuration for the project.

    Attributes:
        mycoai_home: The working directory for the project. Downloads and cache files are stored
            here. Defaults to "~/.cache/mycoai".
            You can also set the `MYCOAI_HOME` environment variable to override this, e.g.
            on Linux or macOS: `export MYCOAI_HOME="~/mycoai"`.
        device: The device to run the model on. Defaults to "cpu".
            Available options are:
                - "cpu": when no GPU is available,
                - "cuda": when NVIDIA GPUs are available, use "cuda:0" to use the first GPU
                - "mps": when Mac GPUs are available
                - and any other valid PyTorch device
            For more information, see the PyTorch documentation:
            https://pytorch.org/docs/stable/tensor_attributes.html#torch-device.
        force_reload: Whether to force reload the model. Defaults to False.

    Examples:
        # Get the default configuration
        >>> config = ProjectConfig()
        >>> print(config)

        # Set the working directory to "~/mycoai"
        >>> config = ProjectConfig(mycoai_home="~/mycoai")
        >>> print(config.mycoai_home)
    """

    mycoai_home: str = Field(
        default_factory=lambda: os.path.expanduser(os.getenv(ENV_MYCOAI_HOME, DEFAULT_CACHE_DIR)),
        min_length=1,
    )
    device: str = Field(default="cpu", min_length=1)
    force_reload: bool = Field(default=False, strict=True)
