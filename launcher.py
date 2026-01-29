"""
Launcher script for Neo4j Workflow Visualization System
Provides menu to choose between Dashboard, Visualizer, and Tests
"""

import sys
import subprocess
import platform


def show_menu():
    """Display main menu"""
    print("\n" + "=" * 60)
    print("Neo4j Workflow Visualization System")
    print("=" * 60)
    print("\nChoose an option:")
    print("1. Launch Dashboard GUI (interactive)")
    print("2. Run Visualizer Tests")
    print("3. View All Processes in Database")
    print("4. Export Process Data")
    print("5. Exit")
    print("-" * 60)
    choice = input("Enter your choice (1-5): ").strip()
    return choice


def launch_dashboard():
    """Launch the dashboard GUI"""
    print("\nLaunching Dashboard...")
    print("The dashboard window should open shortly...")
    print("\nFeatures:")
    print("  - Select and load processes from Neo4j")
    print("  - View process statistics and metrics")
    print("  - Visualize workflow as interactive graph")
    print("  - Find paths from Start to End")
    print("  - Identify bottlenecks and parallel paths")
    print("  - Export process data to JSON")
    
    try:
        if platform.system() == "Windows":
            subprocess.Popen([sys.executable, "dashboard.py"])
        else:
            subprocess.Popen([sys.executable, "dashboard.py"])
        print("\n✅ Dashboard launched!")
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")


def run_tests():
    """Run visualizer tests"""
    print("\nRunning tests...")
    try:
        subprocess.run([sys.executable, "test_dashboard.py"], check=True)
        print("\n✅ Tests completed!")
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")


def view_processes():
    """View all processes in database"""
    try:
        from neo4j_visualizer import Neo4jVisualizer
        
        visualizer = Neo4jVisualizer()
        if visualizer.connect():
            processes = visualizer.get_all_processes()
            
            print("\n" + "=" * 60)
            print("Processes in Database")
            print("=" * 60)
            
            if processes:
                for p in processes:
                    print(f"\nProcess ID: {p['id']}")
                    print(f"  Name: {p['name']}")
                    print(f"  Nodes: {p['node_count']}")
                    
                    # Get stats
                    stats = visualizer.get_process_statistics(p['id'])
                    if stats:
                        print(f"  Edges: {stats['total_edges']}")
                        print(f"  Types: Start({stats['start_count']}), End({stats['end_count']}), " 
                              f"Task({stats['task_count']}), Gateway({stats['gateway_count']})")
            else:
                print("\nNo processes found in database")
            
            visualizer.disconnect()
        else:
            print("\n❌ Could not connect to Neo4j")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def export_data():
    """Export process data"""
    try:
        from neo4j_visualizer import Neo4jVisualizer
        import json
        
        visualizer = Neo4jVisualizer()
        if visualizer.connect():
            processes = visualizer.get_all_processes()
            
            if not processes:
                print("\nNo processes found")
                visualizer.disconnect()
                return
            
            print("\nSelect a process to export:")
            for i, p in enumerate(processes, 1):
                print(f"{i}. {p['id']} - {p['name']}")
            
            choice = input("Enter process number: ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(processes):
                    process_id = processes[idx]['id']
                    visualizer.load_process(process_id)
                    
                    export_json = visualizer.export_process_data(process_id, format='json')
                    if export_json:
                        filename = f"export_{process_id}.json"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(export_json)
                        
                        # Show summary
                        data = json.loads(export_json)
                        print(f"\n✅ Exported {len(data['nodes'])} nodes and {len(data['edges'])} edges")
                        print(f"   Saved to: {filename}")
                    else:
                        print("\n❌ Export failed")
                else:
                    print("\n❌ Invalid selection")
            except ValueError:
                print("\n❌ Invalid input")
            
            visualizer.disconnect()
        else:
            print("\n❌ Could not connect to Neo4j")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main menu loop"""
    while True:
        choice = show_menu()
        
        if choice == "1":
            launch_dashboard()
        elif choice == "2":
            run_tests()
        elif choice == "3":
            view_processes()
        elif choice == "4":
            export_data()
        elif choice == "5":
            print("\nGoodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
