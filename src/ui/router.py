import customtkinter as ctk
from typing import Callable, Optional

class ViewRouter:
    """
    Manages view transitions and navigation state in the application.
    """
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.views = {}
        self.current_view_name: Optional[str] = None
        self.current_view_widget: Optional[ctk.CTkFrame] = None
        
    def register_view(self, name: str, widget: ctk.CTkFrame, 
                      on_enter: Optional[Callable] = None, 
                      on_exit: Optional[Callable] = None):
        """
        Registers a view widget with an optional entry and exit callbacks.
        """
        self.views[name] = {
            "widget": widget,
            "on_enter": on_enter,
            "on_exit": on_exit
        }
        # Initially hide the widget
        widget.grid_forget()
        
    def navigate(self, name: str, **kwargs):
        """
        Switch to the specified view.
        """
        if name not in self.views:
            raise ValueError(f"View '{name}' is not registered.")
            
        # Exit current view
        if self.current_view_name:
            exit_cb = self.views[self.current_view_name]["on_exit"]
            if exit_cb:
                exit_cb()
            self.current_view_widget.grid_forget()
            
        # Enter new view
        view_data = self.views[name]
        self.current_view_name = name
        self.current_view_widget = view_data["widget"]
        
        enter_cb = view_data["on_enter"]
        if enter_cb:
            enter_cb(**kwargs)
            
        self.current_view_widget.grid(row=0, column=0, sticky="nsew")
        self.root.logger.info(f"Navigated to view: {name}")
