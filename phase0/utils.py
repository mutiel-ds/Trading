from numpy import floating
from logging import Logger, getLogger, basicConfig

from typing import TypeAlias

basicConfig(level="INFO")
logger: Logger = getLogger(name="phase0")

Number: TypeAlias = int | float | floating