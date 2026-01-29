from typing import Dict, List, Optional, Any
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
import logging


class Neo4jLoader:
    """
    Neo4j Graph Database Loader for BPMN Workflow Processes.
    Handles connection, graph creation, and complex queries.
    """
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 username: str = "neo4j", 
                 password: str = "password"):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j bolt URI (default: localhost:7687)
            username: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        self.session = None
        
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
    
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                encrypted=False
            )
            
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            
            self.logger.info(f"✅ Connected to Neo4j: {self.uri}")
            return True
            
        except AuthError as e:
            self.logger.error(f"❌ Authentication failed: {e}")
            return False
        except ServiceUnavailable as e:
            self.logger.error(f"❌ Neo4j service unavailable: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Connection error: {e}")
            return False
    
    def close(self) -> None:
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.logger.info("Neo4j connection closed")
    
    def clear_database(self) -> bool:
        """
        Clear all nodes and relationships from database.
        Use with caution!
        
        Returns:
            True if successful
        """
        try:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            
            self.logger.info("✅ Database cleared")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error clearing database: {e}")
            return False
    
    def create_process_graph(self, process_id: str, process_name: str, 
                            nodes: List[Dict], edges: List[Dict]) -> bool:
        """
        Create process graph in Neo4j.
        Creates Process node, Element nodes, and relationships.
        
        Args:
            process_id: Unique process identifier
            process_name: Human-readable process name
            nodes: List of node dictionaries with id, name, type
            edges: List of edge dictionaries with source, target, label
            
        Returns:
            True if successful
        """
        try:
            with self.driver.session() as session:
                # Create Process node
                session.run(
                    """
                    MERGE (p:Process {process_id: $process_id})
                    SET p.name = $process_name
                    """,
                    process_id=process_id,
                    process_name=process_name
                )
                
                # Create Element nodes
                for node in nodes:
                    session.run(
                        """
                        MERGE (e:Element {element_id: $element_id})
                        SET e.name = $name,
                            e.type = $type,
                            e.process_id = $process_id
                        WITH e
                        MATCH (p:Process {process_id: $process_id})
                        MERGE (p)-[:HAS_STEP]->(e)
                        """,
                        element_id=node['id'],
                        name=node['name'],
                        type=node['type'],
                        process_id=process_id
                    )
                
                # Create relationships between elements (edges)
                for edge in edges:
                    source_id = edge['source']
                    target_id = edge['target']
                    edge_label = edge.get('label', '')
                    
                    session.run(
                        """
                        MATCH (source:Element {element_id: $source_id, process_id: $process_id})
                        MATCH (target:Element {element_id: $target_id, process_id: $process_id})
                        MERGE (source)-[r:NEXT {process_id: $process_id}]->(target)
                        SET r.label = $label
                        """,
                        source_id=source_id,
                        target_id=target_id,
                        process_id=process_id,
                        label=edge_label
                    )
                
                self.logger.info(f"✅ Created process graph: {process_name} (ID: {process_id})")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Error creating process graph: {e}")
            return False
    
    # ==================== QUERY METHODS ====================
    
    def find_process_with_task(self, task_name: str) -> List[Dict]:
        """
        Find which Process(es) contain a specific task.
        
        Args:
            task_name: Name of the task to search for
            
        Returns:
            List of dictionaries with process and task information
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (p:Process)-[:HAS_STEP]->(e:Element)
                    WHERE e.type = 'Task' AND e.name CONTAINS $task_name
                    RETURN p.process_id as process_id, 
                           p.name as process_name,
                           e.element_id as task_id,
                           e.name as task_name
                    """,
                    task_name=task_name
                )
                
                records = result.data()
                if records:
                    self.logger.info(f"✅ Found {len(records)} process(es) with task '{task_name}'")
                else:
                    self.logger.info(f"⚠️  No processes found with task '{task_name}'")
                
                return records
                
        except Exception as e:
            self.logger.error(f"❌ Error finding task: {e}")
            return []
    
    def find_paths(self, start_node_type: str, end_node_type: str, 
                   process_id: str) -> List[List[Dict]]:
        """
        Find all paths from Start to End nodes in a specific process.
        Returns all complete paths through the workflow.
        
        Args:
            start_node_type: Type of start node (e.g., 'Start', 'Event')
            end_node_type: Type of end node (e.g., 'End')
            process_id: Process ID to search in
            
        Returns:
            List of paths, where each path is a list of nodes
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (p:Process {process_id: $process_id})
                    MATCH (start:Element {process_id: $process_id, type: $start_type})
                    MATCH (end:Element {process_id: $process_id, type: $end_type})
                    MATCH path = (start)-[:NEXT*]->(end)
                    RETURN path
                    """,
                    process_id=process_id,
                    start_type=start_node_type,
                    end_type=end_node_type
                )
                
                records = list(result)
                
                # Extract path information
                paths = []
                for record in records:
                    path = record['path']
                    path_nodes = []
                    for node in path.nodes:
                        path_nodes.append({
                            'id': node['element_id'],
                            'name': node['name'],
                            'type': node['type']
                        })
                    paths.append(path_nodes)
                
                self.logger.info(f"✅ Found {len(paths)} path(s) from {start_node_type} to {end_node_type}")
                
                return paths
                
        except Exception as e:
            self.logger.error(f"❌ Error finding paths: {e}")
            return []
    
    def get_graph_data(self, process_id: str) -> Dict:
        """
        Retrieve all nodes and relationships for a specific process.
        Used for visualization or further analysis.
        
        Args:
            process_id: Process ID to retrieve
            
        Returns:
            Dictionary with nodes and relationships
        """
        try:
            with self.driver.session() as session:
                # Get all nodes
                nodes_result = session.run(
                    """
                    MATCH (p:Process {process_id: $process_id})-[:HAS_STEP]->(e:Element)
                    RETURN e.element_id as id,
                           e.name as name,
                           e.type as type
                    """,
                    process_id=process_id
                )
                
                nodes = nodes_result.data()
                
                # Get all relationships
                edges_result = session.run(
                    """
                    MATCH (e1:Element {process_id: $process_id})-[r:NEXT]->(e2:Element {process_id: $process_id})
                    RETURN e1.element_id as source,
                           e2.element_id as target,
                           r.label as label
                    """,
                    process_id=process_id
                )
                
                edges = edges_result.data()
                
                # Get process info
                process_result = session.run(
                    """
                    MATCH (p:Process {process_id: $process_id})
                    RETURN p.name as name
                    """,
                    process_id=process_id
                )
                
                process_data = process_result.single()
                process_name = process_data['name'] if process_data else process_id
                
                graph_data = {
                    'process_id': process_id,
                    'process_name': process_name,
                    'nodes': nodes,
                    'edges': edges
                }
                
                self.logger.info(f"✅ Retrieved graph data for process '{process_name}': {len(nodes)} nodes, {len(edges)} edges")
                
                return graph_data
                
        except Exception as e:
            self.logger.error(f"❌ Error retrieving graph data: {e}")
            return {'process_id': process_id, 'nodes': [], 'edges': []}
    
    # ==================== UTILITY QUERIES ====================
    
    def get_all_processes(self) -> List[Dict]:
        """Get all processes in the database."""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (p:Process)
                    RETURN p.process_id as process_id,
                           p.name as process_name
                    ORDER BY p.name
                    """
                )
                
                return result.data()
                
        except Exception as e:
            self.logger.error(f"❌ Error getting processes: {e}")
            return []
    
    def get_process_statistics(self, process_id: str) -> Dict:
        """Get statistics about a process."""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (p:Process {process_id: $process_id})-[:HAS_STEP]->(e:Element)
                    WITH p, e, e.type as type
                    RETURN p.name as process_name,
                           count(e) as total_elements,
                           sum(CASE WHEN type = 'Start' THEN 1 ELSE 0 END) as start_nodes,
                           sum(CASE WHEN type = 'End' THEN 1 ELSE 0 END) as end_nodes,
                           sum(CASE WHEN type = 'Task' THEN 1 ELSE 0 END) as task_nodes,
                           sum(CASE WHEN type = 'Gateway' THEN 1 ELSE 0 END) as gateway_nodes
                    """,
                    process_id=process_id
                )
                
                record = result.single()
                return record if record else {}
                
        except Exception as e:
            self.logger.error(f"❌ Error getting statistics: {e}")
            return {}
    
    def delete_process(self, process_id: str) -> bool:
        """Delete a specific process and all its elements."""
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (p:Process {process_id: $process_id})
                    DETACH DELETE p
                    """,
                    process_id=process_id
                )
                
                self.logger.info(f"✅ Deleted process: {process_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Error deleting process: {e}")
            return False
    
    def get_all_processes(self) -> List[Dict]:
        """
        Get list of all processes in the database.
        
        Returns:
            List of process dictionaries with id and metadata
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (p:Process)
                    OPTIONAL MATCH (p)-[:HAS_STEP]->(e:Element)
                    WITH p, count(e) as node_count
                    RETURN p.process_id as id, p.name as name, node_count
                    ORDER BY p.process_id
                    """
                )
                
                processes = []
                for record in result:
                    processes.append({
                        'id': record['id'],
                        'name': record['name'],
                        'node_count': record['node_count']
                    })
                
                return processes
                
        except Exception as e:
            self.logger.error(f"❌ Error getting all processes: {e}")
            return []
    
    def get_process_statistics(self, process_id: str) -> Optional[Dict]:
        """
        Get detailed statistics for a specific process.
        
        Args:
            process_id: Process ID
            
        Returns:
            Dictionary with process statistics
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (p:Process {process_id: $process_id})-[:HAS_STEP]->(e:Element)
                    RETURN 
                        count(e) as total_nodes,
                        count(CASE WHEN e.type = 'Start' THEN 1 END) as start_count,
                        count(CASE WHEN e.type = 'End' THEN 1 END) as end_count,
                        count(CASE WHEN e.type = 'Task' THEN 1 END) as task_count,
                        count(CASE WHEN e.type = 'Gateway' THEN 1 END) as gateway_count,
                        count(CASE WHEN e.type = 'Decision' THEN 1 END) as decision_count,
                        count(CASE WHEN e.type = 'Event' THEN 1 END) as event_count
                    """,
                    process_id=process_id
                )
                
                record = result.single()
                if record:
                    stats = {
                        'total_nodes': record['total_nodes'],
                        'start_count': record['start_count'],
                        'end_count': record['end_count'],
                        'task_count': record['task_count'],
                        'gateway_count': record['gateway_count'],
                        'decision_count': record['decision_count'],
                        'event_count': record['event_count']
                    }
                    
                    # Get edge count
                    edges_result = session.run(
                        """
                        MATCH (p:Process {process_id: $process_id})-[:HAS_STEP]->(e:Element)-[r:NEXT]-()
                        RETURN count(r) as total_edges
                        """,
                        process_id=process_id
                    )
                    
                    edge_record = edges_result.single()
                    if edge_record:
                        stats['total_edges'] = edge_record['total_edges']
                    else:
                        stats['total_edges'] = 0
                    
                    return stats
                
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error getting process statistics: {e}")
            return None    
    # ==================== ANALYTICS QUERIES ====================
    
    def find_task_in_processes(self, task_name: str) -> List[Dict]:
        """
        Query 1: Find which processes contain a specific task
        
        Args:
            task_name: Name or partial name of task to search
            
        Returns:
            List of dicts: {process_id, process_name, task_id, task_name}
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (p:Process)-[:HAS_STEP]->(e:Element)
                    WHERE toLower(e.name) CONTAINS toLower($task_name) AND e.type = 'Task'
                    RETURN DISTINCT 
                        p.id as process_id, 
                        p.name as process_name, 
                        e.name as task_id, 
                        e.name as task_name
                    ORDER BY p.id
                """, task_name=task_name)
                
                return [dict(record) for record in result]
        except Exception as e:
            self.logger.error(f"❌ Error in find_task_in_processes: {e}")
            return []
    
    def list_all_gateways(self) -> List[Dict]:
        """
        Query 2: List all branching points (gateways) in each process
        
        Returns:
            List of dicts: {process_id, process_name, gateway_id, gateway_name, branch_count}
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (p:Process)-[:HAS_STEP]->(e:Element)
                    WHERE e.type IN ['Gateway', 'Event']
                    OPTIONAL MATCH (e)-[:NEXT]->(next_e:Element)
                    WITH p, e, count(DISTINCT next_e) as branch_count
                    WHERE branch_count > 0
                    RETURN 
                        p.id as process_id,
                        p.name as process_name,
                        e.name as gateway_id,
                        e.name as gateway_name,
                        branch_count
                    ORDER BY p.id, e.name
                """)
                
                return [dict(record) for record in result]
        except Exception as e:
            self.logger.error(f"❌ Error in list_all_gateways: {e}")
            return []
    
    def get_process_time_kpi(self) -> List[Dict]:
        """
        Query 3: Calculate total execution time for each process in hours
        
        Returns:
            List of dicts: {process_id, process_name, total_minutes, total_hours}
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (p:Process)-[:HAS_STEP]->(e:Element)
                    WITH p, sum(COALESCE(e.time, 0)) as total_minutes
                    WITH p, total_minutes, round(total_minutes / 60.0, 2) as total_hours
                    RETURN 
                        p.id as process_id,
                        p.name as process_name,
                        total_minutes,
                        total_hours
                    ORDER BY total_hours DESC
                """)
                
                return [dict(record) for record in result]
        except Exception as e:
            self.logger.error(f"❌ Error in get_process_time_kpi: {e}")
            return []
    
    def get_process_cost_kpi(self) -> List[Dict]:
        """
        Query 4: Calculate total cost for each process
        Uses WITH clause for proper aggregation and ordering
        
        Returns:
            List of dicts: {process_id, process_name, total_cost}
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (p:Process)-[:HAS_STEP]->(e:Element)
                    WITH p, sum(COALESCE(e.cost, 0)) as total_cost
                    WITH p, total_cost
                    RETURN 
                        p.id as process_id,
                        p.name as process_name,
                        total_cost
                    ORDER BY total_cost DESC
                """)
                
                return [dict(record) for record in result]
        except Exception as e:
            self.logger.error(f"❌ Error in get_process_cost_kpi: {e}")
            return []
    
    def get_process_resource_requirements(self) -> List[Dict]:
        """
        Query 5: List unique roles required for each process
        Excludes system roles (System, Start, End)
        
        Returns:
            List of dicts: {process_id, process_name, required_roles, role_count}
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (p:Process)-[:HAS_STEP]->(e:Element)
                    WHERE e.role IS NOT NULL 
                      AND e.role <> 'System' 
                      AND e.role <> 'Start' 
                      AND e.role <> 'End'
                    WITH p, collect(DISTINCT e.role) as required_roles
                    RETURN 
                        p.id as process_id,
                        p.name as process_name,
                        required_roles,
                        size(required_roles) as role_count
                    ORDER BY p.id
                """)
                
                return [dict(record) for record in result]
        except Exception as e:
            self.logger.error(f"❌ Error in get_process_resource_requirements: {e}")
            return []
    
    def disconnect(self) -> None:
        """Alias for close() - disconnect from Neo4j."""
        self.close()
    
    def close_connection(self) -> None:
        """Alias for close() - close Neo4j connection."""
        self.close()