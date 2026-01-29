# 📚 BPMN Workflow Dashboard - Setup & Usage Guide

## 🎯 Overview

**BPMN_LAB** is a professional Neo4j-powered workflow visualization and analytics platform built with Python and Tkinter. It's designed for analyzing, visualizing, and reporting on BPMN (Business Process Model and Notation) workflows.

### What It Does
- 📊 Visualizes complex workflows as interactive graphs
- 🔍 Provides advanced analytics and reporting
- 💾 Stores workflows in Neo4j graph database
- 📈 Calculates KPIs (time, cost, resources)
- 🎯 Finds critical paths and bottlenecks

---

## 💻 System Requirements

| Requirement | Version/Details |
|---|---|
| **OS** | Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+) |
| **Python** | 3.11+ |
| **Neo4j** | 6.1+ |
| **RAM** | 2GB minimum, 4GB recommended |
| **Disk** | 500MB for application + database |
| **Network** | Internet (for dependencies), Local access to Neo4j |

---

## 🔧 Installation Guide

### Step 1: Install Python 3.11+

#### Windows
1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ **Check**: "Add Python to PATH"
4. Verify: `python --version` (should show 3.11+)

#### macOS
```bash
brew install python@3.11
python3 --version  # Verify
```

#### Linux (Ubuntu)
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
python3.11 --version  # Verify
```

### Step 2: Install Neo4j Server

#### Windows
1. Download Neo4j Desktop from https://neo4j.com/download/
2. Install and launch
3. Create a new project and database
4. Start the database (default port: 7687)
5. Set password (default: `password`)

#### macOS
```bash
brew install neo4j
neo4j start
```

#### Linux (Docker - Recommended)
```bash
docker run -d \
  --name neo4j \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:6.1
```

**Verify Neo4j is running**:
```bash
curl bolt://localhost:7687
# Should connect successfully
```

### Step 3: Clone Repository

#### Using Git
```bash
git clone https://github.com/MinhTri267059/BPMN_LAB.git
cd BPMN_LAB
```

#### Alternative: Download ZIP
1. Go to https://github.com/MinhTri267059/BPMN_LAB
2. Click "Code" → "Download ZIP"
3. Extract to desired location

### Step 4: Setup Python Environment

#### Windows (Command Prompt)
```bash
cd BPMN_LAB
python -m venv .venv
.venv\Scripts\activate
```

#### macOS/Linux (Terminal)
```bash
cd BPMN_LAB
python3.11 -m venv .venv
source .venv/bin/activate
```

**Verify activation**: You should see `(.venv)` prefix in terminal.

### Step 5: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Verify installation**:
```bash
python -c "import neo4j; print(f'Neo4j Driver: {neo4j.__version__}')"
# Should print: Neo4j Driver: 6.1.0
```

### Step 6: Configure Neo4j Connection

Edit `neo4j_loader.py` line 12-14 with your Neo4j credentials:

```python
class Neo4jLoader:
    def __init__(self, uri: str = "bolt://localhost:7687",    # ← Neo4j URI
                 username: str = "neo4j",                        # ← Username
                 password: str = "password"):                    # ← Password
```

| Setting | Default | Change If |
|---|---|---|
| URI | `bolt://localhost:7687` | Neo4j on different port/server |
| Username | `neo4j` | Changed in Neo4j settings |
| Password | `password` | Set custom password |

### Step 7: Load Sample Data (Optional)

```bash
python launcher.py
```

This loads 5 sample Vietnamese BPMN workflows into Neo4j:
- Account Management
- Content Creation
- Media Production
- Advertisement Campaign
- Team Marketing

**Check data loaded**:
```bash
python -c "
from neo4j_loader import Neo4jLoader
loader = Neo4jLoader()
loader.connect()
# If no errors, data loaded successfully!
"
```

---

## 🚀 Running the Dashboard

### Start the Application

#### Windows
```bash
.venv\Scripts\python dashboard.py
```

#### macOS/Linux
```bash
source .venv/bin/activate
python dashboard.py
```

**Expected output**:
```
INFO:neo4j_loader:✅ Connected to Neo4j: bolt://localhost:7687
INFO:neo4j_loader:✅ Retrieved graph data for process 'Account': 13 nodes, 13 edges
```

Dashboard window should open automatically. ✅

### Stopping the Application
- Click "X" to close Tkinter window, or
- Press `Ctrl+C` in terminal

---

## 📖 User Guide

### Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│ Process Control Panel                               │
│  [Dropdown] [Refresh] [Load Data] [Export]          │
└─────────────────────────────────────────────────────┘
│ [Visualization] [Analytics]                         │
├──────────────────┬──────────────────────────────────┤
│  Statistics      │  Interactive Graph Canvas        │
│  - Node Counts   │  (Scroll: Zoom, Drag: Pan)       │
│  - Paths         │                                  │
├──────────────────┤                                  │
│  Query Results   │                                  │
│  - Paths         │                                  │
│  - Bottlenecks   │                                  │
│  - Simulation    │                                  │
└──────────────────┴──────────────────────────────────┘
```

### Visualization Tab

#### 1. Select Process
- Click dropdown: "Select Process"
- Choose from list: BP1, BP2, BP3, BP4, BP5
- Graph renders automatically

#### 2. Interact with Graph
- **Zoom**: Scroll mouse wheel (up=zoom in, down=zoom out)
- **Pan**: Click and drag on canvas
- **Node Details**: Click on any node → See properties in "Query Results" panel

#### 3. Run Queries
- **Find Paths (Start→End)**: Lists all execution paths in process
- **Find Bottlenecks**: Identifies nodes with high convergence
- **Simulate Flow**: Step-by-step execution with conditions

### Analytics Tab

#### Report 1: Task Search
**Purpose**: Find tasks by name across all processes

**How to use**:
1. Enter task name in search box
2. Click "Search" button
3. View results in table

**Example**: Search "Review" → Shows all review tasks in any process

**Case-insensitive**: "review", "REVIEW", "Review" all work

#### Report 2: Gateway Management
**Purpose**: Analyze branching points and decision gates

**How to use**:
1. Click "Gateway Management" button
2. View table with gateways

**Columns**:
- process_id: Which process
- gateway_name: Gateway/decision point name
- branch_count: Number of branches from this gateway

**Use case**: Map decision logic, identify parallel branches

#### Report 3: Time KPI
**Purpose**: Calculate execution time for each process

**How to use**:
1. Click "Time KPI" button
2. View process duration breakdown

**Columns**:
- process_id: Process identifier
- process_name: Human-readable name
- total_minutes: Sum of all task times
- total_hours: Converted to hours

**Use case**: Identify slow processes, estimate timelines

#### Report 4: Cost KPI
**Purpose**: Aggregate personnel costs per process

**How to use**:
1. Click "Cost KPI" button
2. View cost breakdown

**Columns**:
- process_id: Process identifier
- process_name: Human-readable name
- total_cost: Sum of all personnel costs

**Use case**: Budget planning, cost allocation

#### Report 5: Resources
**Purpose**: Identify required roles/departments per process

**How to use**:
1. Click "Resources" button
2. View role requirements

**Columns**:
- process_id: Process identifier
- process_name: Human-readable name
- role_count: Number of unique roles
- roles: Comma-separated role list

**Use case**: Staffing requirements, team planning

---

## 🔌 Advanced Features

### Data Reload Without Restart
1. Click "Load Data from Neo4j" button
2. Dashboard re-fetches all data from database
3. Useful after importing new workflows

### Export Process Data
1. Select process from dropdown
2. Click "Export" button
3. Save as JSON file
4. Can be used for reporting or backup

### Workflow Simulation
1. Select process
2. Click "Simulate Flow" button
3. View step-by-step execution
4. See all possible paths with conditions

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to Neo4j"
```
Error: Could not connect to Neo4j database
```

**Solutions**:
1. **Check Neo4j is running**:
   ```bash
   # Windows
   netstat -ano | findstr :7687
   
   # macOS/Linux
   lsof -i :7687
   ```

2. **Verify credentials** in `neo4j_loader.py`

3. **Check firewall**: Allow localhost:7687

4. **Restart Neo4j**:
   ```bash
   # Docker
   docker restart neo4j
   
   # Neo4j Desktop: Stop and Start in UI
   ```

### Issue: "No data displayed"
```
Error: No statistics available
```

**Solutions**:
1. **Load sample data**:
   ```bash
   python launcher.py
   ```

2. **Check data in Neo4j**:
   ```bash
   # In Neo4j Browser (http://localhost:7474)
   MATCH (n) RETURN count(n)
   # Should show >0 nodes
   ```

3. **Reload data**:
   - Click "Load Data from Neo4j" button

### Issue: "Tkinter module not found"
```
ModuleNotFoundError: No module named 'tkinter'
```

**Solutions**:

**Windows**: Tkinter is included, reinstall Python with "tcl/tk"

**macOS**:
```bash
brew install python-tk@3.11
```

**Linux**:
```bash
sudo apt install python3.11-tk
```

### Issue: "Dependencies not found"
```
ModuleNotFoundError: No module named 'neo4j'
```

**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall --no-cache-dir
```

