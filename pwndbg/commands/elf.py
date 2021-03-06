#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import gdb
from elftools.elf.elffile import ELFFile

import pwndbg.commands


@pwndbg.commands.Command
def elfheader():
    """
    Prints the section mappings contained in the ELF header.
    """
    local_path = pwndbg.file.get_file(pwndbg.proc.exe)
    if not local_path:
        print('No file is selected')
        return

    with open(local_path, 'rb') as f:
        elffile = ELFFile(f)
        load_segment = elffile.get_segment(3)
        segment_base = load_segment['p_vaddr']
        sections = []
        for section in elffile.iter_sections():
            start = section['sh_addr']

            # Don't print sections that aren't mapped into memory
            if start == 0:
                continue

            size = section['sh_size']
            sections.append((start, start + size, section.name))

        sections.sort()
        for start, end, name in sections:
            print('%#x - %#x ' % (start, end), name)

@pwndbg.commands.Command
def gotplt():
    """
    Prints any symbols found in the .got.plt section if it exists.
    """
    print_symbols_in_section('.got.plt', '@got.plt')

@pwndbg.commands.Command
def plt():
    """
    Prints any symbols found in the .plt section if it exists.
    """
    print_symbols_in_section('.plt', '@plt')

def get_section_bounds(section_name):
    local_path = pwndbg.file.get_file(pwndbg.proc.exe)
    if not local_path:
        print('No file is selected')
        return (None, None)

    with open(local_path, 'rb') as f:
        elffile = ELFFile(f)

        section = elffile.get_section_by_name(section_name)

        if not section:
            return (None, None)

        start = section['sh_addr']
        size = section['sh_size']
        return (start, start + size)

def print_symbols_in_section(section_name, filter_text=''):
    start, end = get_section_bounds(section_name)
    if start == None:
        print(pwndbg.color.red('Could not find section'))
        return

    symbols = get_symbols_in_region(start, end, filter_text)
    for symbol, addr in symbols:
        print(hex(int(addr)) + ': ' + symbol)

def get_symbols_in_region(start, end, filter_text=''):
    symbols = []
    ptr_size = pwndbg.typeinfo.pvoid.sizeof
    addr = start
    while addr < end:
        name = pwndbg.symbol.get(addr)
        if name != '' and '+' not in name and filter_text in name:
            symbols.append((name, addr))
        addr += ptr_size

    return symbols
