"""
Neo4j Visualizer Module
Fetches data from Neo4j and prepares it for Tkinter canvas visualization
"""

from neo4j_loader import Neo4jLoader
from typing import Dict, List, Tuple, Optional
import logging


class Neo4jVisualizer:
    """
    Handles Neo4j data fetching and visualization preparation
    """
    
    def __init__(self, neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j",
                 neo4j_pass: str = "password"):
        """
        Initialize Neo4j Visualizer
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_pass: Neo4j password
        """
        self.loader = Neo4jLoader(uri=neo4j_uri, username=neo4j_user, password=neo4j_pass)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        self.connected = False
        self.processes = {}
        self.current_process = None
    
    def connect(self) -> bool:
        """Connect to Neo4j database"""
        self.connected = self.loader.connect()
        return self.connected
    
    def disconnect(self) -> None:
        """Disconnect from Neo4j"""
        self.loader.close()
        self.connected = False
    
    def get_all_processes(self) -> List[Dict]:
        """Get list of all processes in database"""
        if not self.connected:
            return []
        
        processes = self.loader.get_all_processes()
        return processes
    
    def load_process(self, process_id: str) -> Optional[Dict]:
        """
        Load a specific process data for visualization
        
        Args:
            process_id: Process ID to load
            
        Returns:
            Dictionary with nodes and edges data
        """
        if not self.connected:
            return None
        
        graph_data = self.loader.get_graph_data(process_id)
        self.current_process = process_id
        self.processes[process_id] = graph_data
        
        return graph_data
    
    def calculate_layout(self, process_id: str, canvas_width: int = 1200, 
                        canvas_height: int = 600) -> Dict:
        """
        Calculate simple grid layout - left to right, top to bottom
        Ensures no skew/tilt, all text visible
        
        Args:
            process_id: Process ID
            canvas_width: Canvas width
            canvas_height: Canvas height
            
        Returns:
            Dictionary with node positions
        """
        if process_id not in self.processes:
            return {}
        
        try:
            graph_data = self.processes[process_id]
            nodes = graph_data['nodes']
            edges = graph_data['edges']
            
            if not nodes:
                return {}
            
            # Build adjacency list
            adjacency = {n['id']: [] for n in nodes}
            for edge in edges:
                adjacency[edge['source']].append(edge['target'])
            
            # Find start nodes
            start_nodes = [n['id'] for n in nodes if n['type'] in ['Start', 'Event']]
            if not start_nodes:
                start_nodes = [nodes[0]['id']]
            
            # BFS for levels
            node_levels = {}
            queue = list(start_nodes)
            for n in start_nodes:
                node_levels[n] = 0
            
            visited = set()
            max_iter = len(nodes) * 2
            iter_count = 0
            
            while queue and iter_count < max_iter:
                iter_count += 1
                current = queue.pop(0)
                
                if current in visited:
                    continue
                visited.add(current)
                
                current_level = node_levels.get(current, 0)
                for next_node in adjacency.get(current, []):
                    next_level = current_level + 1
                    if next_node not in node_levels or node_levels[next_node] < next_level:
                        node_levels[next_node] = next_level
                        if next_node not in queue:
                            queue.append(next_node)
            
            # Group by level
            levels = {}
            for node_id, level in node_levels.items():
                if level not in levels:
                    levels[level] = []
                levels[level].append(node_id)
            
            positions = {}
            
            if not levels:
                # Simple grid if no levels
                cols = max(3, int((len(nodes) ** 0.5)) + 1)
                for i, node in enumerate(nodes):
                    col = i % cols
                    row = i // cols
                    positions[node['id']] = {
                        'x': 50 + col * 180,
                        'y': 50 + row * 120,
                        'width': 120,
                        'height': 60
                    }
            else:
                # Level-based layout
                margin_x = 40
                margin_y = 50
                node_width = 120
                node_height = 60
                h_spacing = 170
                v_spacing = 100
                
                for level in sorted(levels.keys()):
                    node_ids = levels[level]
                    x = margin_x + level * h_spacing
                    
                    # Distribute vertically
                    total_height = len(node_ids) * (node_height + v_spacing)
                    start_y = margin_y + (canvas_height - 2 * margin_y - total_height) / 2
                    
                    for idx, node_id in enumerate(node_ids):
                        y = start_y + idx * (node_height + v_spacing)
                        positions[node_id] = {
                            'x': x,
                            'y': y,
                            'width': node_width,
                            'height': node_height
                        }
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Layout error: {e}")
            # Grid fallback
            positions = {}
            cols = 3
            for i, node in enumerate(graph_data['nodes']):
                positions[node['id']] = {
                    'x': 50 + (i % cols) * 250,
                    'y': 50 + (i // cols) * 120,
                    'width': 120,
                    'height': 60
                }
            return positions
    
    def get_node_color(self, node_type: str) -> str:
        """Get color based on node type"""
        color_map = {
            'Start': '#2ecc71',      # Green
            'End': '#e74c3c',        # Red
            'Task': '#3498db',       # Blue
            'Gateway': '#f39c12',    # Orange
            'Decision': '#9b59b6',   # Purple
            'Event': '#1abc9c'       # Turquoise
        }
        return color_map.get(node_type, '#95a5a6')  # Gray default
    
    def get_process_statistics(self, process_id: str) -> Optional[Dict]:
        """Get statistics for a process"""
        if not self.connected:
            return None
        
        return self.loader.get_process_statistics(process_id)
    
    def find_paths(self, process_id: str) -> List[List[Dict]]:
        """Find all paths from Start to End"""
        if not self.connected:
            return []
        
        return self.loader.find_paths('Start', 'End', process_id)
    
    def find_critical_path(self, process_id: str) -> List[Dict]:
        """
        Find the longest path (critical path) in the workflow
        
        Args:
            process_id: Process ID
            
        Returns:
            List of nodes in critical path
        """
        if process_id not in self.processes:
            return []
        
        paths = self.find_paths(process_id)
        if not paths:
            return []
        
        # Return the longest path
        longest_path = max(paths, key=len) if paths else []
        return longest_path
    
    def get_edge_data(self, process_id: str) -> List[Dict]:
        """Get edge information for a process"""
        if process_id not in self.processes:
            return []
        
        return self.processes[process_id]['edges']
    
    def find_bottlenecks(self, process_id: str) -> List[Dict]:
        """
        Find potential bottlenecks (nodes with high in-degree)
        
        Args:
            process_id: Process ID
            
        Returns:
            List of potential bottleneck nodes
        """
        if process_id not in self.processes:
            return []
        
        graph_data = self.processes[process_id]
        edges = graph_data['edges']
        nodes = {n['id']: n for n in graph_data['nodes']}
        
        # Count incoming edges
        in_degree = {}
        for edge in edges:
            target = edge['target']
            in_degree[target] = in_degree.get(target, 0) + 1
        
        # Find bottlenecks (in_degree > 1)
        bottlenecks = []
        for node_id, degree in in_degree.items():
            if degree > 1 and node_id in nodes:
                bottlenecks.append({
                    'node': nodes[node_id],
                    'in_degree': degree
                })
        
        # Sort by degree descending
        bottlenecks.sort(key=lambda x: x['in_degree'], reverse=True)
        return bottlenecks
    
    def find_parallel_paths(self, process_id: str) -> List[List[Dict]]:
        """
        Find parallel execution paths (branches from gateway nodes)
        
        Args:
            process_id: Process ID
            
        Returns:
            List of parallel path groups
        """
        if process_id not in self.processes:
            return []
        
        graph_data = self.processes[process_id]
        edges = graph_data['edges']
        
        # Find gateway nodes with multiple outgoing edges
        outgoing = {}
        for edge in edges:
            source = edge['source']
            if source not in outgoing:
                outgoing[source] = []
            outgoing[source].append(edge['target'])
        
        # Find gateways with branching
        parallel_paths = []
        for source, targets in outgoing.items():
            if len(targets) > 1:
                parallel_paths.append(targets)
        
        return parallel_paths
    
    def export_process_data(self, process_id: str, format: str = 'dict') -> Optional[Dict]:
        """
        Export process data in various formats
        
        Args:
            process_id: Process ID
            format: Export format ('dict', 'json', 'csv')
            
        Returns:
            Exported data
        """
        if process_id not in self.processes:
            return None
        
        graph_data = self.processes[process_id]
        
        if format == 'dict':
            return graph_data
        
        elif format == 'json':
            import json
            return json.dumps(graph_data, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            # Export as CSV (nodes and edges)
            nodes_csv = "ID,Name,Type\n"
            for node in graph_data['nodes']:
                nodes_csv += f"{node['id']},{node['name']},{node['type']}\n"
            
            edges_csv = "Source,Target,Label\n"
            for edge in graph_data['edges']:
                nodes_csv += f"{edge['source']},{edge['target']},{edge.get('label', '')}\n"
            
            return {'nodes': nodes_csv, 'edges': edges_csv}
        
        return None
