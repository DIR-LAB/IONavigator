import os
import json
import uuid
import pandas as pd
from ion.Utils import get_config, setup_logger

tree_logger = setup_logger('tree')
class DiagnosisTable:
    def __init__(self):
        self.nodesTable = pd.DataFrame(columns=['id', 'name', 'content', 'child', 'step', 'module', 'object'])
        self.nodes = {}

    def add_node(self, node):
        new_entry = pd.DataFrame({
            'id': [node.id],
            'name': [node.name],
            'content': [node.content],
            'child': [node.child.id if node.child else None],
            'step': [node.step],
            'module': [node.module]
        })
        self.nodesTable = pd.concat([self.nodesTable, new_entry], ignore_index=True)
        self.nodes[node.id] = node

    def update_node_child(self, node_id, child_id):
        self.nodesTable.loc[self.nodesTable['id'] == node_id, 'child'] = child_id
    
    def to_tree_json(self):
        def build_tree(node_id):
            node = self.nodes[node_id]
            tree_node = {
                'id': node.id,
                'name': node.name,
                'content': node.content,
                'step': node.step,
                'module': node.module,
                'parents': []
            }
            parent_nodes = self.nodesTable[self.nodesTable['child'] == node_id]
            for _, parent in parent_nodes.iterrows():
                tree_node['parents'].append(build_tree(parent['id']))
            return tree_node

        final_diagnosis_node = self.nodesTable[self.nodesTable['step'] == 'final_diagnosis']
        if not final_diagnosis_node.empty:
            root_node_id = final_diagnosis_node.iloc[0]['id']
            tree = build_tree(root_node_id)
            return [tree]
        else:
            return []



class DiagnosisTreeNode:
    def __init__(self, name, content, step, module, diagnosis_table):
        self.id = str(uuid.uuid4())
        self.name = name
        self.content = content
        self.step = step
        self.module = module
        self.child = None
        diagnosis_table.add_node(self)


    def add_child(self, child, diagnosis_table):
        self.child = child
        diagnosis_table.update_node_child(self.id, child.id)


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'child': self.child.to_dict(),
            'step': self.step,
            'module': self.module
        }



def parse_dir_tree(directory_path):
    print(f"Parsing directory tree: {directory_path}")
    # parse dir tree 
    diagnosis_table = DiagnosisTable()

    step_order = ['summary_fragments', 'rag_diagnoses', 'intra_module_merges', 'inter_module_merges', 'final_diagnosis']
    for step in step_order:
        print(f"Parsing step: {step}")
        if os.path.exists(os.path.join(directory_path, step)):
            print(f"Step exists: {step}")
            if step == 'summary_fragments':
                parse_summary_fragments(directory_path, diagnosis_table)
            elif step == 'rag_diagnoses':
                parse_rag_diagnoses(directory_path, diagnosis_table)
            elif step == 'intra_module_merges':
                parse_intra_module_merge(directory_path, diagnosis_table)
            elif step == 'inter_module_merges':
                parse_inter_module_merge(directory_path, diagnosis_table)
            elif step == 'final_diagnosis':
                parse_final_diagnosis(directory_path, diagnosis_table)
            else:
                print(f"Step does not exist: {step}")
    table_json = diagnosis_table.to_tree_json()
    print(f"Table JSON: {table_json}")
    #save the table_json to a file
    if table_json == []:
        raise Exception("No tree found")
    return table_json


def parse_summary_fragments(directory_path, diagnosis_table):
    # parse summary fragments
    summary_fragments_path = os.path.join(directory_path, "summary_fragments")
    for summary_fragment in os.listdir(summary_fragments_path):
        with open(os.path.join(summary_fragments_path, summary_fragment), 'r') as f:
            summary_fragment_content = f.read()
            module_name = summary_fragment.split('_')[0]
            DiagnosisTreeNode(summary_fragment, summary_fragment_content, 'summary_fragments', module_name, diagnosis_table)
        

def parse_rag_diagnoses(directory_path, diagnosis_table):
    # parse rag diagnoses
    rag_diagnoses_path = os.path.join(directory_path, "rag_diagnoses")
    for rag_diagnosis in os.listdir(rag_diagnoses_path):
        if rag_diagnosis.endswith('.json'):
            with open(os.path.join(rag_diagnoses_path, rag_diagnosis), 'r') as f:
                rag_diagnosis_content = json.load(f)
                corresponding_summary = rag_diagnosis.replace('.json', '.txt')
                # find the node with the corresponding summary
                summary_node = diagnosis_table.nodesTable[diagnosis_table.nodesTable['name'] == corresponding_summary]
                summary_node = summary_node[summary_node['step'] == 'summary_fragments'].iloc[0]
                rag_diagnosis_node = DiagnosisTreeNode(rag_diagnosis, rag_diagnosis_content, 'rag_diagnoses', summary_node['module'], diagnosis_table)
                summary_node_obj = diagnosis_table.nodes[summary_node['id']]
                summary_node_obj.add_child(rag_diagnosis_node, diagnosis_table)

