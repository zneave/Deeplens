import os
from graphviz import Digraph

def generate_project_diagram(project_root, output_filename="docs/images/project_structure"):
    if '.' in output_filename:
        base_filename, output_format = output_filename.rsplit('.', 1)
    else:
        base_filename = output_filename
        output_format = "png"

    dot = Digraph(comment="DeepLens Project Structure", format=output_format)

    dot.attr(rankdir="TB")
    dot.attr(bgcolor="black")
    dot.attr(splines="polyline", nodesep="0.6", ranksep="0.8")
    dot.attr("node", style="filled", fontname="Helvetica", fontsize="10",
             fillcolor="gray20", fontcolor="white", color="white")

    def folder_contains_relevant_files(folder_path):
        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '.git']
            if any(f.endswith(('.py', '.yaml', '.yml')) for f in files):
                return True
        return False

    def add_nodes(current_path, parent_id):
        try:
            items = sorted(os.listdir(current_path))
        except Exception as e:
            print(f"Error reading {current_path}: {e}")
            return

        for item in items:
            if item.startswith('.') or item == '.git':
                continue

            full_path = os.path.join(current_path, item)
            item_id = os.path.relpath(full_path, project_root).replace(os.sep, "_")

            if os.path.isdir(full_path):
                if not folder_contains_relevant_files(full_path):
                    continue
                dot.node(item_id, f"📂 {item}", shape="folder", fillcolor="gray30")
                dot.edge(parent_id, item_id, color="white")
                add_nodes(full_path, item_id)
            else:
                if item.endswith(('.py', '.yaml', '.yml')):
                    dot.node(item_id, f"📄 {item}", shape="note", fillcolor="gray10")
                    dot.edge(parent_id, item_id, color="lightgray")

    root_name = os.path.basename(os.path.abspath(project_root))
    root_id = root_name.replace(os.sep, "_")
    dot.node(root_id, f"📦 {root_name}", shape="folder", fillcolor="gray40")
    add_nodes(project_root, root_id)

    dot.render(filename=base_filename, cleanup=True)
    print(f"[📁 FLOWCHART] Diagram saved as: {base_filename}.{output_format}")

if __name__ == "__main__":
    current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    generate_project_diagram(current_dir)
