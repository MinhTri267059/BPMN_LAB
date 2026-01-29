# BPMN Workflow Visualization & Analytics Dashboard

A comprehensive Neo4j-based tool for visualizing and analyzing BPMN (Business Process Model and Notation) workflows with advanced analytics capabilities.

**Live Demo**: Neo4j Workflow Dashboard with interactive visualization and real-time analytics reporting.

---

## 🎯 Features

### Visualization Tab
- **Interactive Graph Rendering**: Display BPMN workflows with node types (Task, Gateway, Event, etc.)
- **Zoom & Pan**: Scroll to zoom, drag to pan across the canvas
- **Node Details**: Click nodes to see properties (ID, Name, Type)
- **Workflow Simulation**: Step-by-step execution path simulation
- **Path Analysis**: Find all Start→End paths, identify bottlenecks
- **Statistics Panel**: View process statistics (node counts, path counts)

### Analytics Tab
- **Task Search**: Find tasks by name (case-insensitive) across all processes
- **Gateway Management**: List all branching points with branch counts
- **Time KPI**: Calculate total execution time per process
- **Cost KPI**: Aggregate personnel costs per process
- **Resource Requirements**: Identify required roles per process

### Data Management
- **Neo4j Integration**: Store and query BPMN graphs at scale
- **Batch Load**: Load multiple workflow definitions from XML files
- **Data Reload**: Refresh data without restarting the application

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Neo4j Server 6.1+** (running on `bolt://localhost:7687`)
- **Git** (for cloning)

### Installation

#### 1. Clone Repository
```bash
git clone https://github.com/MinhTri267059/BPMN_LAB.git
cd BPMN_LAB
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Neo4j
Make sure Neo4j is running:
```bash
# Neo4j connection details (default)
URI: bolt://localhost:7687
Username: neo4j
Password: password
```

To change connection settings, edit `neo4j_loader.py` line 12-14:
```python
def __init__(self, uri: str = "bolt://localhost:7687", 
             username: str = "neo4j", 
             password: str = "password"):
```

#### 5. Load Sample Data (Optional)
The project includes sample BPMN workflows:
- `Account.xml` - Account Management Process
- `Content.xml` - Content Creation Process
- `Media.xml` - Media Production Process
- `Ads.xml` - Advertisement Campaign Process
- `Team Marketing.xml` - Marketing Team Coordination

To load data into Neo4j:
```bash
python launcher.py
```

#### 6. Run Dashboard
```bash
python dashboard.py
```

The dashboard will open at `http://localhost:8000` or in a Tkinter window.

---

## 📖 Usage Guide

### Dashboard Overview

#### Process Control Panel
- **Select Process**: Choose a process from the dropdown
- **Refresh**: Reload process list from Neo4j
- **Load Data from Neo4j**: Reload all data from database
- **Export**: Export current process as JSON

#### Visualization Tab
1. **Select a process** from the dropdown
2. **View workflow diagram** with interactive features:
   - Scroll wheel: Zoom in/out
   - Drag: Pan across canvas
   - Click node: View node details
3. **Run queries**:
   - "Find Paths (Start→End)": List all execution paths
   - "Find Bottlenecks": Identify nodes with high convergence
   - "Simulate Flow": Execute workflow step-by-step
4. **Statistics panel**: Shows node counts and path information

#### Analytics Tab

##### 1. Task Search
- Enter task name in search box (case-insensitive)
- Click "Search" button
- Results show: Process ID, Process Name, Task Name
- **Example**: Search "content" → finds all tasks containing "content"

##### 2. Gateway Management
- Click "Gateway Management" button
- View all branching points with:
  - Gateway Name
  - Number of branches
  - Associated processes
- **Use case**: Identify decision points in workflows

##### 3. Time KPI
- Click "Time KPI" button
- View total execution time per process (in hours and minutes)
- **Use case**: Identify time-consuming processes

##### 4. Cost KPI
- Click "Cost KPI" button
- View personnel costs aggregated per process
- **Use case**: Budget planning and cost analysis

##### 5. Resources
- Click "Resources" button
- View required roles per process
- **Use case**: Resource planning and staffing requirements

---

## 🏗️ Project Structure

```
BPMN_LAB/
├── dashboard.py              # Main Tkinter GUI application
├── neo4j_loader.py          # Neo4j database connector + analytics queries
├── neo4j_visualizer.py      # Graph layout & visualization engine
├── launcher.py              # Data loading entry point
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore patterns
├── README.md               # This file
│
├── Sample BPMN Files (XML):
├── Account.xml
├── Content.xml
├── Media.xml
├── Ads.xml
└── Team Marketing.xml
```

### Core Modules

#### `neo4j_loader.py` (614 lines)
- **Neo4jLoader class**: Database connection and operations
- **Methods**:
  - `connect()`: Establish database connection
  - `create_process_graph()`: Create BPMN graph in Neo4j
  - `find_task_in_processes()`: Task search query
  - `list_all_gateways()`: Gateway analysis query
  - `get_process_time_kpi()`: Time aggregation query
  - `get_process_cost_kpi()`: Cost aggregation query
  - `get_process_resource_requirements()`: Role requirement query
  - `find_paths()`: Path finding algorithm
  - `find_critical_path()`: Critical path analysis

#### `neo4j_visualizer.py` (354 lines)
- **Neo4jVisualizer class**: Visualization logic
- **Methods**:
  - `calculate_layout()`: BFS-based node positioning
  - `find_paths()`: Path enumeration
  - `find_bottlenecks()`: Node convergence analysis
  - `export_process_data()`: JSON/Cypher export

