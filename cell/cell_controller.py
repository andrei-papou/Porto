#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gtk

import cell.cell as model_cell


class CellController(object):

    def __init__(self, cell, cell_view, notebook):

        self.cell = cell
        self.cell_view = cell_view
        self.notebook = notebook

        self.cell.connect('mark-set', self.on_cursor_movement)
        self.cell.connect('paste-done', self.on_paste)

        # observe cell view
        self.cell_view.connect('focus-in-event', self.on_focus_in)
        self.cell_view.text_entry.connect('focus-in-event', self.on_source_view_focus_in)
        self.cell_view.get_source_view().connect('size-allocate', self.on_size_allocate)
        self.cell_view.text_widget_sw.connect('scroll-event', self.on_scroll)
        
        self.cell_view.text_entry.connect('key-press-event', self.observe_keyboard_keypress_events)

    '''
    *** signal handlers: cells
    '''
    
    def on_scroll(self, scrolled_window, event):

        if(abs(event.delta_y) > 0):
            adjustment = self.notebook.view.get_vadjustment()

            page_size = adjustment.get_page_size()
            scroll_unit = pow (page_size, 2.0 / 3.0)

            adjustment.set_value(adjustment.get_value() + event.delta_y*scroll_unit)

        return True

    def observe_keyboard_keypress_events(self, widget, event):

        # switch cells with arrow keys: upward
        if event.keyval == Gdk.keyval_from_name('Up') and event.state == 0:
            notebook = self.cell.get_notebook()
            cell = self.cell
            if isinstance(cell, model_cell.MarkdownCell) and cell.get_result() != None:
                prev_cell = notebook.get_prev_cell(cell)
                if not prev_cell == None:
                    notebook.set_active_cell(prev_cell)
                    prev_cell.controller.place_cursor_on_last_line()
                    return True

            if cell.get_notebook_position() > 0:
                if cell.get_iter_at_mark(cell.get_insert()).get_offset() == 0:
                    prev_cell = notebook.get_prev_cell(cell)
                    if not prev_cell == None:
                        notebook.set_active_cell(prev_cell)
                        prev_cell.controller.place_cursor_on_last_line()
                        return True
        
        # switch cells with arrow keys: downward
        if event.keyval == Gdk.keyval_from_name('Down') and event.state == 0:
            notebook = self.cell.get_notebook()
            cell = self.cell
            
            if isinstance(cell, model_cell.MarkdownCell) and cell.get_result() != None:
                next_cell = notebook.get_next_cell(cell)
                if not next_cell == None:
                    notebook.set_active_cell(next_cell)
                    next_cell.place_cursor(next_cell.get_start_iter())
                    return True
                
            if cell.get_notebook_position() < notebook.get_cell_count() - 1:
                if cell.get_char_count() == (cell.get_iter_at_mark(cell.get_insert()).get_offset()):
                    next_cell = notebook.get_next_cell(cell)
                    if not next_cell == None:
                        notebook.set_active_cell(next_cell)
                        next_cell.place_cursor(next_cell.get_start_iter())
                        return True

        if event.keyval == Gdk.keyval_from_name('BackSpace') and event.state == 0:
            notebook = self.cell.get_notebook()
            cell = self.cell

            if isinstance(cell, model_cell.CodeCell) and cell.get_char_count() == 0:
                prev_cell = notebook.get_prev_cell(cell)
                if not prev_cell == None:
                    notebook.set_active_cell(prev_cell)
                    prev_cell.controller.place_cursor_on_last_line()
                    cell.remove_result()
                    notebook.remove_cell(cell)
                    return True

            if isinstance(cell, model_cell.MarkdownCell):
                if cell.get_result() != None or cell.get_char_count() == 0:
                    prev_cell = notebook.get_prev_cell(cell)
                    next_cell = notebook.get_next_cell(cell)
                    if not prev_cell == None: 
                        notebook.set_active_cell(prev_cell)
                        prev_cell.controller.place_cursor_on_last_line()
                    elif not next_cell == None:
                        notebook.set_active_cell(next_cell)
                        next_cell.place_cursor(next_cell.get_start_iter())
                    else:
                        notebook.create_cell('last', '', activate=True)
                    cell.remove_result()
                    notebook.remove_cell(cell)
                    return True
        
        return False
    
    def on_cursor_movement(self, cell=None, mark=None, user_data=None):
        self.notebook.controller.scroll_to_cursor(self.cell, check_if_position_changed=True)

    def on_paste(self, cell=None, clipboard=None, user_data=None):
        ''' hack to prevent some gtk weirdness. '''
            
        prev_insert = self.cell.create_mark('name', self.cell.get_iter_at_mark(self.cell.get_insert()), True)
        self.cell.insert_at_cursor('\n')
        GLib.idle_add(lambda: self.cell.delete(self.cell.get_iter_at_mark(self.cell.get_insert()), self.cell.get_iter_at_mark(prev_insert)))

    def on_focus_in(self, cell_view, event=None):
        ''' activate cell on click '''

        if self.cell.is_active_cell() == False:
            self.cell.get_notebook().set_active_cell(self.cell)
        if self.cell_view.text_widget.get_reveal_child():
            self.cell_view.text_entry.grab_focus()
            self.notebook.controller.scroll_to_cursor(cell_view.text_entry.get_buffer(), check_if_position_changed=True)
        return False
    
    def on_source_view_focus_in(self, source_view, event=None):
        ''' activate cell on click '''

        if self.cell.is_active_cell() == False:
            self.cell.get_notebook().set_active_cell(self.cell)
            return True
        return False
    
    def on_size_allocate(self, text_field, allocation=None):
        self.notebook.controller.scroll_to_cursor(text_field.get_buffer(), check_if_position_changed=True)
        
    '''
    *** helpers: cell
    '''
    
    def place_cursor_on_last_line(self):
        target_iter = self.cell_view.text_entry.get_iter_at_position(0, self.cell_view.text_entry.get_allocated_height() - 30)
        self.cell.place_cursor(target_iter[1])


class CodeCellController(CellController):

    def __init__(self, cell, cell_view, notebook):
        CellController.__init__(self, cell, cell_view, notebook)


class MarkdownCellController(CellController):

    def __init__(self, cell, cell_view, notebook):
        CellController.__init__(self, cell, cell_view, notebook)


