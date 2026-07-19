"""External safety detector integration notes.

No guard adapter is implemented in this repository. Use the upstream detector
models or repositories directly, then pass their exported summary to
`stego_cli.py guard-reduction` if ASR reduction is needed.
"""

from .registry import DETECTOR_REFERENCES, detector_references

__all__ = ["DETECTOR_REFERENCES", "detector_references"]
