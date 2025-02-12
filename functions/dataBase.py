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
    Checks both the databases of Grasp and Action and returns a dictionary with the results.
    If the paths do not exist, it creates the knowledge base and the CSV files.
    """
    base_dir = db_config.get("base_dir", None)
    grasp_db = db_config.get("grasp", None)
    action_db = db_config.get("action", None)

    if base_dir is None or grasp_db is None or action_db is None:
        return None
    
    grasp_db_path = os.path.join(base_dir, grasp_db)
    action_db_path = os.path.join(base_dir, action_db)
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    

    print("-"*50,"Database Location","-"*50)
    print(Fore.GREEN + "Base directory path: " + base_dir + Style.RESET_ALL)
    print(Fore.GREEN + "Grasp database path: " + grasp_db_path + Style.RESET_ALL)
    print(Fore.GREEN + "Action database path: " + action_db_path + Style.RESET_ALL)
    
    if not os.path.exists(grasp_db_path) or not os.path.exists(action_db_path):
        print("Creating knowledge base...")
        if not os.path.exists(grasp_db_path):
            pd.DataFrame(columns=["name", "grasp_distance", "pickup_type"]).to_csv(grasp_db_path, index=False)
        if not os.path.exists(action_db_path):
            pd.DataFrame(columns=["name", "model", "num_samples"]).to_csv(action_db_path, index=False)
    
    grasp_df = pd.read_csv(grasp_db_path)
    action_df = pd.read_csv(action_db_path)
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

    if base_dir is None or grasp_db is None or action_db is None:
        return None
    
    grasp_db_path = os.path.join(base_dir, grasp_db)
    action_db_path = os.path.join(base_dir, action_db)
    
    print("-"*50,"Database Location","-"*50)
    print(Fore.GREEN + "Base directory path: " + base_dir + Style.RESET_ALL)
    print(Fore.GREEN + "Grasp database path: " + grasp_db_path + Style.RESET_ALL)
    print(Fore.GREEN + "Action database path: " + action_db_path + Style.RESET_ALL)
    
    if not os.path.exists(grasp_db_path) or not os.path.exists(action_db_path):
        return {"grasp": False, "action": False}
    
    grasp_df = pd.read_csv(grasp_db_path)
    action_df = pd.read_csv(action_db_path)
    
    grasp_exists = name in grasp_df["name"].tolist()
    action_exists = name in action_df[action_df["model"] == True]["name"].tolist()
    
    return {"name":name, "grasp": grasp_exists, "action": action_exists}

if __name__ == "__main__":
    # grasp_names, action_names = check_knowledgebase(db_config)
    # print(grasp_names)
    # print(action_names)

    print(specific_knowledge_check(db_config, "grasp_1"))
    print(specific_knowledge_check(db_config, "pouring"))