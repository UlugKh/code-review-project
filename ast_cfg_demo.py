import ast
import networkx as nx
import matplotlib.pyplot as plt
import random

# Sample code snippets from your dataset
code_snippets = [
    """
def add(a, b):
    return a + b
""",
    """
def sum_numbers(x, y):
    result = x + y
    return result
""",
    """
def multiply(arr):
    total = 1
    for num in arr:
        total *= num
    return total
"""
]

def visualize_ast(code, filename):
    """Generate AST visualization"""
    try:
        tree = ast.parse(code)
        fig, ax = plt.subplots(figsize=(12, 8))
        
        def add_nodes_edges(node, parent=None, depth=0, pos=None, nodes=None, edges=None):
            if nodes is None:
                nodes = {}
            if edges is None:
                edges = []
            
            node_id = len(nodes)
            node_label = type(node).__name__
            if hasattr(node, 'name'):
                node_label += f"\n{node.name}"
            elif hasattr(node, 'id'):
                node_label += f"\n{node.id}"
            elif hasattr(node, 'value') and isinstance(node.value, str):
                node_label += f"\n{node.value}"
            elif hasattr(node, 's') and isinstance(node.s, str):
                node_label += f"\n{node.s}"
            
            nodes[node_id] = (node_label, depth)
            
            if parent is not None:
                edges.append((parent, node_id))
            
            for child in ast.iter_child_nodes(node):
                add_nodes_edges(child, node_id, depth + 1, pos, nodes, edges)
            
            return nodes, edges
        
        nodes, edges = add_nodes_edges(tree)
        
        # Create networkx graph
        G = nx.DiGraph()
        for node_id, (label, depth) in nodes.items():
            G.add_node(node_id, label=label, depth=depth)
        G.add_edges_from(edges)
        
        # Layout
        pos = nx.spring_layout(G, k=2, seed=42)
        
        # Draw
        nx.draw(G, pos, with_labels=True, 
                labels={n: G.nodes[n]['label'] for n in G.nodes()},
                node_size=2000, node_color='lightblue',
                font_size=8, font_weight='bold',
                arrows=True, arrowsize=20)
        
        plt.title(f"AST for code snippet")
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ AST visualization saved to {filename}")
        return True
    except Exception as e:
        print(f"⚠️ AST generation failed: {e}")
        return False

def visualize_cfg(code, filename):
    """Generate CFG visualization (simplified)"""
    try:
        G = nx.DiGraph()
        
        # Simplified CFG nodes for demonstration
        lines = code.strip().split('\n')
        nodes = []
        
        # Entry node
        G.add_node('entry', label='Entry')
        nodes.append('entry')
        
        # Statement nodes
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                node_id = f'stmt_{i}'
                G.add_node(node_id, label=line.strip()[:30])
                nodes.append(node_id)
        
        # Exit node
        G.add_node('exit', label='Exit')
        nodes.append('exit')
        
        # Connect nodes in sequence
        for i in range(len(nodes) - 1):
            G.add_edge(nodes[i], nodes[i+1])
        
        # Add branching for control flow (if/for/while detection)
        for i, line in enumerate(lines):
            if 'if' in line or 'for' in line or 'while' in line:
                node_id = f'stmt_{i}'
                # Add a branch to exit (simplified)
                if i + 1 < len(nodes) - 1:
                    G.add_edge(node_id, 'exit')
        
        pos = nx.spring_layout(G, k=2, seed=42)
        
        plt.figure(figsize=(10, 8))
        nx.draw(G, pos, with_labels=True,
                labels={n: G.nodes[n]['label'] for n in G.nodes()},
                node_size=3000, node_color='lightgreen',
                font_size=9, font_weight='bold',
                arrows=True, arrowsize=20)
        plt.title(f"CFG for code snippet")
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ CFG visualization saved to {filename}")
        return True
    except Exception as e:
        print(f"⚠️ CFG generation failed: {e}")
        return False

# Generate AST and CFG for each sample
for i, code in enumerate(code_snippets):
    print(f"\n--- Sample {i+1} ---")
    print(code.strip())
    print()
    visualize_ast(code, f'ast_sample_{i+1}.png')
    visualize_cfg(code, f'cfg_sample_{i+1}.png')

print("\n✅ AST/CFG generation complete")
print("Add these images to your report as examples")