---

## 📊 Sample Data Description

### 5 Vietnamese Marketing Workflows

#### BP1: Account Management (Quản Lý Tài Khoản)
- **Duration**: 3.25 hours
- **Cost**: $150
- **Nodes**: 7 (Tasks, Gateways, Events)
- **Decision Point**: Customer approval check

#### BP2: Content Creation (Tạo Nội Dung)
- **Duration**: 7 hours
- **Cost**: $180
- **Nodes**: 7
- **Decision Point**: Leader approval

#### BP3: Media Production (Sản Xuất Media)
- **Duration**: 9 hours
- **Cost**: $240
- **Nodes**: 9
- **Decision Point**: Quality feedback loop

#### BP4: Advertisement Campaign (Quản Lý Quảng Cáo)
- **Duration**: 1.5 hours
- **Cost**: $80
- **Nodes**: 5
- **Single Path**: No branching

#### BP5: Team Marketing (Điều Phối Marketing)
- **Duration**: 19 hours
- **Cost**: $1000
- **Nodes**: 14 (Most complex)
- **Multiple Paths**: Parallel coordination

---

## 🔐 Security Notes

⚠️ **Development Use Only**: This setup is for development/testing.

For production:
1. **Change Neo4j password** in settings
2. **Enable Neo4j authentication**
3. **Use encryption** (bolt+s:// instead of bolt://)
4. **Firewall**: Don't expose port 7687 to internet
5. **Database Backup**: Regular backups of Neo4j data

---

## 📚 Learning Resources

### BPMN
- https://www.omg.org/bpmn/ - Official standard
- https://camunda.com/bpmn/ - Visual guide

### Neo4j
- https://neo4j.com/docs/ - Official documentation
- https://neo4j.com/developer/cypher/ - Query language

### Python
- https://docs.python.org/3/ - Official docs
- https://docs.python.org/3/library/tkinter.html - Tkinter tutorial

### Project Code
- `neo4j_loader.py`: Database operations (614 lines)
- `neo4j_visualizer.py`: Graph visualization (354 lines)
- `dashboard.py`: User interface (845 lines)

---

## 🤝 Getting Help

### Troubleshooting Checklist
- [ ] Python 3.11+ installed (`python --version`)
- [ ] Neo4j 6.1+ running (`lsof -i :7687` on Mac/Linux)
- [ ] Dependencies installed (`pip list | grep neo4j`)
- [ ] Neo4j credentials correct in code
- [ ] Sample data loaded (`python launcher.py`)

### Common Commands

```bash
# Activate environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install/update packages
pip install -r requirements.txt

# Run application
python dashboard.py

# Load sample data
python launcher.py

# Check Neo4j connection
python -c "from neo4j_loader import Neo4jLoader; l = Neo4jLoader(); print(l.connect())"

# Deactivate environment
deactivate
```

---

## 📝 Project Structure

```
BPMN_LAB/
├── dashboard.py              # Main GUI application (845 lines)
├── neo4j_loader.py          # Database layer (614 lines)
├── neo4j_visualizer.py      # Visualization engine (354 lines)
├── launcher.py              # Data loading utility
├── requirements.txt         # Python dependencies
├── .gitignore              # Git configuration
├── README_GITHUB.md        # GitHub README (this file)
│
├── Sample Workflows (XML):
├── Account.xml
├── Content.xml
├── Media.xml
├── Ads.xml
└── Team Marketing.xml
```

---

## ✅ Verification Checklist

After installation, verify everything works:

```bash
# 1. Python version
python --version
# ✓ Should be 3.11+

# 2. Neo4j connection
python -c "from neo4j_loader import Neo4jLoader; print('✓ Neo4j OK' if Neo4jLoader().connect() else '✗ Neo4j Failed')"

# 3. Load sample data
python launcher.py
# ✓ Should load 5 workflows

# 4. Run dashboard
python dashboard.py
# ✓ Window should open without errors
```

---

## 🎓 Next Steps

1. **Explore Sample Data**: Load workflows, check each tab
2. **Run Analytics Queries**: Try all 5 report types
3. **Load Custom Data**: Import your own BPMN workflows
4. **Customize**: Modify dashboard colors, layout
5. **Extend**: Add your own analytics queries

---

## 📞 Support

**Issues?**
1. Check this guide's Troubleshooting section
2. Review GitHub Issues: https://github.com/MinhTri267059/BPMN_LAB/issues
3. Create new issue with error details

**Want to contribute?**
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push and create Pull Request

---

**Last Updated**: January 29, 2026  
**Version**: 1.0.0  
**Status**: ✅ Ready for Use
