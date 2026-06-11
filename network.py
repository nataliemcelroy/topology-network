import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

# ── Data Loading ───────────────────────────────────────────────────────────────
data_path = '/Users/natalie/Documents/Personal/Computing Courses/Computational Topology - CS 6170/Final Project/ResearchDevelopment_Network/Data Sources.xlsx'
df = pd.read_excel(data_path, sheet_name='NIH Active Projects')

df['Contact PI / Project Leader'] = df['Contact PI / Project Leader'].astype(str).str.strip()
df['Department'] = df['Department'].astype(str).str.strip()

df = df[~df['Department'].isin(['Unavailable', 'NONE', 'MISCELLANEOUS', 'nan'])]
df = df[df['Contact PI / Project Leader'].notna()]
df = df[df['Contact PI / Project Leader'] != '']

# ── Filter ─────────────────────────────────────────────────────────────────────
top10_depts = df['Department'].value_counts().head(10).index.tolist()
df = df[df['Department'].isin(top10_depts)]

top20_pis = df['Contact PI / Project Leader'].value_counts().head(20).index.tolist()
df = df[df['Contact PI / Project Leader'].isin(top20_pis)]

print(f"Unique PIs: {df['Contact PI / Project Leader'].nunique()}")
print(f"Unique Departments: {df['Department'].nunique()}")

# ── Build Graph ────────────────────────────────────────────────────────────────
G = nx.Graph()

for _, row in df.iterrows():
    pi   = row['Contact PI / Project Leader']
    dept = row['Department']
    G.add_node(pi,   type='PI')
    G.add_node(dept, type='Department')
    if G.has_edge(pi, dept):
        G[pi][dept]['weight'] += 1
    else:
        G.add_edge(pi, dept, weight=1)

print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# ── Layout ─────────────────────────────────────────────────────────────────────
dept_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'Department']
pi_nodes   = [n for n, d in G.nodes(data=True) if d['type'] == 'PI']

dept_nodes_sorted = sorted(dept_nodes)
pi_nodes_sorted   = sorted(pi_nodes)

pos = {}
for i, node in enumerate(dept_nodes_sorted):
    pos[node] = (4, (i - len(dept_nodes_sorted) / 2) * 4.5)
for i, node in enumerate(pi_nodes_sorted):
    pos[node] = (9, (i - len(pi_nodes_sorted) / 2) * 2.5)

dept_label_pos = {n: (pos[n][0] - 0.8, pos[n][1]) for n in dept_nodes}
pi_label_pos   = {n: (pos[n][0] + 0.8, pos[n][1]) for n in pi_nodes}

dept_abbreviations = {
    'PUBLIC HEALTH & PREV MEDICINE':  'PUBLIC HEALTH & PREV MED',
    'INTERNAL MEDICINE/MEDICINE':     'INTERNAL MEDICINE',
    ' INTERNAL MEDICINE/MEDICINE':    'INTERNAL MEDICINE',  # with leading space
}

# ── Visualization ──────────────────────────────────────────────────────────────
color_map = {'PI': '#4A90D9', 'Department': '#5BAD6F'}
node_colors = [color_map[G.nodes[n]['type']] for n in G.nodes()]

# Count projects per PI
pi_project_counts = df['Contact PI / Project Leader'].value_counts().to_dict()

node_sizes = []
for n in G.nodes():
    if G.nodes[n]['type'] == 'Department':
        node_sizes.append(800)
    else:
        # Scale PI node size by project count (min 200, max 1000)
        count = pi_project_counts.get(n, 1)
        node_sizes.append(200 + count * 150)

edge_weights = [G[u][v]['weight'] * 0.5 for u, v in G.edges()]

fig, ax = plt.subplots(figsize=(55, 24))  # ax exists from here down

nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                       node_size=node_sizes, alpha=0.9)
nx.draw_networkx_edges(G, pos, ax=ax, width=edge_weights,
                       edge_color='gray', alpha=0.3)

# Department labels with abbreviations
for node in dept_nodes:
    x, y = dept_label_pos[node]
    label = dept_abbreviations.get(node, node)
    ax.text(x, y, label, fontsize=13, fontweight='bold',
            ha='right', va='center', transform=ax.transData)

for node in pi_nodes:
    x, y = pi_label_pos[node]
    ax.text(x, y, node, fontsize=11,
            ha='left', va='center', transform=ax.transData)
    
legend_handles = [
    mpatches.Patch(color='#4A90D9', label='Principal Investigator (size = # projects)'),
    mpatches.Patch(color='#5BAD6F', label='Department'),
]

# Add this before plt.axis('off'):
all_x = [pos[n][0] for n in G.nodes()]
all_y = [pos[n][1] for n in G.nodes()]
ax.set_xlim(min(all_x) - 5, max(all_x) + 5)
ax.set_ylim(min(all_y) - 2, max(all_y) + 2)

ax.legend(handles=legend_handles, loc='upper center', fontsize=11,
          framealpha=0.9, ncol=2)

ax.set_title("University of Utah NIH Active Projects\nPI ↔ Department Network",
             fontsize=16, pad=20)
plt.axis('off')
plt.savefig(
    "/Users/natalie/Documents/Personal/Computing Courses/Computational Topology - CS 6170/Final Project/ResearchDevelopment_Network/research_network.png",
    bbox_inches='tight', dpi=150
)
plt.close(fig)
print("Saved research_network.png")