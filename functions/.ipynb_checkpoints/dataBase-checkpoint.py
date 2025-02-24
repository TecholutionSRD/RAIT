# """
# This file contains the functions to check the database and manipulate it.
# # TODO : For now the database is a csv file, but it should be a MongoDB database.
# """
# from colorama import Fore, Style
# import pandas as pd
# import os
# import sys
# from dotenv import load_dotenv

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
# from config.config import load_config

# config = load_config("../config/config.yaml")
# db_config = config.get("DataBase", {})

# #--------------------------------------------------------------#
# def check_knowledgebase(db_config):
#     """
#     Checks both the databases of Grasp and Action and returns a dictionary with the results.
#     If the paths do not exist, it creates the knowledge base and the CSV files.
#     """
#     base_dir = db_config.get("base_dir", None)
#     grasp_db = db_config.get("grasp", None)
#     action_db = db_config.get("action", None)

#     if base_dir is None or grasp_db is None or action_db is None:
#         return None
    
#     grasp_db_path = os.path.join(base_dir, grasp_db)
#     action_db_path = os.path.join(base_dir, action_db)
    
#     if not os.path.exists(base_dir):
#         os.makedirs(base_dir)
    

#     print("-"*50,"Database Location","-"*50)
#     print(Fore.GREEN + "Base directory path: " + base_dir + Style.RESET_ALL)
#     print(Fore.GREEN + "Grasp database path: " + grasp_db_path + Style.RESET_ALL)
#     print(Fore.GREEN + "Action database path: " + action_db_path + Style.RESET_ALL)
    
#     if not os.path.exists(grasp_db_path) or not os.path.exists(action_db_path):
#         print("Creating knowledge base...")
#         if not os.path.exists(grasp_db_path):
#             pd.DataFrame(columns=["name", "grasp_distance", "pickup_type"]).to_csv(grasp_db_path, index=False)
#         if not os.path.exists(action_db_path):
#             pd.DataFrame(columns=["name", "model", "num_samples"]).to_csv(action_db_path, index=False)
    
#     grasp_df = pd.read_csv(grasp_db_path)
#     action_df = pd.read_csv(action_db_path)
#     grasp_names = grasp_df["name"].tolist()
#     action_names = action_df[action_df["model"] == True]["name"].tolist()
    
#     return grasp_names, action_names

# #--------------------------------------------------------------#
# def specific_knowledge_check(db_config, name):
#     """
#     Checks if the specified name exists in either the grasp or action databases.
#     Returns a dictionary with the results.
#     """
#     base_dir = db_config.get("base_dir", None)
#     grasp_db = db_config.get("grasp", None)
#     action_db = db_config.get("action", None)

#     if base_dir is None or grasp_db is None or action_db is None:
#         return None
    
#     grasp_db_path = os.path.join(base_dir, grasp_db)
#     action_db_path = os.path.join(base_dir, action_db)
    
#     print("-"*50,"Database Location","-"*50)
#     print(Fore.GREEN + "Base directory path: " + base_dir + Style.RESET_ALL)
#     print(Fore.GREEN + "Grasp database path: " + grasp_db_path + Style.RESET_ALL)
#     print(Fore.GREEN + "Action database path: " + action_db_path + Style.RESET_ALL)
    
#     if not os.path.exists(grasp_db_path) or not os.path.exists(action_db_path):
#         return {"grasp": False, "action": False}
    
#     grasp_df = pd.read_csv(grasp_db_path)
#     action_df = pd.read_csv(action_db_path)
    
#     grasp_exists = name in grasp_df["name"].tolist()
#     action_exists = name in action_df[action_df["model"] == True]["name"].tolist()
    
#     return {"name":name, "grasp": grasp_exists, "action": action_exists}

# if __name__ == "__main__":
#     # grasp_names, action_names = check_knowledgebase(db_config)
#     # print(grasp_names)
#     # print(action_names)

#     print(specific_knowledge_check(db_config, "grasp_1"))
#     print(specific_knowledge_check(db_config, "pouring"))

"""
This file contains the functions to check the database and manipulate it.
# TODO : For now the database is a csv file, but it should be a MongoDB database.
"""
from colorama import Fore, Style
import pandas as pd
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from config.config import load_config

config = load_config("../config/config.yaml")
db_config = config.get("DataBase", {})

#--------------------------------------------------------------#
def check_knowledgebase(db_config):
    """
    Checks the databases (grasping_data, action_data, action_objects) and returns a dictionary with the results.
    If the paths do not exist, it creates the knowledge base and the CSV files.
    """
    base_dir = db_config.get("base_dir", None)
    grasp_db = db_config.get("grasp", None)  # Will be grasping_data.csv
    action_db = db_config.get("action", None)  # Will be action_data.csv
    action_objects_db = db_config.get("action_objects", "action_objects.csv")  # New file
    
    if base_dir is None or grasp_db is None or action_db is None:
        return None
    
    grasp_db_path = os.path.join(base_dir, grasp_db)
    action_db_path = os.path.join(base_dir, action_db)
    action_objects_db_path = os.path.join(base_dir, action_objects_db)
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    print("-"*50,"Database Location","-"*50)
    print(Fore.GREEN + "Base directory path: " + base_dir + Style.RESET_ALL)
    print(Fore.GREEN + "Grasp database path: " + grasp_db_path + Style.RESET_ALL)
    print(Fore.GREEN + "Action database path: " + action_db_path + Style.RESET_ALL)
    print(Fore.GREEN + "Action objects database path: " + action_objects_db_path + Style.RESET_ALL)
    
    # Create database files if they don't exist
    if not os.path.exists(grasp_db_path):
        pd.DataFrame(columns=["name", "grasp_distance", "pickup_mode"]).to_csv(grasp_db_path, index=False)
    
    if not os.path.exists(action_db_path):
        pd.DataFrame(columns=["id", "name", "samples", "model"]).to_csv(action_db_path, index=False)
    
    if not os.path.exists(action_objects_db_path):
        pd.DataFrame(columns=["action_id", "object_name"]).to_csv(action_objects_db_path, index=False)
    
    grasp_df = pd.read_csv(grasp_db_path)
    action_df = pd.read_csv(action_db_path)
    action_objects_df = pd.read_csv(action_objects_db_path)
    
    grasp_names = grasp_df["name"].tolist()
    action_names = action_df[action_df["model"] == True]["name"].tolist()
    
    return grasp_names, action_names

#--------------------------------------------------------------#
def specific_knowledge_check(db_config, name):
    """
    Checks if the specified name exists in either the grasp or action databases.
    Returns a dictionary with the results.
    """
    base_dir = db_config.get("base_dir", None)
    grasp_db = db_config.get("grasp", None)
    action_db = db_config.get("action", None)
    action_objects_db = db_config.get("action_objects", "action_objects.csv")
    
    if base_dir is None or grasp_db is None or action_db is None:
        return None
    
    grasp_db_path = os.path.join(base_dir, grasp_db)
    action_db_path = os.path.join(base_dir, action_db)
    action_objects_db_path = os.path.join(base_dir, action_objects_db)
    
    if not os.path.exists(grasp_db_path) or not os.path.exists(action_db_path):
        return {"grasp": False, "action": False, "object_in_action": False}
    
    grasp_df = pd.read_csv(grasp_db_path)
    action_df = pd.read_csv(action_db_path)
    
    grasp_exists = name in grasp_df["name"].tolist()
    action_exists = name in action_df[action_df["model"] == True]["name"].tolist()
    
    # Additional check if this is an object used in actions
    if os.path.exists(action_objects_db_path):
        action_objects_df = pd.read_csv(action_objects_db_path)
        object_in_action = name in action_objects_df["object_name"].tolist()
    else:
        object_in_action = False
    
    return {"name": name, "grasp": grasp_exists, "action": action_exists, "object_in_action": object_in_action}
#--------------------------------------------------------------#
def get_action_objects(db_config, action_name):
    """
    Returns a list of objects associated with a specific action.
    """
    base_dir = db_config.get("base_dir", None)
    action_db = db_config.get("action", None)
    action_objects_db = db_config.get("action_objects", "action_objects.csv")
    
    if base_dir is None or action_db is None:
        return []
    
    action_db_path = os.path.join(base_dir, action_db)
    action_objects_db_path = os.path.join(base_dir, action_objects_db)
    
    if not os.path.exists(action_db_path) or not os.path.exists(action_objects_db_path):
        return []
    
    action_df = pd.read_csv(action_db_path)
    action_objects_df = pd.read_csv(action_objects_db_path)
    
    # Get the action ID for the given action name
    action_row = action_df[action_df["name"] == action_name]
    if action_row.empty:
        return []
    
    action_id = action_row.iloc[0]["id"]
    
    # Get objects associated with this action ID
    objects = action_objects_df[action_objects_df["action_id"] == action_id]["object_name"].tolist()
    
    return objects

