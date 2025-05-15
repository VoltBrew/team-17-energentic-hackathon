"""
This agents.py file defines an AI Agent responsible for managing feeder information.
It provides functionalities to register, retrieve, update, delete, and monitor feeders.
"""

import uuid
from typing import Dict, List, Optional, Union
from google.adk.agents import Agent
# from google.adk.tools import Tool  # Removed Tool decorator
# from google.adk.memory.persistent_memory import PersistentMemory  # Corrected import
#from google.adk.models.gemini import Gemini
import datetime
import json
import os
from zoneinfo import ZoneInfo

# Define the persistent memory - using a dictionary and file storage
# memory = PersistentMemory()
_memory_file = "feeder_memory.json"
_memory: Dict[str, dict] = {}

def _load_memory():
    """Loads memory from a file."""
    global _memory
    if os.path.exists(_memory_file):
        try:
            with open(_memory_file, "r") as f:
                _memory = json.load(f)
        except json.JSONDecodeError:
            print("Warning: Memory file was corrupted.  Starting with empty memory.")
            _memory = {}
    else:
        _memory = {}

def _save_memory():
    """Saves memory to a file."""
    global _memory
    try:
        with open(_memory_file, "w") as f:
            json.dump(_memory, f, indent=4)
    except Exception as e:
        print(f"Error saving memory to file: {e}")

# Load memory at the start
_load_memory()

