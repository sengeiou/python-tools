#!/usr/bin/python3
#coding=utf-8


import xml_parse as xml
import os
import re


#
#                                          |->TargetOption->TargetArmAds->Cads->VariousControls->IncludePath
#                                          |
# XML map path: Project->Targets->Target->Groups->Group->
# 
#     GroupName
# ->|
#     Files->File->FileName
#                ->FileType
#                ->FilePath


#Project include path for C/C++ compiler
include_path = ['.\include;',
                '.\plc_include;',
                '.\others\include;',
                '.\others;',
                '.\ecrt_lib\include\ecrt;',
                '.\ecrt_lib\include;',
                '.\ecrt_lib\include\lib']

file_type_id = {'.h':'5', '.c':'1'}

project_group_name = ['eslv_inc', 'eslv_src', 'lib', 'cia402', 'ecrt_lib', 'printk', 'cia402_mc', 'lib']


def generate_include(inc_path = []):
    sum_str = ''
    for item in inc_path:
        sum_str += item
    return sum_str
          
def find_cc_compile_option(root):
    return xml.xml_find_tag(root, 'Cads')
  
def set_cc_compile_option(cc_root, tag, option):
    child = xml.xml_find_tag(cc_root, tag)
    if child != None:
        child.text = option

def add_file_to_group(group_root, path_name):
    fnode = xml.xml_new_parent('File', group_root)

    ext_name = os.path.splitext(path_name)
    relpath = '.\\' + os.path.relpath(path_name)

    xml.xml_add_child(fnode, 'FileName', os.path.basename(path_name))
    xml.xml_add_child(fnode, 'FileType', file_type_id[ext_name[1]])
    xml.xml_add_child(fnode, 'FilePath', relpath)

def find_file_group(root, group_name):
    group = xml.xml_find_node_by_text(root, 'Group', 'GroupName', group_name)
    if group:
        return group.find('Files')
    else:
        return None

def create_file_group(groups_root, group_name):
    gnode = xml.xml_new_parent('Group', groups_root)
    xml.xml_add_child(gnode, 'GroupName', group_name)
    fnode = xml.xml_new_parent('Files', gnode)
    return fnode
    
def list_dir(path, filelists, exclude_dir=[]):
    list_content = []
    filelists.append('<DIR>' + path)
    list_files = os.listdir(path)
    for item in list_files:
        if os.path.isdir(os.path.join(path, item)):
            if item not in exclude_dir:
                list_content.append(os.path.join(path, item))
        else:
            filelists.append(item)
            #print(item)

    for list_item in list_content:
       # print('Content->', list_item)
        list_dir(list_item, filelists, exclude_dir)


def project_add_files(groups_root, path):
    list_files = []
    abs_path = os.path.abspath(path)
    list_dir(path, list_files, ['.svn', 'include', 'tools'])

    patern = re.compile(r'<DIR>\w+')

    group_file_root = None
    group_name = None
    file_node = None
    dir_path = None
    
    for f_item in list_files:
        #Is directory?
        if patern.match(f_item):
            dir_path = re.sub(r'<DIR>', '', f_item)
            group_name = os.path.basename(dir_path)
            file_node = create_file_group(groups_root, group_name)
            #print(group_name, dir_path)
            
        else:
            add_file_to_group(file_node, dir_path+ '\\'+ f_item)
            #print(f_item)

                
def delete_group(groups_root, group_name=[]):
    del_list = []
    for item in groups_root.iter('Group'):
        text = item.find('GroupName').text
        if text in group_name:
            del_list.append(item)
            #print('Delete ', text)
    for rm_item in del_list:
        groups_root.remove(rm_item)
        
        
def project_setup(target_file, add_dir, del_group=[]):
    #Parse XML tree to memory
    tree = xml.xml_open_file(target_file)
    root = tree.getroot()

    #Set include diectories for c/c++ compiler
    print('Set c/c++ compiler options...');
    cc_node = find_cc_compile_option(root)
    inc_path = generate_include(include_path)
    set_cc_compile_option(cc_node, 'IncludePath', inc_path)
    set_cc_compile_option(cc_node, 'MiscControls', '--fpu=vfpv2 --c99 --diag_suppress=1296,111,1')

    #Get the root of file groups
    groups_root = xml.xml_find_tag(root, 'Groups')

    #Delete existing group
    print('Delete existing group...')
    delete_group(groups_root, del_group)

    #Add group file from special directory
    print('Add files to project...')
    project_add_files(groups_root, add_dir)

    #Relayout xml format and save it
    xml.xml_relayout(root)
    xml.xml_save(tree, target_file)


def project_fixed(file_name):
    try:
        title = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\" ?>"
        file_text = ''
        with open(file_name, 'r') as fp:
            for line in fp.readlines():
                #print(line)
                if line.find("<?xml version='1.0' encoding='utf-8'?>") == 0:
                    #print('Found it', line)
                    line = title + '\n'
                    file_text += line
                else:
                    file_text += line
                    
        with open(file_name, 'w') as fp:
            fp.write(file_text)
            
    except OSError as e:
        print(e)    
    

if __name__ == '__main__':
    #PMSM_LPC32X0.uvproj

    file_name = 'PMSM_LPC32X0.uvproj'
    project_setup(file_name, 'ecrt_lib', project_group_name)
    project_fixed(file_name)

    os.system('pause')

        
        
    
    #target_file = 'test.xml'
    #tree = xml.xml_open_file(target_file)
    #root = tree.getroot()

    #groups_root = xml.xml_find_tag(root, 'Groups')
    #fpath = os.path.abspath('cia402.c')

    #groupfile_node = create_file_group(groups_root, 'ecrt_src')
    #add_file_to_group(groupfile_node, fpath)

    #delete_group(groups_root, ['ecrt_lib', 'cia402_mc', 'printk'])
    #project_add_files(groups_root, 'ecrt_lib')

    #for item_elem in groups_root.iter():
    #    print(item_elem.tag, item_elem.text)
    #add_file_to_group(groupfile_node, fpath)
    #xml.xml_relayout(root)
    #xml.xml_save(tree, target_file)


    


    
    


