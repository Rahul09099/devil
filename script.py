# script.py
import importlib.util

# Load compiled .pyc
spec = importlib.util.spec_from_file_location("script", "./script.pyc")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Expose the 'app' object for Gunicorn
app = module.app
