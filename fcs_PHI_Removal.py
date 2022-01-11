# Date: 2021-06-8
# Author: Hannah Ghassabeh
# Purpose: Rename files within directory and remove PHI. ***Still includes H-Number***
# Prepared for Dr.Goswami and Dr.Peerani

import os
from FlowCytometryTools import FCMeasurement
import shutil

# **** Path declarations ****

# ---- Set dataDirectory equal to the directory that contains the files you wish to remove PHI ---
# ---- Creates new anonymous files in the this directory and a key in the form of text file ------
data_directory = r'C:\Users\hghas\OneDrive\Desktop\test'

# ---- Set jar_directory to the directory that contains the deidentifyfcs.jar executable ---------
# ---- Warning: The jar file can not be in the same directory as your fcs files ------------------
jar_directory = r'C:\Users\hghas\OneDrive\Desktop\deid\deidentifyfcs.jar'

# ---- Optional: moves PHI containing files to the path specified by data_dest --------------------
data_dest = r'C:\Users\hghas\OneDrive\Desktop\demonstration'


class Node (object):

    def __init__(self, name, study_number, h_number, tube, next_node=None):
        self.name = name
        self.h_number = h_number
        self.study_number = study_number
        self.file_list = []
        self.tube = tube
        self.next_node = next_node

    def get_next(self):
        return self.next_node

    def set_next(self, next_node):
        self.next_node = next_node

    def get_name(self):
        return self.name

    def get_study_number(self):
        return self.study_number

    def get_h_number(self):
        return self.h_number

    def get_tube(self):
        return self.tube


class LinkedList (object):
    def __init__(self, root=None):
        self.root = root

    # **** Method add ****
    # Adds a new node to the front of the linked list and adds file_name to file_list
    def add(self, name, study_number, h_number, file_name, tube):
        new_node = Node(name, study_number, h_number, tube, self.root)
        self.root = new_node
        new_node.file_list.append(file_name)

    # **** Method find ****
    # Returns true & study number if the node with the same patient name and h number exist
    def find(self, name, h_number):
        this_node = self.root
        while this_node:
            if this_node.get_name() == name and this_node.get_h_number() == h_number:
                return this_node.get_study_number()
            else:
                this_node = this_node.get_next()
        return False

    # **** Method find_name ****
    # Increments file name according to number of file names in cur_node.file_list attribute
    def find_name(self, temp_file_name, s_number, tube):
        cur_node = self.root
        while cur_node:
            if s_number == cur_node.get_study_number() and tube == cur_node.get_tube():
                count_file = len(cur_node.file_list)
                temp_1, temp_2 = temp_file_name.split(".")
                temp_file_name = f"{temp_1} ({count_file}).{temp_2}"
                cur_node.file_list.append(temp_file_name)
                return temp_file_name
            else:
                cur_node = cur_node.get_next()
        return temp_file_name


# **** Function search_string ****
# returns True if the substring is found within the string
def search_string(string, substring):
    result = string.find(substring)
    if result == -1:
        return False
    return True


patient_list = LinkedList()
study_num = 100
os.chdir(data_directory)

# Goes through each file within the directory/folder specified
for i, file in enumerate(os.listdir()):

    sample = FCMeasurement(ID=f'Test Sample #{i + 100}', datafile=file)

    dictn = sample.get_meta()
    mrn, h_numb = dictn['@SAMPLEID3'].split()
    paitent_name = dictn['@SAMPLEID1']

    # Searching if the patient already exists in linked list and assign study number accordingly
    if patient_list.find(f"{dictn['@SAMPLEID1']}", h_numb):
        dictn['@SAMPLEID1'] = patient_list.find(f"{dictn['@SAMPLEID1']}", h_numb)
        fileName = "{} {} {}{}".format(dictn['@SAMPLEID1'], dictn['@SAMPLEID2'], h_numb, '.fcs')
        fileName = patient_list.find_name(fileName, dictn['@SAMPLEID1'], dictn['@SAMPLEID2'])
    # If patient doesn't exist assign new study number and add a new node to linked list
    else:
        fileName = "{} {} {}{}".format(study_num,dictn['@SAMPLEID2'], h_numb, '.fcs')
        patient_list.add(f"{dictn['@SAMPLEID1']}", study_num, h_numb, fileName, dictn['@SAMPLEID2'])
        study_num += 1

    # ---- Open text_file and writing old and new file name ---
    text_file = open(fr'{data_directory}\0key.txt', 'a')
    text_file.write(f'Original file name: {file} \n')
    text_file.write(f'Updated file name: {fileName}\n')
    text_file.write('File naming and content inconsistencies: ')

    # Searches for patient name, tube, mrn, H number and technician's name from within the file in the file name
    # If the id's are not found a sentence describing the discrepancy is written in text_file
    consistent = True
    if not search_string(file, paitent_name):
        text_file.write(f"@SAMPLEID1 ({paitent_name}) inconsistent with file name\n")
        consistent = False
    if not search_string(file, dictn['@SAMPLEID2']):
        text_file.write(f"@SAMPLEID2 ({dictn['@SAMPLEID2']}) inconsistent with file name\n")
        consistent = False
    if not search_string(file, mrn):
        text_file.write(f"@SAMPLEID3 ({mrn}) inconsistent with file name\n")
        consistent = False
    if not search_string(file, h_numb):
        text_file.write(f"@SAMPLEID3 ({h_numb}) inconsistent with file name\n")
        consistent = False
    if not search_string(file, dictn['@SAMPLEID4']):
        text_file.write(f"@SAMPLEID4 ({dictn['@SAMPLEID4']}) inconsistent with file name\n")
        consistent = False
    if consistent:
        text_file.write("N/A\n")

    text_file.write('\n\n')
    text_file.close()

    # Runs the command line from deidentifyfcs.jar
    cmd = fr'java -jar {jar_directory} "-InputFile:{file}" "-Remove:@SAMPLEID1,@SAMPLEID2,@SAMPLEID3,@SAMPLEID4,$INST,$INSTADDRESS,$FIL" "-OutputFile:{fileName}"'
    os.system(cmd)

    # Optional: moves files with PHI to the data_dest
    shutil.move(file, data_dest)
