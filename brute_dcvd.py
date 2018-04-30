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



def d_cvd(G,d,k,solution):
	"""
	Input: Graph G represented by p3s,the parameter k and d, solution
	Output: True,solution if the G has a k-sized d-cvd set or False
	"""
	number_cliques=nx.number_connected_components(G)
	if number_cliques<d: # Case 1: number of connected components is lesser than d
		return False,[]
	if number_cliques==d:  # Case 2: number of connected components is equal than d
		return True,solution
	else:	# Case 3: number of connected components is greater than d
		cliques={}
		for connected_component in nx.connected_component_subgraphs(G): # sort the cliques in non decreasing order
			cc_nodes=connected_component.nodes()
			if len(cc_nodes) not in cliques:
				cliques[len(cc_nodes)]=[cc_nodes]
			else:
				cliques[len(cc_nodes)].append(cc_nodes)
		
		while (not number_cliques==d) and k>0: # delete the cliques until d number of connected components(cliques) 
			key=sorted(cliques)[0]
			del_clique=cliques[key].pop(0)
			solution+=del_clique
			k-=key
			if cliques[key]==[]:
				del cliques[key]
			number_cliques-=1
		if k>=0 and number_cliques==d:
			return True,solution
		return False,[]

def brute(G,k,d):
	"""
	Input: Graph G, parameter k and d
	Output: k-vertex d-CVD-set if G has k-vertex d-CVD set else None
	"""
	#for solution in itertools.combinations(universe, k):
	for solution in itertools.combinations(G.nodes(), k):
		G_temp=copy.deepcopy(G)
		G_temp.remove_nodes_from(solution) 
		if is_cluster_graph(G_temp): # check if solution is a CVD set
			G_temp=copy.deepcopy(G)
			G_temp.remove_nodes_from(solution) 
			d_cvd_solution=d_cvd(G_temp,d,k,solution) # check if solution is a k-vertex d-cvd set
			if d_cvd_solution[0]:
				return d_cvd_solution[1]
	return []


def main():
	G=get_graph.edge_list()	# read the input instance
	print_graph.input(G)
	k=int(input("Enter k:"))
	d=int(input("Enter d:"))
	G,k,kernel_solution=kernel.kernelization(G,k) # do kernelization
	print("Kernelization",k,kernel_solution)
	brute_solution=brute(G,k,d) # do brute force
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
