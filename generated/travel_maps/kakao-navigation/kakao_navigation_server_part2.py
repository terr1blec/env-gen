@mcp.tool()
def future_direction_search_by_coords(start_latitude: float, start_longitude: float, 
                                     end_latitude: float, end_longitude: float, 
                                     departure_time: str) -> Dict[str, Any]:
    """Search for future directions with traffic prediction based on departure time.

    Args:
        start_latitude (float): Starting point latitude coordinate
        start_longitude (float): Starting point longitude coordinate
        end_latitude (float): Destination latitude coordinate
        end_longitude (float): Destination longitude coordinate
        departure_time (str): Planned departure time (YYYY-MM-DD HH:MM format)

    Returns:
        result (dict): Future direction information with traffic prediction
    """
    direction = _find_future_direction_by_coords(
        start_latitude, start_longitude, end_latitude, end_longitude, departure_time
    )
    
    if direction:
        return {
            "start_address": _find_closest_address_by_coords(start_latitude, start_longitude)["address"],
            "end_address": _find_closest_address_by_coords(end_latitude, end_longitude)["address"],
            "departure_time": direction["departure_time"],
            "distance": direction["distance"],
            "duration": direction["duration"],
            "traffic_prediction": direction["traffic_prediction"]
        }
    else:
        # Try to find a regular direction as fallback
        regular_direction = _find_direction_by_coords(start_latitude, start_longitude, end_latitude, end_longitude)
        
        if regular_direction:
            return {
                "start_address": regular_direction["start_address"],
                "end_address": regular_direction["end_address"],
                "departure_time": departure_time,
                "distance": regular_direction["distance"],
                "duration": regular_direction["duration"],
                "traffic_prediction": "No specific traffic prediction available for this departure time"
            }
        else:
            start_address = _find_closest_address_by_coords(start_latitude, start_longitude)
            end_address = _find_closest_address_by_coords(end_latitude, end_longitude)
            
            return {
                "start_address": start_address["address"] if start_address else "Unknown location",
                "end_address": end_address["address"] if end_address else "Unknown location",
                "departure_time": departure_time,
                "distance": "Route not found in database",
                "duration": "Route not found in database",
                "traffic_prediction": "No route information available"
            }


@mcp.tool()
def multi_destination_direction_search(start_latitude: float, start_longitude: float, 
                                      destinations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Search for multi-destination directions starting from coordinates.

    Args:
        start_latitude (float): Starting point latitude coordinate
        start_longitude (float): Starting point longitude coordinate
        destinations (list): List of destination objects with 'latitude' and 'longitude' fields

    Returns:
        result (dict): Multi-destination route information
    """
    # Find the closest matching multi-destination route
    tolerance = 0.01
    
    for route in database["multi_destination_directions"]:
        start_coords = route["start_coords"]
        
        start_match = (abs(start_coords["latitude"] - start_latitude) < tolerance and 
                      abs(start_coords["longitude"] - start_longitude) < tolerance)
        
        # Check if destinations match (same number and similar coordinates)
        if start_match and len(route["destinations"]) == len(destinations):
            destination_match = True
            for i, dest in enumerate(destinations):
                route_dest = route["destinations"][i]
                if (abs(route_dest["coordinates"]["latitude"] - dest["latitude"]) > tolerance or
                    abs(route_dest["coordinates"]["longitude"] - dest["longitude"]) > tolerance):
                    destination_match = False
                    break
            
            if destination_match:
                return {
                    "summary": route["summary"],
                    "total_distance": route["total_distance"],
                    "total_duration": route["total_duration"],
                    "destinations": route["destinations"]
                }
    
    # Return fallback if no exact match
    start_address = _find_closest_address_by_coords(start_latitude, start_longitude)
    
    return {
        "summary": "Custom multi-destination route",
        "total_distance": "Route calculation required",
        "total_duration": "Route calculation required",
        "destinations": destinations,
        "start_address": start_address["address"] if start_address else "Unknown location"
    }


# Load database when module is imported
load_database()


if __name__ == "__main__":
    mcp.run()