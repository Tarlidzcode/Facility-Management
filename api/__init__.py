"""Aggregate API blueprint that reuses legacy routes and adds modular endpoints."""

from __future__ import annotations

import importlib.util
import pathlib
import sys


def _load_legacy_api_module():
	"""Load the legacy root-level ``api.py`` without clashing with this package."""
	if "legacy_api_routes" in sys.modules:
		return sys.modules["legacy_api_routes"]

	project_root = pathlib.Path(__file__).resolve().parent.parent
	api_path = project_root / "api.py"

	spec = importlib.util.spec_from_file_location("legacy_api_routes", api_path)
	if spec is None or spec.loader is None:
		raise ImportError(f"Unable to locate legacy API module at {api_path}")

	module = importlib.util.module_from_spec(spec)
	sys.modules["legacy_api_routes"] = module
	spec.loader.exec_module(module)
	print("INFO: Loaded legacy API routes from api.py")
	return module


_legacy_api = _load_legacy_api_module()
api_bp = _legacy_api.api_bp

# Attach supplementary route groups
from .safety import init_safety_routes
init_safety_routes(api_bp)

from .stock import stock_bp
api_bp.register_blueprint(stock_bp, url_prefix='/stock')

__all__ = ["api_bp"]