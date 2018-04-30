import networkx as nx
import itertools
import copy

#user defined functions
import kernelization as kernel
import print_graph
import get_graph


def is_cluster_graph(Graph):
	"""
	Input: Graph
	Output: True if the given graph is a cluster graph else False
	Discription: Check if all connected component is a clique
	"""
	for connected_component in nx.connected_component_subgraphs(Graph):#enumerate all connected component
		if not connected_component_isclique(connected_component):# check if connected component is clique
			return False
	return True

def connected_component_isclique(Graph):
	"""
	Input: Graph
	Output: True if the given graph is a clique(complete graph) else False
	Discription: Check if every pair of vertices in graph has an edge 
	"""
	nodes=Graph.nodes()
	if len(nodes)==1:
		return True
	for i in range(0,len(nodes)):
		if not set(Graph.neighbors(nodes[i]))==(set(nodes)-set([nodes[i]])):
			return False
	return True


def brute(G,k):
	"""
	Input: Graph G, parameter k
	Output: k-vertex CVD-set if G has k-vertex CVD set else None
	"""
	#for solution in itertools.combinations(universe, k):
	for solution in itertools.combinations(G.nodes(), k):
		G_temp=copy.deepcopy(G)
		G_temp.remove_nodes_from(solution) 
		if is_cluster_graph(G_temp): # check if solution is a CVD set
			return solution
	return []
#iteratively check for CVD with given G,k,d				
def main():
	G=get_graph.edge_list()	# read the input instance
	print_graph.input(G)
	k=int(input("Enter k:"))
	G,k,kernel_solution=kernel.kernelization(G,k) # do kernelization
	print("Kernelization",k,kernel_solution)
	brute_solution=brute(G,k) # do brute force
	if k>0 and brute_solution == []:	
		print ("No Solution")
	else:
		solution=list(set(kernel_solution)|set(brute_solution)) # combine kernelization and brute force approach results
		print("CVD solution: ",solution)
		G.remove_nodes_from(solution)
		print_graph.output(G)
		print_graph.show()

if __name__== "__main__":
	main()
