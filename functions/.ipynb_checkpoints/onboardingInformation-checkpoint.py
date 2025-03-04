# """
# This file contains the code to get the onboarding information and create a task in RLEF.
# """
# import os
# import sys
# from typing import List
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# from config.config import load_config

# config = load_config('../config/config.yaml')

# class OnboardingInformation:
#     def __init__(self, config):
#         self.config = config

#     def extract_objects(self, description):
#         """
#         Extracts the object names from the description.

#         Args:
#             description (str): The description of the action.

#         Returns:
#             list: A list of object names extracted from the description.
#         """
#         objects = []
#         return objects
    
#     def create_task(self, action_name:str, objects:List[str]):
#         """
#         Creates a task in RLEF using the action name and object names.
#         """
#         # TODO: Implement the task creation in RLEF.
#         pass
    
#     def confirm_information(self, action_name:str, description:str, objects:List[str], confirm:bool = False):
#         """
#         Asks the user about the information required for onboarding an action or grasp and then confirms the information.
#         Once confirmed creates a task in RLEF using the action name and object names.
#         Returns the RLEF TaskID.
        
#         Args:
#             action_name (str): The name of the action.
#             description (str): The description of the action.
#             objects (List[str]): The list of object names.
#             confirm (bool): The confirmation status of the information.
#         Returns:
#             str: The RLEF TaskID.
#         """
#         if confirm:
#             task_id = self.create_task(action_name, objects)
#             return task_id
#         else:
#             print("Onboarding information not confirmed.")
#             return None

import os
import sys
import uuid
from typing import List, Optional, Dict
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.config import load_config
from rlef.rlef_utils import RLEFManager

class OnboardingInformation:
    def __init__(self, config):
        """
        Initialize the OnboardingInformation class with configuration.
        
        Args:
            config (dict): Configuration dictionary containing RLEF settings
        """
        self.config = config
        self.rlef_config = config.get("RLEF", {})
        self.task_database = {}  # Simulated database for tasks
        self.manager = RLEFManager(self.rlef_config)

    def validate_information(self, action_name: str, description: str, objects: List[str]) -> bool:
        """
        Validates the provided information for onboarding.
        
        Args:
            action_name (str): Name of the action
            description (str): Description of the action
            objects (List[str]): List of objects involved
            
        Returns:
            bool: True if information is valid, False otherwise
        """
        if not action_name or not isinstance(action_name, str):
            return False
        if not description or not isinstance(description, str):
            return False
        if not objects or not isinstance(objects, list) or not all(isinstance(obj, str) for obj in objects):
            return False
        return True

    def confirm_information(self, action_name: str, description: str, objects: List[str], confirm: bool = False) -> Optional[str]:
        """
        Process the onboarding information and create task if confirmed.
        
        Args:
            action_name (str): Name of the action
            description (str): Description of the action
            objects (List[str]): List of objects involved
            confirm (bool): Confirmation flag
            
        Returns:
            Optional[str]: Task ID if confirmed and created successfully, None otherwise
        
        Raises:
            ValueError: If the provided information is invalid
        """
        # Validate the information
        if not self.validate_information(action_name, description, objects):
            raise ValueError("Invalid onboarding information provided")

        if not confirm:
            return None

        try:
            # Create task in RLEF
            task_id = self.manager.get_or_create_task(action_name)
            print(f"Created task for : {action_name}")
            return task_id
        except Exception as e:
            print(f"Error creating task: {str(e)}")
            raise

    def get_task_status(self, task_id: str) -> Dict:
        """
        Retrieve the status of a task from RLEF.
        
        Args:
            task_id (str): The ID of the task to check
            
        Returns:
            Dict: Task information and status
            
        Raises:
            KeyError: If task_id is not found
        """
        pass
    
    # TODO: Add actual RLEF API integration
    def _send_to_rlef_api(self, task_data: Dict):
        """
        Send task data to RLEF API.
        
        Args:
            task_data (Dict): Task information to be sent to RLEF
            
        Note:
            This is a placeholder for actual RLEF API integration
        """
        pass

if __name__ == "__main__":
    config = load_config('../config/config.yaml')
    onboarding_info = OnboardingInformation(config)

    # Example usage
    action_name = input("Enter the action name: ")
    description = input("Enter the description: ")
    objects = input("Enter the objects (comma-separated): ").split(",")

    print("\nPlease confirm the following information:")
    print(f"Action Name: {action_name}")
    print(f"Description: {description}")
    print(f"Objects: {objects}")

    confirm = input("Do you confirm the information? (yes/no): ").strip().lower() == 'yes'

    try:
        task_id = onboarding_info.confirm_information(action_name, description, objects, confirm=confirm)
        if task_id:
            print(f"Task created successfully with ID: {task_id}")
        else:
            print("Task creation not confirmed.")
    except ValueError as e:
        print(f"Validation error: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")