def parse_intra_module_merge(directory_path, diagnosis_table):
    tree_logger.info("Parsing new intra module merge")
    # parse intra module merge
    intra_module_merge_path = os.path.join(directory_path, "intra_module_merges")
    for dir_name in os.listdir(intra_module_merge_path):
        if not "final" in dir_name:
            module_name = dir_name
            # convert subdir to int and sort
            subdirs = [int(subdir) for subdir in os.listdir(os.path.join(intra_module_merge_path, dir_name))]
            subdirs.sort()
            #  find the nodes with the same module name and step 'rag_diagnoses' from diagnosis_table
            module_nodes = diagnosis_table.nodesTable[diagnosis_table.nodesTable['module'] == module_name]
            module_nodes = module_nodes[module_nodes['step'] == 'rag_diagnoses']
            # each one of the module_node should be named as module_<idx>.json. extract idx from the name
            module_nodes['idx'] = module_nodes['name'].apply(lambda x: int(x.split('_')[1].split('.')[0]))
            max_idx = max(module_nodes['idx'])
            for file in os.listdir(os.path.join(intra_module_merge_path, dir_name, str(subdirs[0]))):
                if file.endswith('.json'):
                    idx = int(file.split('.')[0])
                    with open(os.path.join(intra_module_merge_path, dir_name, str(subdirs[0]), file), 'r') as f:
                        intra_module_merge_content = json.load(f)
                    if idx != max_idx:
                        # find the node with the same id
                        rag_diagnosis1 = module_nodes.loc[module_nodes['idx'] == idx, 'id'].iloc[0]
                        rag_diagnosis1_node = diagnosis_table.nodes[rag_diagnosis1]
                        rag_diagnosis2 = module_nodes.loc[module_nodes['idx'] == idx + 1, 'id'].iloc[0]
                        rag_diagnosis2_node = diagnosis_table.nodes[rag_diagnosis2]
                        intra_module_merge_node = DiagnosisTreeNode(file, intra_module_merge_content, 'intra_module_merges', module_name, diagnosis_table)
                        rag_diagnosis1_node.add_child(intra_module_merge_node, diagnosis_table)
                        rag_diagnosis2_node.add_child(intra_module_merge_node, diagnosis_table)
                        if module_name == "POSIX":
                            tree_logger.info(f"adding {intra_module_merge_node.name} as child to {rag_diagnosis1_node.name}")
                            tree_logger.info(f"adding {intra_module_merge_node.name} as child to {rag_diagnosis2_node.name}")
                    else:
                        rag_diagnosis1 = module_nodes.loc[module_nodes['idx'] == idx, 'id'].iloc[0]
                        rag_diagnosis1_node = diagnosis_table.nodes[rag_diagnosis1]
                        intra_module_merge_node = DiagnosisTreeNode(file, intra_module_merge_content, 'intra_module_merges', module_name, diagnosis_table)
                        rag_diagnosis1_node.add_child(intra_module_merge_node, diagnosis_table)
                        if module_name == "POSIX":
                            tree_logger.info(f"adding {intra_module_merge_node.name} as child to {rag_diagnosis1_node.name}")
            for subdir in subdirs[1:]:
                if dir_name == "POSIX":
                    tree_logger.info(f"subdir: {subdir} of {subdirs[1:]}")
                previous_merge_nodes = diagnosis_table.nodesTable[diagnosis_table.nodesTable['module'] == module_name]
                previous_merge_nodes = previous_merge_nodes[previous_merge_nodes['step'] == 'intra_module_merges']
                # find where child is None
                previous_merge_nodes = previous_merge_nodes[previous_merge_nodes['child'].isna()]
                previous_merge_nodes['idx'] = previous_merge_nodes['name'].apply(lambda x: int(x.split('.')[0]))
                # sort by idx
                previous_merge_nodes = previous_merge_nodes.sort_values(by='idx')
                for file in os.listdir(os.path.join(intra_module_merge_path, dir_name, str(subdir))):
                    if file.endswith('.json'):
                        tree_logger.info(f"file: {file}")
                        idx = int(file.split('.')[0])
                        with open(os.path.join(intra_module_merge_path, dir_name, str(subdir), file), 'r') as f:
                            intra_module_merge_content = json.load(f)
                        if len(previous_merge_nodes) > 1:
                            previous_merge_node1_id = previous_merge_nodes['id'].iloc[0]
                            # remove the first element from previous_merge_nodes
                            previous_merge_nodes = previous_merge_nodes.iloc[1:]
                            previous_merge_node1_obj = diagnosis_table.nodes[previous_merge_node1_id]
                            previous_merge_node2_id = previous_merge_nodes['id'].iloc[0]
                            # remove the first element from previous_merge_nodes
                            previous_merge_nodes = previous_merge_nodes.iloc[1:]
                            previous_merge_node2_obj = diagnosis_table.nodes[previous_merge_node2_id]
                            intra_module_merge_node = DiagnosisTreeNode(file, intra_module_merge_content, 'intra_module_merges', module_name, diagnosis_table)
                            previous_merge_node1_obj.add_child(intra_module_merge_node, diagnosis_table)
                            previous_merge_node2_obj.add_child(intra_module_merge_node, diagnosis_table)
                            if module_name == "POSIX":
                                tree_logger.info(f"adding {intra_module_merge_node.name} as child to {previous_merge_node1_obj.name}")
                                tree_logger.info(f"adding {intra_module_merge_node.name} as child to {previous_merge_node2_obj.name}")
                        else:
                            previous_merge_node_id = previous_merge_nodes['id'].iloc[0]
                            # remove the first element from previous_merge_nodes
                            previous_merge_nodes = None
                            previous_merge_node_obj = diagnosis_table.nodes[previous_merge_node_id]
                            intra_module_merge_node = DiagnosisTreeNode(file, intra_module_merge_content, 'intra_module_merges', module_name, diagnosis_table)
                            previous_merge_node_obj.add_child(intra_module_merge_node, diagnosis_table)
                            if module_name == "POSIX":
                                tree_logger.info(f"adding {intra_module_merge_node.name} as child to {previous_merge_node_obj.name}")
                        tree_logger.info(f"previous_merge_nodes: {previous_merge_nodes}")
    # now find the dir with "final" in its name
    for dir_name in os.listdir(intra_module_merge_path):
        if "final" in dir_name:
            final_dir = os.path.join(intra_module_merge_path, dir_name)
            tree_logger.info(f"final_dir: {final_dir}")
            for file in os.listdir(final_dir):
                module_name = file.split('.')[0]
                with open(os.path.join(final_dir, file), 'r') as f:
                    intra_module_merge_content = json.load(f)
                print("module_name", module_name)
                # find all nodes with the same module name and step 'intra_module_merge' that have no child
                intra_module_merge_nodes = diagnosis_table.nodesTable[diagnosis_table.nodesTable['module'] == module_name]
                print("intra_module_merge_nodes", intra_module_merge_nodes)
                intra_module_merge_nodes = intra_module_merge_nodes[intra_module_merge_nodes['step'] == 'intra_module_merges']
                print("intra_module_merge_nodes", intra_module_merge_nodes)
                intra_module_merge_nodes = intra_module_merge_nodes[intra_module_merge_nodes['child'].isna()]
                print("intra_module_merge_nodes", intra_module_merge_nodes)
                final_intra_module_merge_node = DiagnosisTreeNode(file, intra_module_merge_content, 'intra_module_merges', module_name, diagnosis_table)
                print("intra_module_merge_nodes", intra_module_merge_nodes)
                print(type(intra_module_merge_nodes))
                for _, node in intra_module_merge_nodes.iterrows():
                    print("node: ", node)
                    node_obj = diagnosis_table.nodes[node['id']]
                    node_obj.add_child(final_intra_module_merge_node, diagnosis_table)
                    if module_name == "POSIX":
                        tree_logger.info(f"adding {final_intra_module_merge_node.name} as child to {node_obj.name}")

