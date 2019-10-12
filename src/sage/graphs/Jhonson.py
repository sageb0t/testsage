class Node(object):
    
    def __init__(self):
        self.index_in_graph = 0
        self.neighbors = {}
        
    def add_neighbors(self, node_idx, cost):
        self.neighbors[node_idx] = cost
        
    def remove_neighbor(self, node_idx):
        self.neighbors.pop(node_idx, None)
        
class Graph(object):
    
    def new_completely_connected_v(self):
        self.add_node(Node())
        idx = self.num_nodes-1
        for old_node in range(idx):
            self.add_edge_from_to(idx_from=idx, idx_to=old_node, cost=0)
            
    def __init__(self):
        self.nodes = []
        self.num_nodes = 0
        
    def add_node(self, node):
        self.nodes.append(node)
        node.index_in_graph = len(self.nodes) - 1
        self.num_nodes += 1
        
    def create_graph_by_num_of_nodes(self, num_of_nodes):
        for i in range(num_of_nodes):
            self.add_node(node=Node())
            
    def add_edge_from_to(self, idx_from, idx_to, cost):
        self.nodes[idx_from].add_neighbors(node_idx=idx_to, cost=cost)
        
    def remove_node(self, node):
        for other_node in self.nodes:
            other_node.remove_neighbor(node_idx=node.index_in_graph)
        self.nodes.remove(node)
        self.num_nodes -= 1
        
        
class Dijkstra(Graph):
    
    def __init__(self, graph):
        self.nodes = graph.nodes
        self.num_nodes = graph.num_nodes
        self.min_costs = None
        self.next_nodes = {}
        self.visited_nodes = []
        
    def add_next_node(self, next_node, current_node):
        if next_node not in self.visited_nodes:
            try:
                self.next_nodes[next_node] = min(self.nodes[current_node].neighbors[next_node] + 
                                            self.min_costs[current_node], self.next_nodes[next_node])
            except:
                self.next_nodes[next_node] = self.nodes[current_node].neighbors[next_node] + \
                                                self.min_costs[current_node]
    
    def remove_next_node(self, remove_idx):
        self.next_nodes.pop(remove_idx)
       
    def visit_node(self, node_idx, cost, step_by_step=False):
        self.min_costs[node_idx] = cost
        if step_by_step:
            print("   Chosen node: ", node_idx, "   |   New lowest paths: ", list(self.min_costs))
            print("-------------------------------------------------------------------------")
        self.visited_nodes.append(node_idx)
        self.remove_next_node(remove_idx=node_idx)
            
    def get_min_in_next_nodes(self, step_by_step=False):
        minimum_value = min(self.next_nodes.values())
        if step_by_step:
            print("Values of the nodes to be inserted: ", self.next_nodes)
            print("-------------------------------------------------------------------------")
            print("Lowest value: ", minimum_value, "<<<")
        for node in self.next_nodes.keys():
            if self.next_nodes[node] == minimum_value:
                if step_by_step:
                    print("Lowest value node: ", node, "<<<")
                    print("-------------------------------------------------------------------------")
                return node
            
    def build_instance(self, node_idx, step_by_step=False, next_nodes=True):
        self.min_costs = np.full(self.num_nodes,float('inf'))
        if step_by_step:
            print("Initial node: ", node_idx)
            print("Initial costs: ", list(self.min_costs))
            print("-------------------------------------------------------------------------")
        if next_nodes:
            self.next_nodes[node_idx] = 0
        else:
            self.min_costs[node_idx] = 0
           
    def run(self, node_idx, step_by_step=False):
        self.build_instance(node_idx, step_by_step=step_by_step)
        while(len(self.next_nodes.keys()) > 0):
            chosen_node_idx = self.get_min_in_next_nodes(step_by_step=step_by_step)
            self.visit_node(node_idx=chosen_node_idx, cost=self.next_nodes[chosen_node_idx], 
                            step_by_step=step_by_step)
            for node in self.nodes[chosen_node_idx].neighbors.keys():
                self.add_next_node(next_node=node, current_node=chosen_node_idx)
                if step_by_step:
                    print("Novos nós a serem inseridos: ", self.next_nodes)
    
    def show_results(self):
        print("\n\n\n\n")
        print("Minimum paths:")
        for idx, cost in enumerate(self.min_costs):
            print("-------------------------------------------------------------------------")
            print("Node index:", idx,"\nCost:", cost)

