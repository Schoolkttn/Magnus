#!/usr/bin/env python3
import json
import time
import os
from pathlib import Path

class VectorWriter:
    def __init__(self, output_file):
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _atomic_write(self, data):
        """Helper method to write data atomically to the JSON file
        
        Args:
            data: Dictionary to write as JSON
        """
        # Write atomically to prevent reading corrupted data
        temp_file = self.output_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        os.chmod(temp_file, 0o777)
        # Atomic rename
        temp_file.replace(self.output_file)
    
    def write_vector(self, x, y):
        """Write a 2D vector to JSON file"""
        data = {
            "vector": {
                "x": x,
                "y": y
            },
            "timestamp": time.time()
        }
        self._atomic_write(data)
    
    def write_vectors(self, vectors):
        """Write multiple 2D vectors to JSON file
        
        Args:
            vectors: List of dictionaries with 'x', 'y', 'name', and optionally other metadata
        """
        data = {
            "vectors": vectors,
            "timestamp": time.time()
        }
        self._atomic_write(data)
    
    def write_empty(self):
        self._atomic_write([{}])
