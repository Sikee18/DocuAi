import os
import sys

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from DOCU_AI.backend.rag import build_vectorstore

print("Starting build_vectorstore test...")
try:
    build_vectorstore()
    print("Test finished successfully.")
except Exception as e:
    import traceback
    traceback.print_exc()
