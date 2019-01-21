#!/usr/bin/python3
#coding=utf-8

import xml.etree.cElementTree as ET
import os


def xml_relayout(elem, level=0):
    i = '\n' + level * '\t'
    if len(elem) :
        if not elem.text or not elem.text.strip() :
            elem.text = i + '\t'
        if not elem.tail or not elem.tail.strip() :
            elem.tail = i
        for elem in elem :
            xml_relayout(elem, level+1)
        if not elem.tail or not elem.tail.strip() :
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()) :
            elem.tail = i

def xml_open_file(path):
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        print('Open faile: ', e.code, e.position)
    return tree

def xml_add_child(parent, tag, text, attr={}):
    element = ET.SubElement(parent, tag, attr)
    element.text = text
    return element

def xml_new_parent(tag, parent=None):
    root = ET.Element(tag)
    if parent != None:
        parent.append(root)
    return root

def xml_remove_child(root, parent, tag):
    for child in root.iter(parent):
        if child.find(tag):
            child.remove(tag)
            break

def xml_save(tree, path):
    try:
        tree.write(path, "utf-8", True)
    except ET.ParseError as e:
        print('Write file faile: ', e.code, e.position)

def xml_find_tag(root, tag_name):
    for child in root.iter():
        if child.tag == tag_name:
            return child
    return None

def xml_findall_tag(root, tag_name):
    list_tag = []
    for child in root.iter():
        if child.tag == tag_name:
            list_tag.append(child)
    return list_tag

def xml_find_node_by_text(root, node_name, tag, text):
    for child in root.iter(node_name):
        if child.find(tag).text == text:
            return child
    return None

    
        
