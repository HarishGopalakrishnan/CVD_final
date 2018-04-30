#system packages
import networkx as nx
import copy
import itertools

 #user defined functions
import kernelization as kernel
import print_graph
import get_graph



#2^k vertex cover
def vertex_cover(G_t,G,k,solution):
	"""
	Input: Graph G_t,G, parameter k
	Output: Check if G_t has a vertex cover of size at most k
	Description: A two way branching algorithm for vertex cover
	"""
	if k<0:
		return False
		
	if G.number_of_edges()==0:
		#print (solution)
		global sol
		sol=solution	
		return True
	edges=G.edges()
	edge=edges[0] # arbitrarily select an edge and branch on it
	G0=copy.deepcopy(G)
	G0.remove_node(edge[0])
	G1=copy.deepcopy(G)
	G1.remove_node(edge[1])
	return vertex_cover(G_t,G0,k-1,solution+[edge[0]]) or vertex_cover(G_t,G1,k-1,solution+[edge[1]])
	

#reduction of Graph to instance of vertex cover by using the permanent vertices
def reduction_to_vc(G,k,permanent):
	for vertex1 in permanent:
		for vertex2 in permanent:
			if (not vertex1==vertex2):
				if G.has_edge(vertex1,vertex2):
					return G,-1,[]
	solution=set()
	neighbors=set()
	'''removes all vertex from G that are not adjacent to any permanent vertex and are adjacent to more than one permanent vertex'''
	for p_vertex in permanent:
		neighbors.add(p_vertex)
		for neighbor in G.neighbors(p_vertex):
			if neighbor  not in neighbors and neighbor not in permanent:
				neighbors.add(neighbor)
			elif neighbor not in solution and neighbor not in permanent:
				neighbors.remove(neighbor)
				solution.add(neighbor) # Reduction Rule 1
	
	nodes=set(G.nodes())
	solution=list(set(list(solution)+list(nodes-neighbors)))	# Reduction Rule 2
	k-=len(solution)
	G.remove_nodes_from(list(solution))
	'''convert G to instance of vertex cover by removing adjacent vertices of non permanent vertices or insert otherwise '''	
	delete_edges=[]
	add_edges=[]
	for p_vertex in permanent:
		neighbors=[]
		neighbors+=G.neighbors(p_vertex)
		neighbors.append(p_vertex)
		G2=nx.subgraph(G,neighbors)
		delete_edges+=G2.edges()
		add_edges+=(nx.complement(G2)).edges()
		#print(delete_edges)
		#print(add_edges)
	G.remove_edges_from(delete_edges)
	G.add_edges_from(add_edges)
	#print(G.edges())
	return G,k,list(solution)		

def brute_on_d(G,k,d):
	#iteratively check for CVD with given G,k,d
	for permanent in itertools.combinations(G.nodes(), d): # iterate on all subsets of size d
		k1=k
		G_temp=copy.deepcopy(G)
		G_vc,k1,solution=reduction_to_vc(G_temp,k1,permanent) # reduction to vertex cover
		G_t=copy.deepcopy(G_vc)	
		if k1>=0:
			if vertex_cover(G_t,G_vc,k1,solution): # check if k-vertex d-CVD 
				print("Solution",sol)
				return True
	return False
	
def main():
	G=get_graph.edge_list()	# read the input instance
	print_graph.input(G)
	k=int(input("Enter k:"))
	d=int(input("Enter d:"))
	G,k,kernel_solution=kernel.kernelization(G,k) # do kernelization
	print("Kernelization",k,kernel_solution)
	if not brute_on_d(G,k,d): # do brute force on d
		print ("No Solution")
	else:
		print("d-CVD solution: ",sol)
		G.remove_nodes_from(sol)
		print_graph.output(G)
		print_graph.show()

if __name__== "__main__":
	main()
