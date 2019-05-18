#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
from heapq import nlargest
import subprocess

N_VERSIONS_TO_KEEP = 1

COMMAND = 'dpkg -l | grep -E "ii.*linux-(headers|image|modules)-\d*"'
IMAGESTRING = 'linux-image-generic'

#Input:
#dpkg -l | grep -E "ii.*linux-(headers|image|modules)-\d*"

def command_output():
    var = subprocess.getoutput(COMMAND)
    return var

def meta_version(s):
    '''Get Linux Meta Package Version'''
    pass

def extract_version(version_string, full_tuple=False):
    version_string = re.split('[\.|-]',version_string)
    version = '.'.join(version_string[:3])
    build_ref = version_string[3:4][0]
    build_version = '.'.join(version_string[3:])
    if full_tuple:
        return version, build_ref, build_version
    else:
        return version+'-'+build_ref

def create_table(s, process_version=True, full_tuple=False):
    '''Documentation for create_table function'''
    table = []
    for line in s.split('\n'):
        split = re.split(r' \ +', line)
        table.append(split[1:3])
    if process_version:
        for item in table:
            item[1] = extract_version(item[1], full_tuple)
    return table

def dict_from_table(table, key_column=1, value_process=lambda x: ' '.join(x)):
    version_dict = {}
    for item in table:
        print('Item:', item)
        key = item[key_column]
        item.remove(key)
        value = value_process(item)
        version_dict.setdefault(key, []).append(value)
        print('Value:', item)
    return version_dict

def read_shell_pipe():
    '''Lê a entrada via shell pipe'''
    s = ''
    for line in sys.stdin:
        s+=line
    #s = s.rstrip()
    return s

def create_version_dict(s):
    '''Extrai o nome do programa, a versão, e adiciona o programa na lista de versão correspondente no dicionário'''

    version_dict = {}
    meta_dict = {}

    for line in s.split('\n'):
        if line:
            row = re.split('\ +', line)
            program_name = row[1]
            version = extract_version(row[2])
            if re.match('.*\d+.*' , program_name):
                # re.search('\d+\.\d+\.\d+-\d+', program_name).group()
                version_dict.setdefault(version, []).append(program_name)
            else:
                meta_dict.setdefault(program_name, version)

    return version_dict, meta_dict

def remove_versions(version_dict, meta_version=None):
    '''Remove do dicionário as listas das duas versões mais recentes e cria a lista final dos programas a serem removidos'''

    version_keys = list(version_dict.keys())
    if meta_version:
        version_keys.remove(meta_version)
    keep_versions = nlargest(N_VERSIONS_TO_KEEP, version_keys)

    if meta_version:
        keep_versions.append(meta_version)

    for program_version in keep_versions:
        del(version_dict[program_version])

    programs_final = version_dict.values()
    programs_final = [y for x in programs_final for y in x]

    return programs_final, keep_versions

def main():

    #s = read_shell_pipe()
    s = command_output()
    version_dict, meta_dict = create_version_dict(s)
    version_found = list(version_dict.keys())

    meta_version = meta_dict.get("linux-image-generic")
    programs_final, keep_versions = remove_versions(version_dict, meta_version)

    if meta_version:
        for i,item in enumerate(version_found):
            if item == meta_version:
                version_found[i] += ' (linux-image-generic)'
        for i,item in enumerate(keep_versions):
            if item == meta_version:
                keep_versions[i] += ' (linux-image-generic)'


    '''Testa e imprime as versões atuais, a serem removidas e o comando pra remoção'''
    print('Found Linux versions:\n', '\n '.join(version_found), end='\n\n')

    print('Versions to keep:\n', '\n '.join(keep_versions), end='\n\n')

    if programs_final:
        print('Version to be removed:\n', '\n '.join(set(version_dict.keys()) - set(keep_versions)) , end='\n\n')

        print('Command to remove:')
        new_s = 'sudo apt remove {}'.format(' '.join(programs_final))
        print(new_s)

    else:
        print('System Ok!')


if __name__ == '__main__':
    sys.exit(main())