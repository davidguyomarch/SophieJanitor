# src/debug.py

from typing import Any
import numpy as np

class Debug:
    """
    Utility class for inspecting objects and analyzing vectorstore scores.
    """

    @staticmethod
    def inspect_object(obj: Any, depth: int = 1, indent: int = 0) -> None:
        """
        Inspect and print the structure of a Python object.

        Args:
            obj (Any): Object to inspect.
            depth (int): Depth of recursive inspection.
            indent (int): Internal indentation level.
        """
        prefix = " " * indent
        print(f"{prefix}Type: {type(obj)}")

        if depth <= 0:
            return

        if isinstance(obj, dict):
            print(f"{prefix}Dict with {len(obj)} keys")
            for key, value in obj.items():
                print(f"{prefix}  Key: {key}")
                Debug.inspect_object(value, depth - 1, indent + 4)

        elif isinstance(obj, (list, tuple, set)):
            print(f"{prefix}{type(obj).__name__} with {len(obj)} elements")
            if len(obj) > 0:
                print(f"{prefix}  First element:")
                Debug.inspect_object(list(obj)[0], depth - 1, indent + 4)

        elif hasattr(obj, "__dict__"):
            print(f"{prefix}Attributes:")
            for attr, value in vars(obj).items():
                print(f"{prefix}  {attr}: {type(value)}")

    @staticmethod
    def analyze_scores(results):
        """
        Analyze similarity_search_with_score output.
        """
        scores = [score for _, score in results]
        print("Min:", np.min(scores))
        print("Max:", np.max(scores))
        print("Mean:", np.mean(scores))
