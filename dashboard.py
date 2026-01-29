"""
Dashboard GUI for Neo4j Workflow Visualization
Displays processes, statistics, and workflow graphs with Neo4j integration
"""

import tkinter as tk
from tkinter import ttk, messagebox
from neo4j_visualizer import Neo4jVisualizer
from neo4j_loader import Neo4jLoader
import logging


class WorkflowDashboard:
    """
    Main dashboard for visualizing Neo4j workflow data
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the dashboard
        
        Args:
            root: Tk root window
        """
        self.root = root
        self.root.title("Neo4j Workflow Dashboard")
        self.root.geometry("1400x900")
        
        # Initialize visualizer
        self.visualizer = Neo4jVisualizer()
        self.loader = Neo4jLoader()  # Add loader for analytics queries
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # Current data
        self.processes = []
        self.current_process_id = None
        
        # Setup UI
        self.setup_ui()
        self.connect_to_database()
    
    def setup_ui(self):
        """Setup UI components"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top control panel
        control_frame = ttk.LabelFrame(main_frame, text="Process Control", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Process selector
        ttk.Label(control_frame, text="Select Process:").pack(side=tk.LEFT, padx=5)
        
        self.process_var = tk.StringVar()
        self.process_combo = ttk.Combobox(control_frame, textvariable=self.process_var, 
                                         state='readonly', width=30)
        self.process_combo.pack(side=tk.LEFT, padx=5)
        self.process_combo.bind('<<ComboboxSelected>>', self.on_process_selected)
        
        ttk.Button(control_frame, text="Refresh", command=self.refresh_processes).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Load Data from Neo4j", command=self.load_data_from_neo4j).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export", command=self.export_process).pack(side=tk.LEFT, padx=5)
        
        # Main content area with notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Visualization
        self.setup_visualization_tab()
        
        # Tab 2: Analytics
        self.setup_analytics_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
    
    def setup_visualization_tab(self):
        """Setup visualization tab"""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Visualization")
        
        # Main content area with paned window
        paned = ttk.PanedWindow(viz_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Statistics and Info
        left_panel = ttk.Frame(paned)
        paned.add(left_panel, weight=1)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(left_panel, text="Process Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=10, width=40, font=("Courier", 9))
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Query Results frame
        query_frame = ttk.LabelFrame(left_panel, text="Query Results", padding=10)
        query_frame.pack(fill=tk.BOTH, expand=True)
        
        # Query buttons
        query_button_frame = ttk.Frame(query_frame)
        query_button_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(query_button_frame, text="Find Paths (Start→End)", 
                  command=self.find_paths).pack(side=tk.LEFT, padx=2)
        ttk.Button(query_button_frame, text="Find Bottlenecks", 
                  command=self.find_bottlenecks).pack(side=tk.LEFT, padx=2)
        ttk.Button(query_button_frame, text="Simulate Flow", 
                  command=self.simulate_workflow).pack(side=tk.LEFT, padx=2)
        
        # Query results text
        self.query_text = tk.Text(query_frame, height=15, width=40, font=("Courier", 8))
        self.query_text.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Canvas for visualization
        right_panel = ttk.LabelFrame(viz_frame, text="Workflow Visualization (Scroll to zoom, Drag to pan)", padding=10)
        paned.add(right_panel, weight=2)
        
        # Canvas with zoom/pan support
        self.canvas = tk.Canvas(right_panel, bg='white', highlightthickness=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind events for zoom and pan
        self.canvas.bind("<MouseWheel>", self.on_canvas_scroll)  # Windows
        self.canvas.bind("<Button-4>", self.on_canvas_scroll)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_canvas_scroll)    # Linux scroll down
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_scroll_start)  # Start drag
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)     # Drag to pan
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_click)  # Click or end drag
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
        # Canvas info label
        self.canvas_info_label = ttk.Label(right_panel, text="Scroll: Zoom | Drag: Pan | Click: Details", 
                                          foreground='gray')
        self.canvas_info_label.pack(fill=tk.X, pady=(5, 0))
        
        # Store canvas transform state
        self.canvas_zoom = 1.0
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        self.canvas_drag_start = None
        self.dragging_node = None  # Track if dragging a node
        self.node_offsets = {}  # Store individual node offsets for dragging
    
    def setup_analytics_tab(self):
        """Setup analytics reports tab"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="Analytics")
        
        # Analytics controls
        controls_frame = ttk.LabelFrame(analytics_frame, text="Select Report", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(controls_frame, text="Task Search", 
                  command=self.show_task_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Gateway Management", 
                  command=self.show_gateways).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Time KPI", 
                  command=self.show_time_kpi).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Cost KPI", 
                  command=self.show_cost_kpi).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Resources", 
                  command=self.show_resources).pack(side=tk.LEFT, padx=5)
        
        # Task search frame
        search_frame = ttk.LabelFrame(analytics_frame, text="Search Task by Name", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(search_frame, text="Task name:").pack(side=tk.LEFT, padx=5)
        self.task_search_var = tk.StringVar()
        self.task_search_entry = ttk.Entry(search_frame, textvariable=self.task_search_var, width=30)
        self.task_search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", 
                  command=self.perform_task_search).pack(side=tk.LEFT, padx=5)
        
        # Results frame with treeview
        results_frame = ttk.LabelFrame(analytics_frame, text="Report Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create treeview for displaying results
        self.analytics_tree = ttk.Treeview(results_frame, height=20)
        self.analytics_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.analytics_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.analytics_tree.config(yscrollcommand=scrollbar.set)
    
    def show_task_search(self):
        """Show task search results"""
        if not self.task_search_var.get():
            messagebox.showwarning("Warning", "Please enter a task name to search")
            return
        self.perform_task_search()
    
    def perform_task_search(self):
        """Perform task search query"""
        try:
            task_name = self.task_search_var.get()
            if not task_name:
                messagebox.showwarning("Warning", "Please enter a task name to search")
                return
            
            self.status_var.set(f"Searching for tasks with name: {task_name}...")
            self.root.update()
            
            results = self.loader.find_task_in_processes(task_name)
            
            self.display_table_results(
                results, 
                ["process_id", "process_name", "task_id", "task_name"],
                f"Task Search Results - '{task_name}' (Found {len(results)} matches)"
            )
            
            self.status_var.set(f"✓ Found {len(results)} tasks")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def show_gateways(self):
        """Show all gateways report"""
        try:
            self.status_var.set("Loading gateway management report...")
            self.root.update()
            
            results = self.loader.list_all_gateways()
            
            self.display_table_results(
                results,
                ["process_id", "gateway_name", "branch_count"],
                f"Gateway Management Report (Found {len(results)} gateways)"
            )
            
            self.status_var.set(f"✓ Loaded {len(results)} gateways")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load gateways: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def show_time_kpi(self):
        """Show time KPI report"""
        try:
            self.status_var.set("Loading time KPI report...")
            self.root.update()
            
            results = self.loader.get_process_time_kpi()
            
            self.display_table_results(
                results,
                ["process_id", "process_name", "total_minutes", "total_hours"],
                "Process Time KPI Report (Hours)"
            )
            
            self.status_var.set(f"✓ Loaded time KPI for {len(results)} processes")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load time KPI: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def show_cost_kpi(self):
        """Show cost KPI report"""
        try:
            self.status_var.set("Loading cost KPI report...")
            self.root.update()
            
            results = self.loader.get_process_cost_kpi()
            
            self.display_table_results(
                results,
                ["process_id", "process_name", "total_cost"],
                "Process Cost KPI Report (USD)"
            )
            
            self.status_var.set(f"✓ Loaded cost KPI for {len(results)} processes")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cost KPI: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def show_resources(self):
        """Show resource requirements report"""
        try:
            self.status_var.set("Loading resource requirements report...")
            self.root.update()
            
            results = self.loader.get_process_resource_requirements()
            
            # Convert required_roles list to string for display
            for row in results:
                if 'required_roles' in row and isinstance(row['required_roles'], list):
                    row['roles'] = ', '.join(row['required_roles'])
                else:
                    row['roles'] = str(row.get('required_roles', ''))
            
            self.display_table_results(
                results,
                ["process_id", "process_name", "role_count", "roles"],
                "Process Resource Requirements Report"
            )
            
            self.status_var.set(f"✓ Loaded resources for {len(results)} processes")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load resources: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def display_table_results(self, results, columns, title):
        """Display results in treeview table"""
        # Clear existing data
        for item in self.analytics_tree.get_children():
            self.analytics_tree.delete(item)
        
        # Configure columns
        self.analytics_tree['columns'] = columns
        self.analytics_tree.column('#0', width=0, stretch=tk.NO)
        
        for col in columns:
            self.analytics_tree.column(col, anchor=tk.W, width=120)
            self.analytics_tree.heading(col, text=col, anchor=tk.W)
        
        # Insert data
        for idx, row in enumerate(results):
            values = [str(row.get(col, '')) for col in columns]
            self.analytics_tree.insert('', 'end', iid=idx, values=values)
    
    def connect_to_database(self):
        """Connect to Neo4j database"""
        try:
            self.status_var.set("Connecting to Neo4j...")
            self.root.update()
            
            if self.visualizer.connect() and self.loader.connect():
                self.status_var.set("Connected to Neo4j ✓")
                self.refresh_processes()
            else:
                self.status_var.set("Failed to connect to Neo4j")
                messagebox.showerror("Connection Error", 
                                   "Could not connect to Neo4j database")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def refresh_processes(self):
        """Refresh list of processes from database"""
        try:
            self.status_var.set("Loading processes...")
            self.root.update()
            
            self.processes = self.visualizer.get_all_processes()
            
            process_names = [f"{p['id']}" for p in self.processes]
            self.process_combo['values'] = process_names
            
            self.status_var.set(f"Loaded {len(self.processes)} processes")
        except Exception as e:
            self.status_var.set(f"Error loading processes: {str(e)}")
            messagebox.showerror("Error", f"Failed to load processes: {str(e)}")
    
    def load_data_from_neo4j(self):
        """Load/reload all data from Neo4j database"""
        try:
            self.status_var.set("Loading all data from Neo4j...")
            self.root.update()
            
            # Reconnect to database to refresh all data
            if self.visualizer.connect():
                # Clear all cached data
                self.visualizer.processes = {}
                
                # Reload all processes
                self.processes = self.visualizer.get_all_processes()
                
                # Update combo box
                process_names = [f"{p['id']}" for p in self.processes]
                self.process_combo['values'] = process_names
                
                # Clear current view
                self.canvas.delete('all')
                self.stats_text.delete('1.0', tk.END)
                self.query_text.delete('1.0', tk.END)
                self.current_process_id = None
                
                self.status_var.set(f"✓ Data reloaded! {len(self.processes)} processes from Neo4j")
                messagebox.showinfo("Success", f"Data reloaded from Neo4j!\nTotal processes: {len(self.processes)}")
            else:
                self.status_var.set("Failed to reconnect to Neo4j")
                messagebox.showerror("Error", "Could not reconnect to Neo4j database")
                
        except Exception as e:
            self.status_var.set(f"Error reloading data: {str(e)}")
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def on_process_selected(self, event=None):
        """Handle process selection"""
        try:
            selected = self.process_var.get()
            if not selected:
                return
            
            self.current_process_id = selected
            self.status_var.set(f"Loading process: {selected}...")
            self.root.update()
            
            # Reset zoom/pan state
            self.canvas_zoom = 1.0
            self.canvas_offset_x = 0
            self.canvas_offset_y = 0
            self.canvas_drag_start = None
            self.dragging_node = None
            self.node_offsets = {}  # Clear node offsets when loading new process
            
            # Load process data
            self.visualizer.load_process(selected)
            
            # Update statistics
            self.update_statistics(selected)
            
            # Draw process
            self.draw_process(selected)
            
            self.status_var.set(f"Process loaded: {selected}")
        except Exception as e:
            self.status_var.set(f"Error loading process: {str(e)}")
            messagebox.showerror("Error", f"Failed to load process: {str(e)}")
    
    def update_statistics(self, process_id: str):
        """Update statistics panel"""
        try:
            stats = self.visualizer.get_process_statistics(process_id)
            
            self.stats_text.delete('1.0', tk.END)
            
            if stats:
                stats_str = f"""Process: {process_id}
-----------------------------------
Total Nodes: {stats.get('total_nodes', 0)}
Total Edges: {stats.get('total_edges', 0)}

Node Types:
  Start: {stats.get('start_count', 0)}
  End: {stats.get('end_count', 0)}
  Task: {stats.get('task_count', 0)}
  Gateway: {stats.get('gateway_count', 0)}
  Decision: {stats.get('decision_count', 0)}
  Event: {stats.get('event_count', 0)}

Paths (Start→End): {len(self.visualizer.find_paths(process_id))}
Critical Path Length: {len(self.visualizer.find_critical_path(process_id))}
"""
                self.stats_text.insert('1.0', stats_str)
            else:
                self.stats_text.insert('1.0', "No statistics available")
        except Exception as e:
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert('1.0', f"Error loading statistics:\n{str(e)}")
    
    def draw_process(self, process_id: str):
        """Draw process on canvas with zoom/pan support"""
        try:
            self.canvas.delete('all')
            self.canvas_info_label.config(text="Rendering graph...")
            self.root.update_idletasks()
            
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 800
                canvas_height = 500
            
            # Calculate layout
            positions = self.visualizer.calculate_layout(process_id, canvas_width, canvas_height)
            
            if not positions:
                self.canvas.create_text(canvas_width/2, canvas_height/2, 
                                       text="No data to display", font=("Arial", 14))
                self.canvas_info_label.config(text="No nodes to display")
                return
            
            graph_data = self.visualizer.processes[process_id]
            nodes = {n['id']: n for n in graph_data['nodes']}
            edges = graph_data['edges']
            
            # Store node objects for click detection
            self.node_objects = {}
            
            # Draw edges
            for edge in edges:
                source_id = edge['source']
                target_id = edge['target']
                
                if source_id in positions and target_id in positions:
                    source_pos = positions[source_id]
                    target_pos = positions[target_id]
                    
                    # Apply zoom and pan - zoom FIRST, then apply offset
                    x1 = source_pos['x'] + source_pos['width'] / 2
                    y1 = source_pos['y'] + source_pos['height'] / 2
                    x2 = target_pos['x'] + target_pos['width'] / 2
                    y2 = target_pos['y'] + target_pos['height'] / 2
                    
                    x1_scaled = x1 * self.canvas_zoom + self.canvas_offset_x
                    y1_scaled = y1 * self.canvas_zoom + self.canvas_offset_y
                    x2_scaled = x2 * self.canvas_zoom + self.canvas_offset_x
                    y2_scaled = y2 * self.canvas_zoom + self.canvas_offset_y
                    
                    # Draw arrow
                    self.canvas.create_line(x1_scaled, y1_scaled, x2_scaled, y2_scaled, 
                                          arrow=tk.LAST, fill='#555555', width=2)
                    
                    # Draw edge label
                    if edge.get('label'):
                        mid_x = (x1_scaled + x2_scaled) / 2
                        mid_y = (y1_scaled + y2_scaled) / 2
                        label_text = str(edge['label'])[:15]
                        
                        self.canvas.create_text(mid_x, mid_y - 15, 
                                              text=label_text,
                                              font=("Arial", 8, "bold"), 
                                              fill='#333333',
                                              anchor='center')
            
            # Draw nodes
            for node_id, node in nodes.items():
                if node_id not in positions:
                    continue
                
                pos = positions[node_id]
                color = self.visualizer.get_node_color(node['type'])
                
                # Apply zoom and pan - zoom FIRST, then apply offset
                x = pos['x'] * self.canvas_zoom + self.canvas_offset_x
                y = pos['y'] * self.canvas_zoom + self.canvas_offset_y
                
                # Apply node-specific offset if dragging this node
                if node_id in self.node_offsets:
                    x += self.node_offsets[node_id][0]
                    y += self.node_offsets[node_id][1]
                
                w = pos['width'] * self.canvas_zoom
                h = pos['height'] * self.canvas_zoom
                
                # Draw rectangle
                rect = self.canvas.create_rectangle(
                    x, y, x + w, y + h,
                    fill=color, outline='#333333', width=2, tags='node'
                )
                
                # Create text label - full text, no truncation
                text_x = x + w / 2
                text_y = y + h / 2
                text = self.canvas.create_text(
                    text_x, text_y,
                    text=node['name'],  # Full text
                    font=("Arial", 7, "bold"),
                    fill='white', tags='node',
                    justify='center',
                    width=int(w) if w > 30 else 0
                )
                
                # Store node object
                self.node_objects[rect] = {
                    'id': node_id,
                    'node': node,
                    'text': text,
                    'pos': (x, y, w, h)
                }
                self.node_objects[text] = self.node_objects[rect]
            
            self.canvas_info_label.config(text="Scroll: Zoom | Drag: Pan | Click: Details")
            
        except Exception as e:
            self.canvas.delete('all')
            error_msg = str(e)[:100]
            self.canvas.create_text(self.canvas.winfo_width()/2, 
                                   self.canvas.winfo_height()/2,
                                   text=f"Error:\n{error_msg}", 
                                   font=("Arial", 11))
            self.logger.error(f"Error drawing process: {e}")
            
        except Exception as e:
            self.canvas.delete('all')
            error_msg = str(e)[:100]
            self.canvas.create_text(self.canvas.winfo_width()/2, 
                                   self.canvas.winfo_height()/2,
                                   text=f"Error:\n{error_msg}", 
                                   font=("Arial", 11))
            self.logger.error(f"Error drawing process: {e}")
    
    def on_canvas_click(self, event):
        """Handle canvas click events - only for nodes, not for drag"""
        # Store initial click position for future checks
        if not hasattr(self, 'click_start'):
            self.click_start = None
        
        # Check if this is actually a click (not a drag)
        # Drag should have already moved canvas_drag_start multiple times
        items = self.canvas.find_closest(event.x, event.y)
        
        if items and items[0] in self.node_objects:
            node_info = self.node_objects[items[0]]
            node = node_info['node']
            
            # Display node info in the right panel instead of popup
            info_text = f"Node Details:\n"
            info_text += f"{'='*40}\n"
            info_text += f"ID: {node['id']}\n"
            info_text += f"Name: {node['name']}\n"
            info_text += f"Type: {node['type']}\n"
            info_text += f"{'='*40}\n\n"
            info_text += "Tip: Use scroll wheel to zoom\n"
            info_text += "Drag to move canvas\n"
            
            self.query_text.delete('1.0', tk.END)
            self.query_text.insert('1.0', info_text)
            self.canvas_info_label.config(text=f"Selected: {node['name']}")
        
        # Clear drag state after release
        self.canvas_drag_start = None
        self.dragging_node = None
    
    def on_canvas_motion(self, event):
        """Handle canvas mouse motion for hover effects"""
        items = self.canvas.find_closest(event.x, event.y)
        
        if items and items[0] in self.node_objects:
            node_info = self.node_objects[items[0]]
            self.canvas_info_label.config(text=f"Node: {node_info['node']['name']}")
        else:
            self.canvas_info_label.config(text="Click on nodes to see details")
    
    def find_paths(self):
        """Find and display all paths from Start to End"""
        try:
            if not self.current_process_id:
                messagebox.showwarning("Warning", "Please select a process first")
                return
            
            self.query_text.delete('1.0', tk.END)
            self.status_var.set("Finding paths...")
            self.root.update()
            
            paths = self.visualizer.find_paths(self.current_process_id)
            
            result = f"Found {len(paths)} paths from Start to End:\n\n"
            
            for i, path in enumerate(paths, 1):
                result += f"Path {i}:\n"
                path_names = [n['name'] for n in path]
                result += " → ".join(path_names[:20])  # Truncate long paths
                if len(path) > 20:
                    result += f" ... (+{len(path) - 20} more nodes)"
                result += f" (Length: {len(path)})\n\n"
            
            self.query_text.insert('1.0', result)
            self.status_var.set(f"Found {len(paths)} paths")
        except Exception as e:
            self.query_text.delete('1.0', tk.END)
            self.query_text.insert('1.0', f"Error finding paths:\n{str(e)}")
    
    def find_bottlenecks(self):
        """Find and display potential bottlenecks"""
        try:
            if not self.current_process_id:
                messagebox.showwarning("Warning", "Please select a process first")
                return
            
            self.query_text.delete('1.0', tk.END)
            self.status_var.set("Finding bottlenecks...")
            self.root.update()
            
            bottlenecks = self.visualizer.find_bottlenecks(self.current_process_id)
            
            result = f"Found {len(bottlenecks)} potential bottlenecks:\n\n"
            
            for bn in bottlenecks:
                node = bn['node']
                degree = bn['in_degree']
                result += f"• {node['name']} ({node['type']})\n"
                result += f"  Incoming paths: {degree}\n\n"
            
            self.query_text.insert('1.0', result)
            self.status_var.set(f"Found {len(bottlenecks)} bottlenecks")
        except Exception as e:
            self.query_text.delete('1.0', tk.END)
            self.query_text.insert('1.0', f"Error finding bottlenecks:\n{str(e)}")
    
    def simulate_workflow(self):
        """Simulate workflow execution step by step"""
        try:
            if not self.current_process_id:
                messagebox.showwarning("Warning", "Please select a process first")
                return
            
            self.query_text.delete('1.0', tk.END)
            paths = self.visualizer.find_paths(self.current_process_id)
            
            if not paths:
                self.query_text.insert('1.0', "No paths found to simulate")
                return
            
            result = f"Workflow Simulation - Process: {self.current_process_id}\n"
            result += "=" * 60 + "\n\n"
            
            for path_idx, path in enumerate(paths, 1):
                result += f"Execution Path {path_idx}:\n"
                result += "-" * 60 + "\n"
                
                total_weight = 0
                for step_idx, node in enumerate(path, 1):
                    result += f"Step {step_idx}: {node['name']}\n"
                    result += f"  Type: {node['type']}\n"
                    result += f"  ID: {node['id']}\n"
                    
                    # Find edge to next node for label/weight
                    if step_idx < len(path):
                        next_node = path[step_idx]
                        edge_data = next((e for e in self.visualizer.processes[self.current_process_id]['edges']
                                        if e['source'] == node['id'] and e['target'] == next_node['id']), None)
                        if edge_data and edge_data.get('label'):
                            result += f"  → Condition: {edge_data['label']}\n"
                    
                    result += "\n"
                
                result += f"Path completed ({len(path)} steps)\n\n"
            
            self.query_text.insert('1.0', result)
            self.status_var.set("Workflow simulation complete")
        except Exception as e:
            self.query_text.delete('1.0', tk.END)
            self.query_text.insert('1.0', f"Error simulating workflow:\n{str(e)}")
    
    def on_canvas_scroll(self, event):
        """Handle canvas zoom via mouse wheel"""
        if event.num == 5 or event.delta < 0:
            # Zoom out
            self.canvas_zoom *= 0.9
        else:
            # Zoom in
            self.canvas_zoom *= 1.1
        
        self.canvas_zoom = max(0.5, min(3.0, self.canvas_zoom))
        self.redraw_canvas()
    
    def on_canvas_drag(self, event):
        """Handle canvas pan via drag or node drag"""
        if self.canvas_drag_start:
            dx = event.x - self.canvas_drag_start[0]
            dy = event.y - self.canvas_drag_start[1]
            
            if self.dragging_node:
                # Dragging a node - update node offset
                if self.dragging_node not in self.node_offsets:
                    self.node_offsets[self.dragging_node] = (0, 0)
                
                prev_dx, prev_dy = self.node_offsets[self.dragging_node]
                self.node_offsets[self.dragging_node] = (prev_dx + dx, prev_dy + dy)
                
                print(f"DEBUG: Dragging node {self.dragging_node} offset=({prev_dx + dx}, {prev_dy + dy})")
            else:
                # Dragging canvas - pan view
                self.canvas_offset_x += dx
                self.canvas_offset_y += dy
                
                print(f"DEBUG: Pan canvas offset=({self.canvas_offset_x:.1f}, {self.canvas_offset_y:.1f})")
            
            self.canvas_drag_start = (event.x, event.y)
            self.redraw_canvas()
    
    def on_canvas_scroll_start(self, event):
        """Initialize canvas drag - check if dragging a node"""
        # Find what was clicked
        items = self.canvas.find_closest(event.x, event.y)
        
        # Check if clicked on a node
        if items and items[0] in self.node_objects:
            # Dragging a node
            node_info = self.node_objects[items[0]]
            self.dragging_node = node_info['id']
        else:
            # Dragging canvas (pan)
            self.dragging_node = None
        
        self.canvas_drag_start = (event.x, event.y)
    
    def on_canvas_scroll_release(self, event):
        """End canvas drag - clear drag state"""
        self.canvas_drag_start = None
    
    def redraw_canvas(self):
        """Redraw canvas with current zoom/pan"""
        if self.current_process_id:
            self.draw_process(self.current_process_id)
            self.root.update_idletasks()  # Force UI update
    
    def export_process(self):
        """Export current process data"""
        try:
            if not self.current_process_id:
                messagebox.showwarning("Warning", "Please select a process first")
                return
            
            from tkinter import filedialog
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                export_data = self.visualizer.export_process_data(
                    self.current_process_id, format='json'
                )
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(export_data)
                
                messagebox.showinfo("Success", f"Process exported to {file_path}")
                self.status_var.set(f"Process exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def on_closing(self):
        """Handle window closing"""
        try:
            self.visualizer.disconnect()
            self.root.destroy()
        except Exception as e:
            print(f"Error closing: {str(e)}")
            self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    dashboard = WorkflowDashboard(root)
    root.protocol("WM_DELETE_WINDOW", dashboard.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