class BellmanFord(Dijkstra):
    
    def __init__(self, graph):
        self.nodes = graph.nodes
        self.num_nodes = graph.num_nodes
        self.min_costs = None
        self.next_edges = []
    
    def add_edge_to_analyse(self, begin_node, end_node, weight):
        if [begin_node, end_node, weight] in self.next_edges:
            return True
        self.next_edges.append([begin_node, end_node, weight])
        return False
    
    def generate_edges_list(self, initial_node):
        loop = {}
        for node, weight in self.nodes[initial_node].neighbors.items():
            loop[node] = self.add_edge_to_analyse(begin_node=initial_node, end_node=node, weight=weight)
        for node in loop:
            if not loop[node]:
                self.generate_edges_list(node)
    
    def run(self, node_idx, step_by_step=False):
        self.build_instance(node_idx=node_idx, step_by_step=step_by_step ,next_nodes=False)
        self.generate_edges_list(initial_node=node_idx)
        i = 0
        if step_by_step:
            print("Update minimum costs ",self.num_nodes-1, " times.")
        while i < self.num_nodes - 1:
            if step_by_step:
                print("-------------------------------------------------------------------------")
                print("Atualization #", i+1, "- Minimum costs: ", self.min_costs)
                print("For each arc on the graph:")
            for begin_node, end_node, weight in self.next_edges:
                if step_by_step:
                    print("-------------------------------------------------------------------------")
                    print("Arc beginning at node ", begin_node, "and ending in node ", end_node," with cost ", weight, ".")
                    print("Minimum cost of node", end_node, "before:", self.min_costs[end_node])
                self.min_costs[end_node] = min(self.min_costs[end_node], self.min_costs[begin_node] + weight)
                if step_by_step:
                    print("Minimum cost of node", end_node, "after:", self.min_costs[end_node])
            i += 1
            
        if step_by_step:
            print("-------------------------------------------------------------------------")
            print("Test if there is a negative loop:")
        for begin_node, end_node, weight in self.next_edges:
                if self.min_costs[end_node] > self.min_costs[begin_node] + weight:
                    if step_by_step:
                        print("There is a negative loop including the arc that goes from ", begin_node, " to ", end_node)
                    return False
        if step_by_step:
            print("There is no negative loop.")
        return True

class Johnson(Graph):
    
    def __init__(self, graph):
        self.nodes = graph.nodes
        self.num_nodes = graph.num_nodes
        self.min_costs = None
        self.nodes_weights = np.zeros(self.num_nodes)
    
    def create_aux_graph(self):
        aux_graph = Graph()
        aux_graph.create_graph_by_num_of_nodes(self.num_nodes)
        for node in self.nodes:
            from_node = node.index_in_graph
            for to_node, weight in node.neighbors.items():
                new_weight = weight + self.nodes_weights[from_node] - \
                                self.nodes_weights[to_node]
                aux_graph.add_edge_from_to(from_node, to_node, new_weight)
        return aux_graph
    
    def get_nodes_weights(self):
        self.new_completely_connected_v()
        aux_bellman_ford = BellmanFord(self)
        aux_bellman_ford.run(node_idx=self.num_nodes-1)
        self.nodes_weights = aux_bellman_ford.min_costs[:-1]
        self.remove_node(self.nodes[-1])
        self.min_costs = None
        
    def run_dijkstras(self, new_graph):
        dijkstras_nodes = []
        for node in range(self.num_nodes):
            aux = Dijkstra(new_graph)
            aux.run(node_idx=node)
            dijkstras_nodes.append(aux.min_costs)
        return dijkstras_nodes
        
    def calculate_min_costs(self, dijkstras, new_graph):
        self.min_costs = np.zeros((self.num_nodes, self.num_nodes))
        for from_node, mins in enumerate(dijkstras):
            for to_node, minimum in enumerate(mins):
                self.min_costs[from_node][to_node] = \
                    minimum - \
                    self.nodes_weights[from_node] + \
                    self.nodes_weights[to_node]
        
    def run(self):
        self.get_nodes_weights()
        new_graph = self.create_aux_graph()
        dijkstras = self.run_dijkstras(new_graph=new_graph)
        self.calculate_min_costs(dijkstras=dijkstras, new_graph=new_graph)
        
