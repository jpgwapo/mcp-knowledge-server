import subprocess
import json

# Test the search function directly
import sys
sys.path.insert(0, '.')

from server import search_knowledge, list_documents, get_document

print("=== LIST DOCUMENTS ===")
print(list_documents())

print("\n=== SEARCH: irrigation ===")
print(search_knowledge("irrigation"))

print("\n=== GET DOCUMENT: equipment.md ===")
print(get_document("equipment.md"))
