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
        
        # Atomic rename
        temp_file.replace(self.output_file)
        # Set permissions so plasmoid can read
        os.chmod(self.output_file, 0o644)
    
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
    
    def run(self, update_interval=1.0):
        """Main loop - replace with your actual vector generation logic"""
        counter = 0
        while True:
            # Example:  generate some vector data
            # Replace this with your actual vector calculation
            x = counter % 100
            y = (counter * 2) % 100
            
            self.write_vector(x, y)
            print(f"Written vector: ({x}, {y})")
            
            time.sleep(update_interval)
            counter += 1

if __name__ == "__main__": 
    # Use a location accessible to both the service and plasmoid
    output_file = os.path.expanduser("~/.local/share/vector_data/vector.json")
    
    writer = VectorWriter(output_file)
    print(f"Writing vectors to {output_file}")
    writer.run()