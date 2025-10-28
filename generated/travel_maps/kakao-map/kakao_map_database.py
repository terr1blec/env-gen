def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the existing database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    
    Args:
        updates: Dictionary containing updates to merge into the database
        database_path: Path to the database JSON file. If None, uses recommended location
        
    Returns:
        Updated database dictionary
        
    Raises:
        FileNotFoundError: If database file doesn't exist
        ValueError: If updates are incompatible with DATA CONTRACT
    """
    if database_path is None:
        # Use recommended path
        database_path = Path(__file__).parent / "kakao_map_database.json"
    
    # Load existing database
    if not Path(database_path).exists():
        raise FileNotFoundError(f"Database file not found: {database_path}")
    
    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Validate existing database structure
    if not validate_database_structure(database):
        raise ValueError("Existing database structure is invalid")
    
    # Validate and merge updates
    if "places" in updates:
        if not isinstance(updates["places"], list):
            raise ValueError("Updates 'places' must be a list")
        
        # Validate each place in updates
        for place in updates["places"]:
            if not isinstance(place, dict):
                raise ValueError("Each place in updates must be a dictionary")
            
            required_fields = ["id", "name", "location", "type", "description", "rating", "price_range", "tags", "coordinates"]
            for field in required_fields:
                if field not in place:
                    raise ValueError(f"Place missing required field: {field}")
            
            # Validate coordinates structure
            if not isinstance(place["coordinates"], dict) or "latitude" not in place["coordinates"] or "longitude" not in place["coordinates"]:
                raise ValueError("Place coordinates must contain 'latitude' and 'longitude'")
        
        # Merge places (append new ones, update existing ones by id)
        existing_places_by_id = {place["id"]: place for place in database.get("places", [])}
        
        for updated_place in updates["places"]:
            existing_places_by_id[updated_place["id"]] = updated_place
        
        database["places"] = list(existing_places_by_id.values())
    
    # Save updated database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    return database


def main():
    """Generate the database and save it to JSON."""
    # Ensure output directory exists
    output_dir = Path(__file__).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate database
    database = generate_kakao_map_database(seed=42, place_count=80)
    
    # Validate the generated database
    if not validate_database_structure(database):
        raise ValueError("Generated database structure is invalid")
    
    # Check for duplicate names
    names = [place["name"] for place in database["places"]]
    unique_names = set(names)
    if len(names) != len(unique_names):
        print(f"Warning: Found {len(names) - len(unique_names)} duplicate place names")
    
    # Save to JSON
    output_path = output_dir / "kakao_map_database.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"Database generated with {len(database['places'])} places")
    print(f"All place names are unique: {len(names) == len(unique_names)}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()