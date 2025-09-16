# wsgi.py
import importlib.util
import sys

# Load the .pyc file
spec = importlib.util.spec_from_file_location("script", "script.pyc")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)

# Make sure `app` is available for Gunicorn
app = getattr(script, "app")
