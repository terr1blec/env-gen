

def generate_database(seed: int = 42) -> Dict[str, Any]:
    """
    Generate the national parks database with the given seed.
    
    Args:
        seed: Random seed for deterministic generation
        
    Returns:
        Complete database dictionary following DATA CONTRACT
    """
    generator = NationalParksDatabaseGenerator(seed=seed)
    return generator.generate_database()


def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    
    Args:
        updates: Dictionary with updates to apply
        database_path: Path to database JSON file. If None, uses recommended location.
        
    Returns:
        Updated database dictionary
        
    Raises:
        FileNotFoundError: If database file doesn't exist
        ValueError: If updates violate DATA CONTRACT
    """
    if database_path is None:
        database_path = "generated/travel_maps/national-parks-information-server/national_parks_information_server_database.json"
    
    # Load existing database
    if not Path(database_path).exists():
        raise FileNotFoundError(f"Database file not found: {database_path}")
    
    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Validate updates against DATA CONTRACT
    required_keys = {"parks", "alerts", "visitor_centers", "campgrounds", "events"}
    update_keys = set(updates.keys())
    
    if not update_keys.issubset(required_keys):
        invalid_keys = update_keys - required_keys
        raise ValueError(f"Invalid update keys: {invalid_keys}. Must be one of: {required_keys}")
    
    # Apply updates (extend lists, update dictionaries by key)
    for key in update_keys:
        if key in database and isinstance(database[key], list) and isinstance(updates[key], list):
            # For arrays, extend with new items
            database[key].extend(updates[key])
        elif key in database and isinstance(database[key], dict) and isinstance(updates[key], dict):
            # For dictionaries, update by merging
            database[key].update(updates[key])
        else:
            # Replace if types don't match or key doesn't exist
            database[key] = updates[key]
    
    # Save updated database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    return database


if __name__ == "__main__":
    """Generate and save the database when run as a script."""
    import sys
    
    # Parse command line arguments
    seed = 42
    if len(sys.argv) > 1:
        try:
            seed = int(sys.argv[1])
        except ValueError:
            print(f"Warning: Invalid seed '{sys.argv[1]}', using default seed 42")
    
    # Generate database
    database = generate_database(seed=seed)
    
    # Save to recommended path
    output_path = "generated/travel_maps/national-parks-information-server/national_parks_information_server_database.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    stats = {key: len(value) for key, value in database.items()}
    print(f"Database generated with seed {seed}")
    print(f"Saved to: {output_path}")
    print("Statistics:")
    for key, count in stats.items():
        print(f"  {key}: {count}")
    
    # Verify balanced distribution
    park_codes = [park["parkCode"] for park in database["parks"]]
    for key in ["alerts", "visitor_centers", "campgrounds", "events"]:
        counts = {}
        for item in database[key]:
            park_code = item["parkCode"]
            counts[park_code] = counts.get(park_code, 0) + 1
        print(f"\n{key} distribution:")
        for park_code in park_codes:
            print(f"  {park_code}: {counts.get(park_code, 0)}")