# Define data structure for a feeder
class Feeder:
    """
    Represents a feeder with its attributes.
    """
    def __init__(self, feeder_id: str, name: str, location: str, configuration: Optional[Dict] = None):
        """
        Initializes a Feeder object.

        Args:
            feeder_id (str): The unique ID of the feeder.
            name (str): The name of the feeder.
            location (str): The location of the feeder.
            configuration (Optional[Dict], optional): Configuration parameters for the feeder. Defaults to None.
        """
        self.feeder_id = feeder_id
        self.name = name
        self.location = location
        self.configuration = configuration  # Added configuration

    def to_dict(self) -> Dict:
        """
        Converts the Feeder object to a dictionary.

        Returns:
            Dict[str, str]: A dictionary representation of the Feeder.
        """
        return {
            "feeder_id": self.feeder_id,
            "name": self.name,
            "location": self.location,
            "configuration": self.configuration, #Added configuration
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Feeder":
        """
        Creates a Feeder object from a dictionary.

        Args:
            data (Dict[str, str]): A dictionary containing feeder data.

        Returns:
            Feeder: A Feeder object.
        """
        return cls(
            feeder_id=data["feeder_id"],
            name=data["name"],
            location=data["location"],
            configuration=data.get("configuration"), #Added configuration
        )

# Helper Functions for interacting with memory
def _get_feeder_memory_key(feeder_id: str) -> str:
    """
    Constructs the memory key for a feeder ID.

    Args:
        feeder_id (str): The ID of the feeder.

    Returns:
        str: The memory key.
    """
    return f"feeder:{feeder_id}"

def _get_all_feeders_key() -> str:
    """
    Returns the key used to store the list of all feeder IDs.

    Returns:
        str: The key for the list of all feeder IDs.
    """
    return "all_feeders"

# Define the tools for the agent
def register_feeder(feeder_id: str, feeder_name: str, feeder_location: str, configuration: Optional[Dict[str, Union[str, int, float]]] = None) -> Dict[str, Union[str, Dict]]:
    """
    Registers a new feeder, generates a unique ID, and saves it to persistent memory.

    Args:
        feeder_id (str): The ID of the feeder to register.
        feeder_name (str): The name of the feeder.
        feeder_location (str): The location of the feeder.
        configuration (Optional[Dict], optional): Configuration parameters for the feeder. Defaults to None.

    Returns:
        Dict[str, str]: A dictionary containing the registration status with a 'status' key ('success' or 'error')
        and a 'report' key with the registration details if successful, or an 'error_message' if an error occurred.
    """
    global _memory
    memory_key = _get_feeder_memory_key(feeder_id)
    if memory_key in _memory:
        return {"status": "error", "error_message": f"Feeder ID '{feeder_id}' already exists."}

    feeder = Feeder(feeder_id, feeder_name, feeder_location, configuration)
    _memory[memory_key] = feeder.to_dict()
    _save_memory() # Save after writing to memory

    # Update the list of all feeders
    all_feeders_key = _get_all_feeders_key()
    all_feeder_ids = _memory.get(all_feeders_key)  # type: Optional[List[str]]
    if all_feeder_ids is None:
        all_feeder_ids = []
    all_feeder_ids.append(feeder_id)
    _memory[all_feeders_key] = all_feeder_ids
    _save_memory()
    return {"status": "success", "report": feeder.to_dict()}  # Include all feeder details in report



def get_registered_feeders() -> Dict[str, Union[str, List[Dict]]]:
    """
    Retrieves a list of all registered feeders from persistent memory.

    Returns:
       dict: A dictionary containing the list of registered feeders with a 'status' key ('success' or 'error') and a 'report' key with the list of feeders if successful, or an 'error_message' if an error occurred.
    """
    global _memory
    all_feeders_key = _get_all_feeders_key()
    all_feeder_ids = _memory.get(all_feeders_key)  # type: Optional[List[str]]
    if all_feeder_ids is None:
        return {"status": "success", "report": []}  # Return empty list if no feeders are registered

    feeders = []
    for feeder_id in all_feeder_ids:
        memory_key = _get_feeder_memory_key(feeder_id)
        feeder_data = _memory.get(memory_key)
        if feeder_data:  # Check if feeder_data is not None
            feeders.append(Feeder.from_dict(feeder_data).to_dict())
    return {"status": "success", "report": feeders}



def get_feeder_health(feeder_id: str) -> Dict[str, Union[str, Dict]]:
    """
    Retrieves the health status of a specified feeder.

    Args:
        feeder_id (str): The ID of the feeder to check.

    Returns:
        dict: A dictionary containing the health status of the feeder with a 'status' key ('success' or 'error')
        and a 'report' key with the health details if successful, or an 'error_message' if an error occurred.
    """
    global _memory
    memory_key = _get_feeder_memory_key(feeder_id)
    if memory_key not in _memory:
        return {"status": "error", "error_message": f"Feeder ID '{feeder_id}' not found."}

    # In a real-world scenario, this would involve checking the actual health
    # of the feeder, perhaps by querying a database or an API.  For this
    # example, we'll just return a simulated status.
    health_status = "Operational and healthy."  # Placeholder
    return {"status": "success", "report": health_status}



def get_feeder_alerts(feeder_id: str) -> Dict[str, Union[str, List[Dict[str, str]]]]:
    """
    Retrieves the alerts for a specified feeder.

    Args:
        feeder_id (str): The ID of the feeder to check.

    Returns:
        dict: A dictionary containing the alerts for the feeder with a 'status' key ('success' or 'error') and
        a 'report' key with the alert details if successful, or an 'error_message' if an error occurred.
    """
    global _memory
    memory_key = _get_feeder_memory_key(feeder_id)
    if memory_key not in _memory:
        return {"status": "error", "error_message": f"Feeder ID '{feeder_id}' not found."}

    alerts_key = f"alerts:{feeder_id}"
    alerts = _memory.get(alerts_key)  # type: Optional[List[Dict[str, str]]]
    if alerts is None:
        alerts = []  # Return an empty list, not None
    return {"status": "success", "report": alerts}



def get_weather(city: str) -> Dict[str, str]:
    """Retrieves the current weather report for a specified city.

    Returns:
        dict: A dictionary containing the weather information with a 'status' key ('success' or 'error') and a 'report' key with the weather details if successful, or an 'error_message' if an error occurred.
    """
    if city.lower() == "new york":
        return {"status": "success",
                "report": "The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}
    else:
        return {"status": "error",
                "error_message": f"Weather information for '{city}' is not available."}



def get_current_time(city: str) -> Dict[str, str]:
    """Returns the current time in a specified city.

    Args:
        dict: A dictionary containing the current time for a specified city information with a 'status' key ('success' or 'error') and a 'report' key with the current time details in a city if successful, or an 'error_message' if an error occurred.
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {"status": "error",
                "error_message": f"Sorry, I don't have timezone information for {city}."}

    tz = ZoneInfo(tz_identifier)
    now = datetime.now(tz)
    return {"status": "success",
            "report": f"""The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}"""}

# Create the agent
root_agent = Agent(
    name="agent_grid_watch",
    model="gemini-2.0-flash",
    description="Agent to monitor and manage grid feeders.",
    instruction="You are a root agent responsible for managing feeders in a system. Your primary goal is to ensure the health, availability, and proper operation of these feeders. You are designed to be proactive and ensure data is saved persistently.\n\nCore Responsibilities:\n1.  Feeder Registration: Ensure all feeders are properly registered and their data is automatically saved.\n2.  Feeder Inventory: Maintain an accurate and up-to-date inventory of all registered feeders.\n3.  Health Monitoring: Continuously monitor the health status of each feeder.\n4.  Health Forecasting: Predict potential future health issues or degradation of feeders.\n5.  Alerting: Generate timely and informative alerts when feeder health deviates from expected parameters or when potential issues are predicted.\n6.  Coordination: Coordinate with other agents or systems as necessary to resolve feeder-related issues.\n7.  Reporting: Provide summaries of feeder status, health, and any alerts or actions taken.\n8.  Data Persistence: Ensure that feeder data (registration details, configuration) is saved persistently.  This is a core function of the agent.\n\nAvailable Tools:\n* register_feeder: Registers a new feeder with the system.\n    * Description: Adds a new feeder to the system's inventory and saves the feeder's data.\n    * Input:\n        * feeder_id (string, required): Unique identifier for the feeder.\n        * feeder_type (string, required): Type of feeder.\n        * configuration (dictionary, optional): Configuration parameters for the feeder.\n    * Output:\n        * Success: Returns a success message with the feeder ID.\n        * Failure: Returns an error message.\n* get_all_registered_feeders: Retrieves a list of all registered feeders.\n    * Description: Retrieves a list of all feeders currently registered in the system.\n    * Input: None\n    * Output:\n        * Success: Returns a list of dictionaries, where each dictionary represents a feeder and contains its details (feeder_id, feeder_type, configuration, etc.).\n        * Failure: Returns an error message.\n* check_feeder_health: Checks the current health status of a specific feeder.\n    * Description: Retrieves the current health status of a specified feeder.\n    * Input:\n        * feeder_id (string, required): The ID of the feeder to check.\n    * Output:\n        * Success: Returns a dictionary containing the feeder's health status (e.g., 'healthy', 'warning', 'critical') and any relevant metrics.\n        * Failure: Returns an error message, such as 'Feeder not found' or 'Unable to retrieve health status.'\n* forecast_feeder_health: Forecasts the future health status of a specific feeder.\n    * Description: Predicts the future health of a feeder based on historical data, current status, and other relevant factors.\n    * Input:\n        * feeder_id (string, required): The ID of the feeder to forecast.\n        * time_horizon (string, optional): The time period for the forecast (e.g., '1h', '24h', '7d'). If not provided, use a reasonable default.\n    * Output:\n        * Success: Returns a dictionary containing the predicted health status for the specified time horizon, including a confidence level or probability.\n        * Failure: Returns an error message, such as 'Unable to forecast health' or 'Invalid time horizon.'\n* generate_alerts: Generates alerts based on feeder health status or forecasts.\n    * Description: Creates alerts when a feeder's health is critical, deteriorating, or predicted to degrade.\n    * Input:\n        * alert_level (string, required): The severity of the alert ('info', 'warning', 'critical').\n        * message (string, required): A descriptive message about the alert.\n        * feeder_id (string, optional): The ID of the feeder associated with the alert.\n    * Output:\n        * Success: Returns a success message with the alert details.\n        * Failure: Returns an error message.\n",
    tools=[get_feeder_health, get_feeder_alerts, register_feeder, get_registered_feeders, get_weather, get_current_time] #removed the tool decorator
)
