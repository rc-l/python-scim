import os
import sys
import pytest

# Ensure the scim2 package can be imported
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

