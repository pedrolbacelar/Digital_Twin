
import os
import shutil
from datetime import datetime
from dtwinpylib.dtwinpy.tester import Tester
import json

def save_results(exp_id):
    test=Tester(exp_id = exp_id)
    test.load_exp_setup()
    test.initiate_for_analysis()
    
    dt_name = test.name

    global folder_name
        
    #--- 1. Create folder with current date time format as name, inside "root" folder
    print(f"Generating folder for \033[32m{dt_name}\033[0m ...")
    global root_folder
    root_folder = "data_generation"
    now = datetime.now()
    folder_name = now.strftime(now.strftime("%m").lstrip("0") + "." + now.strftime("%d").lstrip("0") + ".%H.%M")
    os.makedirs(os.path.join(root_folder, folder_name))
    test.exp_db_path = f"{root_folder}/{folder_name}/databases/exp_database.db"

    

    #--- 2. Create markdown file with the same name as the folder
    print("Generating markdown file ...")
    global markdown_file
    markdown_filename = folder_name + ".md"
    markdown_file = open(os.path.join(root_folder, folder_name, markdown_filename), "w")

    #--- 3. Write data to the markdown file
    markdown_file.write("# test " + folder_name + "\n")
    markdown_file.write("## Objective \n\n")
    markdown_file.write(test.objective + "\n\n")

    #--- 4. Ask user for additional comments
    markdown_file.write("## Observations and Comments\n")
    user_input = input("\033[35m \nDo you want to add any additional comments or observations? (y/n): \033[0m")
    if user_input.lower() == "y":
        additional_comments = input("Enter your comments: ")
        markdown_file.write(additional_comments + "\n\n")
    else: markdown_file.write("## None\n")

    # #--- 5. copying the definition file
    # if dt_name == "5s_determ":
    #     print("Copying mydt.py ...")
    #     mydt_path = "mydt.py"
    # else:
    #     print(f"Copying {dt_name}.py ...")
    #     mydt_path = f"{dt_name}.py"

    # my_folder = "data_generation/" + folder_name
    # shutil.copy(mydt_path, my_folder)

    #--- 7. replacing replicator_db
    print("Creating replicated database ...")
    # Set the path to the file you want to copy and the new filename
    source_file = f"databases/{dt_name}/real_database.db"
    new_file = f"databases/{dt_name}/real_database_replicated.db"

    #-- If the new file already exists, delete it
    if os.path.isfile(new_file):
        os.remove(new_file)

    #-- Copy the source file to the new location with the new filename
    shutil.copy(source_file, new_file)


    #--- 8. Copy a models folder into the created folder and rename it to "models"
    print(f"Copying models and databases from {dt_name} ...")
    models_folder_path = f"models/{dt_name}"
    shutil.copytree(models_folder_path, os.path.join(root_folder, folder_name, "models"))

    #--- 9. Copy a databases folder into the created folder and rename it to 'databases'
    databases_folder_path = f"databases/{dt_name}"
    shutil.copytree(databases_folder_path, os.path.join(root_folder, folder_name, "databases"))
    markdown_file.close()
    
    #--- 9. replacing replicator_db
    print("Creating replicated database ...")
    # Set the path to the file you want to copy and the new filename
    source_file = f"databases/{dt_name}/real_database.db"
    new_file = f"databases/{dt_name}/real_database_replicated.db"

    #-- If the new file already exists, delete it
    if os.path.isfile(new_file):
        os.remove(new_file)

    #-- Copy the source file to the new location with the new filename
    shutil.copy(source_file, new_file)

    #--- 10. write the models into exp_database
    test.create_json_model_table()
    model_subfolder_path = f"{root_folder}/{folder_name}/models"
    models_list = os.listdir(model_subfolder_path)
    for model in models_list:
        with open(f"{model_subfolder_path}/{model}") as file:
            # Load the JSON data into a Python object
            print(f"writing '{model}' into exp_database")
            json_model = json.load(file)
            test.write_json_model(model_dict=json_model, model_name=model)

    #--- 11. calculate CT
    #-- calculate throughput and cycle time of system
    #-- find last part to exit the system
    #-- find number of parts finished
    #-- find CT of each parts finished
    #-- write to results table
    print("calculating CT (system & parts) and writing to results table ...")
    real_db_path = f"{root_folder}/{folder_name}/databases/real_database.db"
    test.run_analysis(real_db_path=real_db_path)

    #--- 12. plot some results
    #-- figures are plotted into fgures folder in the root
    test.figures_folder = f"figures/{dt_name}"
    test.plot()

    #--- 13. copy and paste the figures folder
    
    shutil.copytree(test.figures_folder, os.path.join(root_folder, folder_name, "figures"))


    #--- finally. write exp_id into the allexp_database and exp_database setup_data table if exp_id given is recent
    if exp_id == 'recent':
        print(f"Assiging the new exp_id to the 'recent' experiment in allexp_database and exp_db.")
        test.assign_exp_id(folder_name)

    print(f"\033[32m Results saved to {folder_name} \033[0m")

try:
    #--- get exp_id from user
    user_input = input(f"\033[35m \n Enter the exp_id or press 'Enter' to continue with 'recent': \033[0m")
    if user_input == "":                      
        save_results(exp_id="recent")
    else:
        save_results(exp_id=user_input)


except KeyboardInterrupt:
    markdown_file.close()
    folder_to_delete = os.path.join(root_folder, folder_name)
    if os.path.exists(folder_to_delete):
        user_input = input(f"\033[31m \nDo you want to delete the folder '{folder_name}' created? (y/n): \033[0m")
        if user_input.lower() == "y":
            shutil.rmtree(f"{root_folder}/{folder_name}")
            print(f"\033[38;5;94m {folder_name} deleted successfully.\033[0m")
            print("--- Program terminated ---")
        else:
            print(f"Folder not deleted. Possibility of empty folder ! You can verify at /{root_folder}/{folder_name}.")
            print("--- Program terminated ---")
    else:
        print("--- Program terminated ---")