#### `dashboard.py` (845 lines)
- **WorkflowDashboard class**: Tkinter GUI
- **Tabs**:
  - Visualization: Interactive graph + workflow analysis
  - Analytics: Business intelligence queries
- **Methods**:
  - `setup_ui()`: Initialize UI components
  - `on_process_selected()`: Load selected process
  - `show_*()`: Analytics report methods
  - `draw_process()`: Render graph on canvas

---

## 🗄️ Database Schema

### Neo4j Graph Model

```
(Process) -[:HAS_STEP]-> (Element)
```

**Process Node**:
```
{
  id: "BP1",
  name: "Account"
}
```

**Element Node** (Task, Gateway, Event, Start, End):
```
{
  id: "unique-id",
  name: "Task name",
  type: "Task|Gateway|Event|Start|End",
  time: 60,        # minutes (optional)
  cost: 150,       # USD (optional)
  role: "Account"  # role/department (optional)
}
```

**Relationship**: `:NEXT` (between elements)
```
(Element) -[:NEXT]-> (Element)
```

---

## 📊 Analytics Queries

All queries are implemented in `Neo4jLoader` class:

### Query 1: Task Search
```cypher
MATCH (p:Process)-[:HAS_STEP]->(e:Element)
WHERE toLower(e.name) CONTAINS toLower($task_name) AND e.type = 'Task'
RETURN p.id, p.name, e.name
```

### Query 2: Gateway Management
```cypher
MATCH (p:Process)-[:HAS_STEP]->(e:Element)
WHERE e.type IN ['Gateway', 'Event']
OPTIONAL MATCH (e)-[:NEXT]->(next_e:Element)
WITH p, e, count(DISTINCT next_e) as branch_count
WHERE branch_count > 0
RETURN p.id, e.name, branch_count
```

### Query 3: Time KPI
```cypher
MATCH (p:Process)-[:HAS_STEP]->(e:Element)
WITH p, sum(COALESCE(e.time, 0)) as total_minutes
WITH p, total_minutes, round(total_minutes / 60.0, 2) as total_hours
RETURN p.id, p.name, total_minutes, total_hours
ORDER BY total_hours DESC
```

### Query 4: Cost KPI
```cypher
MATCH (p:Process)-[:HAS_STEP]->(e:Element)
WITH p, sum(COALESCE(e.cost, 0)) as total_cost
RETURN p.id, p.name, total_cost
ORDER BY total_cost DESC
```

### Query 5: Resource Requirements
```cypher
MATCH (p:Process)-[:HAS_STEP]->(e:Element)
WHERE e.role IS NOT NULL AND e.role <> 'System' AND e.role <> 'Start' AND e.role <> 'End'
WITH p, collect(DISTINCT e.role) as required_roles
RETURN p.id, p.name, required_roles, size(required_roles) as role_count
```

---

## 🔧 Configuration

### Neo4j Connection
Edit connection parameters in `neo4j_loader.py`:
```python
loader = Neo4jLoader(
    uri="bolt://localhost:7687",
    username="neo4j",
    password="password"
)
```

### Canvas Settings
Edit visualization settings in `dashboard.py`:
```python
# Canvas dimensions
self.root.geometry("1400x900")

# Zoom limits
self.canvas_zoom = max(0.5, min(3.0, self.canvas_zoom))
```

---

## 🐛 Troubleshooting

### Neo4j Connection Failed
```
Error: Could not connect to Neo4j database
```
**Solution**: 
1. Check Neo4j server is running: `neo4j status`
2. Verify credentials in `neo4j_loader.py`
3. Check firewall allows port 7687

### No Data Displayed
```
Error: No statistics available
```
**Solution**:
1. Click "Load Data from Neo4j" button
2. Or run `python launcher.py` to load sample data
3. Check Neo4j has data: `neo4j console` → `MATCH (n) RETURN count(n)`

### UI Issues
```
Tkinter window not opening / elements not showing
```
**Solution**:
1. Restart dashboard: `python dashboard.py`
2. Check Python version: `python --version` (need 3.11+)
3. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

---

## 📝 Requirements

```
neo4j==6.1.0
tkinter (included with Python)
```

**System Requirements**:
- Python 3.11+
- 500MB disk space
- 2GB RAM (minimum)
- Neo4j Server 6.1+ running locally

---

## 🤝 Contributing

To contribute to BPMN_LAB:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👤 Author

**Trương Minh Trí** (@MinhTri267059)  
Email: [contact@example.com]  
GitHub: https://github.com/MinhTri267059

---

## 🎓 Sample Data

The project includes 5 sample BPMN workflows in Vietnamese (Marketing processes):

1. **Account Process** (BP1): Account management workflow
2. **Content Process** (BP2): Content creation and approval
3. **Media Process** (BP3): Media production with feedback loops
4. **Ads Process** (BP4): Advertisement campaign management
5. **Team Marketing** (BP5): Cross-functional marketing coordination

Each workflow demonstrates different BPMN elements (Tasks, Gateways, Events).

---

## 🔗 Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [BPMN 2.0 Standard](https://www.omg.org/bpmn/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/)

---

## 📞 Support

For issues and questions:
1. Check README and troubleshooting section above
2. Review existing GitHub Issues
3. Create new Issue with detailed description
4. Include logs from console output

---

**Last Updated**: January 29, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅
