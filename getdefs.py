# python code to get theorems and definitions from a tex file
# This will scan the tex file and extract theorems and definitions
# Theorems are written in the form:
# \begin{theorem}[name]
# ...
# \end{theorem}
# The same is true for definitions, propositions, lemmas, corollaries, and remarks

import re
import sys
import os

LIST_OF_ENVS = [
    "theorem",
    "definition",
    "proposition",
    "lemma",
    "corollary",
    "remark"
]

FOLDER_TO_SEARCH = "chapters/"


def get_files(folder):
    files = []
    for file in os.listdir(folder):
        if file.endswith(".tex"):
            files.append(folder + file)
    return files



def get_theorems():
    files = get_files(FOLDER_TO_SEARCH)
    
    full_list_of_theorems = []
    chapter_obj = {}

    for file in files:
        with open(file, "r") as f:
            lines = f.read()
            line_number = 0
            print("Scanning file:", file)
            chapter_obj["file"] = file.replace(FOLDER_TO_SEARCH, "")
            # Remove file extension
            chapter_obj["file"] = chapter_obj["file"].replace(".tex", "")
            # Convert to number
            chapter_obj["file"] = int(chapter_obj["file"])
            # Convert to string and append "Chapter " to beginning
            chapter_obj["file"] = "Chapter " + str(chapter_obj["file"])
            list_of_theorems = []
            

            for env in LIST_OF_ENVS:
                # find enclosing environment
                pattern = "(\\\\begin\\{" + env +"\\}.*?\\\\end\\{" + env +"\\})"
                try:
                    matches = re.findall(pattern, lines, re.DOTALL)
                    # Return line number of match
                    line_number_of_match = re.search(pattern, lines, re.DOTALL).start()
                    for match in matches:
                        list_of_theorems.append(match)
                except:
                    print("Error in file:", file)
                    print("Error in environment type:", env)
                    print("Error in pattern:", pattern)
                    print("Error description:", sys.exc_info()[0])
                    print("Error details:", sys.exc_info()[1])

            chapter_obj["theorems"] = list_of_theorems

            full_list_of_theorems.append(chapter_obj)

    return full_list_of_theorems

def parse_theorems(list_of_theorem_objs):
    parsed_theorems = []
    for chapter_obj in list_of_theorem_objs:
        # print index
        #print(list_of_theorems.index(theorem) + 1)
        # remove string "label=(\alph*)" from theorem object
        chapter = chapter_obj["file"]
        chapter_theorem_obj = {}
        chapter_theorem_obj["chapter"] = chapter
        list_of_theorems = chapter_obj["theorems"]
        parsed_theorems_list = []
        for theorem in list_of_theorems:
            theorem = theorem.replace("[label=(\\alph*)]", "")
            theorem_obj = {}

            # find environment type
            for env in LIST_OF_ENVS:
                #print("Checking for environment:", env)
                if re.search("\\\\begin\\{" + env + "\\}", theorem):
                    theorem_obj["type"] = env
                    break
                else :
                    theorem_obj["type"] = "No type"
            
            # find theorem name

            try:
                # find theorem name enclosed in square brackets
                name = re.search("\}\[(.*?)\]", theorem).group(1)
                theorem_obj["name"] = name
            except:
                try:
                    # find theorem name enclosed in square brackets preceded by a %
                    # for example: \begin{theorem}%[name]
                    name = re.search("%\[(.*?)\]", theorem).group(1)
                    # if name contains "label=", go to next match
                    if "label=" in name:
                        name = re.search("%\[(.*?)\]", theorem, re.DOTALL).group(1)


                    theorem_obj["name"] = name
                except:
                    theorem_obj["name"] = "No name"

            # get label
            try:
                label = re.search("\\\\label\\{(.*?)\\}", theorem).group(1)
                theorem_obj["label"] = label
            except:
                theorem_obj["label"] = "No label"

            # get first 100 characters of theorem (minus the environment)
            try:
                theorem_text = re.search("\\\\begin\\{" + theorem_obj["type"] + "\\}(.*?)\\\\end\\{" + theorem_obj["type"] + "\\}", theorem, re.DOTALL).group(1)
                theorem_obj["text"] = theorem_text[:20]
                # Remove newlines and extra spaces
                # Remove title in square brackets
                theorem_obj["text"] = re.sub("\[(.*?)\]", "", theorem_obj["text"])
                # Remove label
                theorem_obj["text"] = re.sub("\\\\label\\{(.*?)\\}", "", theorem_obj["text"])
                theorem_obj["text"] = re.sub("\n", "", theorem_obj["text"])
                theorem_obj["text"] = re.sub("\s+", " ", theorem_obj["text"])
                # Remove initial and trailing spaces
                theorem_obj["text"] = re.sub("^\s+", "", theorem_obj["text"])
                
            except:
                theorem_obj["text"] = "No text"

            parsed_theorems_list.append(theorem_obj)

        chapter_theorem_obj["theorems"] = parsed_theorems_list

        parsed_theorems.append(chapter_theorem_obj)

    return parsed_theorems




def create_tex_file(parsed_theorems):
    with open("theorems.tex", "w") as f:
        f.write("\\chapter*{Index of definitions and results}\n")
        # New heading for each type of theorem
        # sort LIST_OF_ENVS alphabetically
        # Redefine corollary and lemma to become theorems in dictionary
        for theorem in parsed_theorems:
            if theorem["type"] == "corollary":
                theorem["type"] = "theorem"
            if theorem["type"] == "lemma":
                theorem["type"] = "theorem"
        # Sort theorems by type
        parsed_theorems.sort(key=lambda x: x["type"])


        LIST_OF_ENVS.sort()
        for env in LIST_OF_ENVS:
            # if count of theorems of this type is 0, skip
            count = 0
            for theorem in parsed_theorems:
                if theorem["type"] == env:
                    count += 1
            if count == 0:
                continue
            else:
                # make env plural
                env_display = env + "s"
                # Capitalize first letter
                env_display = env_display.capitalize()
                f.write("\\section*{" + env_display + "}\n")
                for theorem in parsed_theorems:
                    if theorem["type"] == env:
                        if theorem["label"] != "No label":
                            f.write("\\textbf{\\ref{" + theorem["label"] + "}}\\quad " + theorem["name"] + ", p.~\\pageref{" + theorem["label"] + "}\n")
                        else:
                            f.write(theorem["name"] + "\n")
                        
                        f.write("\n")

        f.close()

# normalize dictionary

def normalize_dict(parsed_theorems):
    normalized_theorems = []
    for chapter in parsed_theorems:
        for theorem in chapter["theorems"]:
            theorem["chapter"] = chapter["chapter"]
            normalized_theorems.append(theorem)
    return normalized_theorems


import pandas as pd

def main():
    list_of_theorems = get_theorems()
    parsed_theorems = parse_theorems(list_of_theorems)
    print(parsed_theorems)
    
    normalized_dictionary = normalize_dict(parsed_theorems)
    #make df from dictionary
    df = pd.DataFrame(normalized_dictionary)
    print(df)
    #create_tex_file(parsed_theorems)

if __name__ == "__main__":
    main()