#--------------------------------------------------------------#
def add_grasp_data(db_config, name, grasp_distance, pickup_mode):
    """
    Adds a new grasp entry to the grasp database.
    """
    base_dir = db_config.get("base_dir", None)
    grasp_db = db_config.get("grasp", None)
    
    if base_dir is None or grasp_db is None:
        return False
    
    grasp_db_path = os.path.join(base_dir, grasp_db)
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Create the file with headers if it doesn't exist
    if not os.path.exists(grasp_db_path):
        pd.DataFrame(columns=["name", "grasp_distance", "pickup_mode"]).to_csv(grasp_db_path, index=False)
    
    grasp_df = pd.read_csv(grasp_db_path)
    
    # Check if entry already exists
    if name in grasp_df["name"].tolist():
        print(f"Grasp entry for '{name}' already exists.")
        return False
    
    # Add new entry
    new_row = pd.DataFrame([[name, grasp_distance, pickup_mode]], 
                          columns=["name", "grasp_distance", "pickup_mode"])
    grasp_df = pd.concat([grasp_df, new_row], ignore_index=True)
    grasp_df.to_csv(grasp_db_path, index=False)
    
    print(f"Added grasp entry for '{name}'.")
    return True

#--------------------------------------------------------------#
def add_action_data(db_config, name, samples, model=True):
    """
    Adds a new action entry to the action database.
    Returns the ID of the new action.
    """
    base_dir = db_config.get("base_dir", None)
    action_db = db_config.get("action", None)
    
    if base_dir is None or action_db is None:
        return None
    
    action_db_path = os.path.join(base_dir, action_db)
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Create the file with headers if it doesn't exist
    if not os.path.exists(action_db_path):
        pd.DataFrame(columns=["id", "name", "samples", "model"]).to_csv(action_db_path, index=False)
    
    action_df = pd.read_csv(action_db_path)
    
    # Check if entry already exists
    if name in action_df["name"].tolist():
        print(f"Action entry for '{name}' already exists.")
        action_id = action_df[action_df["name"] == name].iloc[0]["id"]
        return action_id
    
    # Generate a new ID (max ID + 1)
    if action_df.empty:
        new_id = 1
    else:
        new_id = action_df["id"].max() + 1
    
    # Add new entry
    new_row = pd.DataFrame([[new_id, name, samples, model]], 
                          columns=["id", "name", "samples", "model"])
    action_df = pd.concat([action_df, new_row], ignore_index=True)
    action_df.to_csv(action_db_path, index=False)
    
    print(f"Added action entry for '{name}' with ID {new_id}.")
    return new_id

#--------------------------------------------------------------#
def add_action_object(db_config, action_id, object_name):
    """
    Associates an object with an action in the action_objects database.
    """
    base_dir = db_config.get("base_dir", None)
    action_objects_db = db_config.get("action_objects", "action_objects.csv")
    
    if base_dir is None:
        return False
    
    action_objects_db_path = os.path.join(base_dir, action_objects_db)
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Create the file with headers if it doesn't exist
    if not os.path.exists(action_objects_db_path):
        pd.DataFrame(columns=["action_id", "object_name"]).to_csv(action_objects_db_path, index=False)
    
    action_objects_df = pd.read_csv(action_objects_db_path)
    
    # Check if association already exists
    if ((action_objects_df["action_id"] == action_id) & 
        (action_objects_df["object_name"] == object_name)).any():
        print(f"Association between action ID {action_id} and object '{object_name}' already exists.")
        return False
    
    # Add new association
    new_row = pd.DataFrame([[action_id, object_name]], columns=["action_id", "object_name"])
    action_objects_df = pd.concat([action_objects_df, new_row], ignore_index=True)
    action_objects_df.to_csv(action_objects_db_path, index=False)
    
    print(f"Added association between action ID {action_id} and object '{object_name}'.")
    return True

if __name__ == "__main__":
    # Example usage
    grasp_names, action_names = check_knowledgebase(db_config)
    print("Grasp names:", grasp_names)
    print("Action names:", action_names)

#     # Add some sample data
    add_grasp_data(db_config, "Red Soda Can", 10.0, "HORIZONTAL")
    add_grasp_data(db_config, "Bottle", 10.0, "HORIZONTAL")
    
#     pouring_id = add_action_data(db_config, "Pouring", 20, True)
#     add_action_object(db_config, pouring_id, "Blue Cup")
#     add_action_object(db_config, pouring_id, "Red Bottle")
    
    # # Check specific objects
    # print(specific_knowledge_check(db_config, "Red Bottle"))
    # print(specific_knowledge_check(db_config, "Pouring"))
    
    # Get objects associated with an action
    # objects = get_action_objects(db_config, "Pouring")
    # print("Objects used in Pouring:", objects)