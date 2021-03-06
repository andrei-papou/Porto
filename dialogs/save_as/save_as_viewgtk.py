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
from gi.repository import Gtk
from gi.repository import Gdk


class SaveAs(object):
    ''' This dialog is asking for the notebook name. '''

    def __init__(self, main_window):
        builder = Gtk.Builder.new_from_string('<?xml version="1.0" encoding="UTF-8"?><interface><object class="GtkDialog" id="dialog"><property name="use-header-bar">1</property></object></interface>', -1)

        self.save_as_dialog = builder.get_object('dialog')
        self.save_as_dialog.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.save_as_dialog.set_destroy_with_parent(True)
        self.save_as_dialog.set_transient_for(main_window)
        self.save_as_dialog.set_modal(True)
        self.save_as_dialog.set_can_focus(False)

        self.css_provider = Gtk.CssProvider()
        self.save_as_dialog.get_style_context().add_provider(self.css_provider, 800)

        self.headerbar = self.save_as_dialog.get_header_bar()
        self.headerbar.set_show_close_button(False)
        self.headerbar.set_title('Save As')
        self.cancel_button = self.save_as_dialog.add_button('_Cancel', Gtk.ResponseType.CANCEL)
        self.save_button = self.save_as_dialog.add_button('_Save', Gtk.ResponseType.APPLY)
        self.save_button.set_receives_default(True)
        self.save_button.get_style_context().add_class('suggested-action')
        self.headerbar.show_all()

        self.topbox = self.save_as_dialog.get_content_area()
        self.topbox.set_border_width(0)
        self.topbox.set_margin_left(18)
        self.topbox.set_margin_right(18)
        self.vbox = Gtk.VBox()
        self.vbox.set_margin_top(18)
        name_label = Gtk.Label('Name')
        name_label.set_xalign(0)
        self.vbox.pack_start(name_label, False, False, 0)
        self.topbox.add(self.vbox)

        self.name_entry = Gtk.Entry()
        self.name_entry_buffer = self.name_entry.get_buffer()
        self.name_entry.set_margin_top(3)
        self.name_entry.set_margin_bottom(6)
        self.vbox.pack_start(self.name_entry, False, False, 0)
        desc_label = Gtk.Label('This will also be the filename.')
        desc_label.get_style_context().add_class('form-description')
        desc_label.set_xalign(0)
        self.vbox.pack_start(desc_label, False, False, 0)
        
        folder_label = Gtk.Label('Folder')
        folder_label.set_xalign(0)
        folder_label.set_margin_top(18)
        self.vbox.pack_start(folder_label, False, False, 0)
        self.folder_entry = Gtk.Button()
        self.folder_entry_widget = Gtk.HBox()
        self.folder_entry_widget_label = Gtk.Label('(None)')
        self.folder_entry_widget.pack_start(self.folder_entry_widget_label, False, False, 0)
        self.folder_entry_widget.pack_end(Gtk.Image.new_from_icon_name('document-open-symbolic', Gtk.IconSize.BUTTON), False, False, 0)
        self.folder_entry.add(self.folder_entry_widget)
        self.folder_entry.set_margin_top(3)
        self.folder_entry.set_margin_bottom(24)
        self.vbox.pack_start(self.folder_entry, False, False, 0)
        
    def run(self):
        return self.save_as_dialog.run()
        
    def response(self, args):
        self.save_as_dialog.response(args)
        
    def __del__(self):
        self.save_as_dialog.destroy()
        

