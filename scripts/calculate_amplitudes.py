import json
import math
import hashlib

def calculate_phase(change_nature):
    """
    Maps a semantic description of change to a phase angle (0 to 2pi).
    Uses hashing to ensure consistent mapping for similar strings.
    """
    if not change_nature or change_nature.lower() == "none":
        return 0.0
    
    # Create a hash of the string
    hash_object = hashlib.md5(change_nature.encode())
    # Convert hex to int
    hash_int = int(hash_object.hexdigest(), 16)
    # Normalize to 0 - 2pi
    phase = (hash_int % 360) * (math.pi / 180.0)
    return phase

def main():
    try:
        with open("llm.txt", "r") as f:
            llm_data = json.load(f)
    except FileNotFoundError:
        print("llm.txt not found.")
        return

    tca_data = []

    for test_id, metrics in llm_data.items():
        relevance = metrics.get("relevance", 0.0)
        complexity = metrics.get("complexity", 0.0)
        change_nature = metrics.get("change_nature", "")

        # MAGNITUDE CALCULATION
        # We fuse relevance (external risk) and complexity (internal risk)
        # Magnitude |A| ranges from 0 to 1
        magnitude = (relevance * 0.7) + (complexity * 0.3)
        
        # PHASE CALCULATION
        # Represents the "direction" of the risk
        phase = calculate_phase(change_nature)

        tca_data.append({
            "test_id": test_id,
            "magnitude": float(f"{magnitude:.4f}"),
            "phase": float(f"{phase:.4f}"),
            "original_semantics": change_nature
        })

    # Output the complex amplitudes
    with open("tca.json", "w") as f:
        json.dump(tca_data, f, indent=4)
        
    print(f"Calculated amplitudes for {len(tca_data)} test cases.")

if __name__ == "__main__":
    main()