def parse_inter_module_merge(directory_path, diagnosis_table):
    inter_module_merge_path = os.path.join(directory_path, "inter_module_merges")
    subdirs = [int(subdir) for subdir in os.listdir(inter_module_merge_path)]
    subdirs.sort()
    module_diagnoses = diagnosis_table.nodesTable[diagnosis_table.nodesTable['step'] == 'intra_module_merges']
    module_diagnoses = module_diagnoses[module_diagnoses['child'].isna()]
    for file in os.listdir(os.path.join(inter_module_merge_path, str(subdirs[0]))):
        if file.endswith('.json'):
            with open(os.path.join(inter_module_merge_path, str(subdirs[0]), file), 'r') as f:
                inter_module_merge_content = json.load(f)
            modules_merged = file.split('.')[0].split('_')
            module_name = file.split('.')[0]
            inter_module_merge_node = DiagnosisTreeNode(file, inter_module_merge_content, 'inter_module_merges', module_name, diagnosis_table)
            for module in modules_merged:
                module_node = module_diagnoses[module_diagnoses['name'] == module+".json"]
                module_node_obj = diagnosis_table.nodes[module_node['id'].iloc[0]]
                module_node_obj.add_child(inter_module_merge_node, diagnosis_table)
    # for now there is only one subdir so no need for a for further loop

def parse_final_diagnosis(directory_path, diagnosis_table):
    final_diagnosis_path = os.path.join(directory_path, "final_diagnosis")
    file_name = "final_diagnosis.json"
    with open(os.path.join(final_diagnosis_path, file_name), 'r') as f:
        final_diagnosis_content = json.load(f)
    final_diagnosis_node = DiagnosisTreeNode(file_name, final_diagnosis_content, 'final_diagnosis', 'final_diagnosis', diagnosis_table)
    # get all nodes with step 'inter_module_merge' that have no child
    inter_module_merge_nodes = diagnosis_table.nodesTable[diagnosis_table.nodesTable['step'].isin(['inter_module_merges', 'intra_module_merges'])]
    inter_module_merge_nodes = inter_module_merge_nodes[inter_module_merge_nodes['child'].isna()]
    print("inter_module_merge_nodes", inter_module_merge_nodes)
    for _, node in inter_module_merge_nodes.iterrows():
        node_obj = diagnosis_table.nodes[node['id']]
        node_obj.add_child(final_diagnosis_node, diagnosis_table)