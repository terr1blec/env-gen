"""Script to generate the Google Calendar dataset JSON file."""

from google_calendar_dataset import generate_dataset

if __name__ == "__main__":
    # Generate and save dataset
    dataset = generate_dataset(
        calendar_count=3,
        event_count=15,  # Extra events for testing
        seed=42,  # Fixed seed for deterministic output
        output_path="google_calendar_dataset.json"
    )
    
    print(f"Generated dataset with {len(dataset['calendars'])} calendars and {len(dataset['events'])} events")
    print(f"Saved to: google_calendar_dataset.json")