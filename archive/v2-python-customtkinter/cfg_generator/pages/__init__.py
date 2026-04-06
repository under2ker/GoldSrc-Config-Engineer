"""
Page mixins for the main App class.

Each mixin contains _p_*() page builders and their helper methods,
extracted from gui.py to keep file sizes manageable.
"""

from cfg_generator.pages.crosshair_page import CrosshairPageMixin
from cfg_generator.pages.deploy_page import DeployPageMixin
from cfg_generator.pages.preview_page import PreviewPageMixin
from cfg_generator.pages.sensitivity_page import SensitivityPageMixin

__all__ = [
    "CrosshairPageMixin",
    "DeployPageMixin",
    "PreviewPageMixin",
    "SensitivityPageMixin",
]
