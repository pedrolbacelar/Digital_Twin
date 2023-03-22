
import os
import shutil
from datetime import datetime

def create_markdown_with_model():
    global folder_name
    print("Generating folder ...")
    # 1. Create folder with current date time format as name, inside "root" folder
    global root_folder
    root_folder = "data_generation"
    now = datetime.now()
    folder_name = now.strftime(now.strftime("%m").lstrip("0") + "." + now.strftime("%d").lstrip("0") + ".%H.%M")
    os.makedirs(os.path.join(root_folder, folder_name))

    print("Generating markdown file ...")

    # 2. Create markdown file with the same name as the folder
    global markdown_file
    markdown_filename = folder_name + ".md"
    markdown_file = open(os.path.join(root_folder, folder_name, markdown_filename), "w")

    # 3. Write data to the markdown file
    markdown_file.write("# test " + folder_name + "\n")
    markdown_file.write("## Objective\n\n")
    objective = input("\033[35m \nwhat is the test objective?\033[0m")
    markdown_file.write(objective + "\n\n")

    # 5. Ask user for additional comments
    markdown_file.write("## Observations and Comments\n")
    user_input = input("\033[35m \nDo you want to add any additional comments or observations? (y/n): \033[0m")
    if user_input.lower() == "y":
        # 6. Ask user for input and add it to the markdown file
        additional_comments = input("Enter your comments: ")
        markdown_file.write(additional_comments + "\n\n")
    else: markdown_file.write("## None\n")

    print("Copying mydt.py ...")

    mydt_path = "mydt.py"
    my_folder = "data_generation/" + folder_name
    shutil.copy(mydt_path, my_folder)


    print("Copying models and databases from 5s_determ ...")

    # 7. Copy a different folder into the created folder and rename it to "models"
    models_folder_path = "models/5s_determ"
    shutil.copytree(models_folder_path, os.path.join(root_folder, folder_name, "models"))

    # 8. Copy a different folder into the created folder
    models_folder_path = "databases/5s_determ"
    shutil.copytree(models_folder_path, os.path.join(root_folder, folder_name, "databases"))
    markdown_file.close()

    print(f"\033[32m Results saved to {folder_name} \033[0m")

try:
    
    create_markdown_with_model()

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