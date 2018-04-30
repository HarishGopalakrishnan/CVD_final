import networkx as nx
import copy
import itertools
import random

#user defined functions
import kernelization as kernel
import print_graph
import get_graph

def union(first,second):
	#find the union of two lists
	return list(set(first)|set(second))

#2^k vertex cover
def vertex_cover(G_t,G,k,solution):
	"""
	Input: Graph G_t,G, parameter k
	Output: Check if G_t has a vertex cover of size at most k
	Description: A two way branching algorithm for vertex cover
	"""
	for i in range(k+1):
		for node in itertools.combinations(G.nodes(), i):
			G0=copy.deepcopy(G)
			G0.remove_nodes_from(union(list(node),list(solution)))
			if G0.number_of_edges()==0:
				return node
	"""				
	if G.number_of_edges()==0:
		#print (solution)
		global sol3
		sol3=solution
		return solution
	if k<=0:
		return False
	edges=G.edges()
	edge=edges[0]
	G0=copy.deepcopy(G)
	G0.remove_node(edge[0])
	G1=copy.deepcopy(G)
	G1.remove_node(edge[1])
	return vertex_cover(G_t,G0,k-1,solution+[edge[0]]) or vertex_cover(G_t,G1,k-1,solution+[edge[1]])
	"""

#reduction of Graph to instance of vertex cover by using the permanent vertices
def connected_component_isclique(Graph):
	"""
	Input:Graph
	Output: True if Graph is clique else False
	"""
	nodes=Graph.nodes()
	if len(nodes)==1:
		return True
	for i in range(0,len(nodes)):
		if not set(Graph.neighbors(nodes[i]))==(set(nodes)-set([nodes[i]])):
			return False
	return True

def reduction_to_vc(G,k,permanent):
	"""
	Input: graph G, parameter k, permanent vertices
	Output: Convert G into a instance vertex cover for the given vertex cover
	Description: Convert G into a instance vertex cover for the given vertex cover
	"""
	solution=set()
	neighbors=set()
	clique=[]
	clique_nodes=[]
	'''removes all vertex from G that are not adjacent to any permanent vertex and are adjacent to more than one permanent vertex'''
	for connected_component in nx.connected_component_subgraphs(G):
		cc_nodes=connected_component.nodes()
		if connected_component_isclique(connected_component) and len(list(set(cc_nodes)&set(permanent)))==0:
			clique.append(cc_nodes)
			clique_nodes+=cc_nodes
	
	G.remove_nodes_from(clique_nodes)
	permanent=list(set(permanent)-set(clique_nodes))
	for p_vertex in permanent:
		neighbors.add(p_vertex)
		for neighbor in G.neighbors(p_vertex):
			if neighbor  not in neighbors and neighbor not in permanent:
				neighbors.add(neighbor)
			elif neighbor not in solution and neighbor not in permanent:
				neighbors.remove(neighbor)
				solution.add(neighbor)
	
	nodes=set(G.nodes())
	solution=list(solution)
	non_neighbors=list(nodes-neighbors)
	solution=union(list(solution),non_neighbors)
	k-=len(solution)
	#print(neighbors,solution)
	#G.remove_nodes_from(union(list(solution),non_neighbors))
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
	return G,k,permanent,list(solution),clique	

def cvdp(G,B,k,d):
	"""
	Input: Graph G, permanent vertices B, parameter k and d
	Output: True and solution if there exists a k-vertex d-CVD set else False
	Description: Check if there exists a k-vertex d-CVD set
	"""
	dprime=d
	G_temp=copy.deepcopy(G)
	G_vc,k,B,solution,cliques=reduction_to_vc(G_temp,k,B) # convert d-CVD to a vertex Cover instance for the given permanent vertex
	G_t=copy.deepcopy(G_vc)	
	if k>=0:
		vc_solution=vertex_cover(G_t,G_vc,k,solution) # get the vertex for the reduced vertex cover instance
		if not vc_solution==None:
			k-=len(vc_solution)
			cliques.sort(key=len)
			while dprime>0 and len(cliques)>0: # select only the maximal d number of cliques
				 del cliques[-1]
				 dprime-=1
			#print(cliques)
			if len(cliques)>0: # delete excess clique that is present
				for lst in cliques:
					k-=len(lst)
					solution=list(solution)+list(lst)
			solution+=list(vc_solution)
			#print(len(solution),k,dprime)
			if k>=0 and dprime==0:
				# return a k-vertex d-CVD set
				return True,solution
	return False,[]

def find_p3_case1(G_in,B,X):
	"""
	Find P3 that satisfy the case 1 
	"""
	G=copy.deepcopy(G_in)
	G.remove_nodes_from(X)
	for permanent in B:
		G.remove_nodes_from(G.neighbors(permanent)+[permanent])
	for v1 in G.nodes():
		for v2 in G.nodes():
			for v3 in G.nodes():
				if (not v1==v2) and (not v2==v3) and (not v1==v3):
					if (G.has_edge(v1, v2) and G.has_edge(v2, v3) and not G.has_edge(v3, v1)):
						return True,v1,v2,v3
					if (G.has_edge(v1, v2) and not G.has_edge(v2, v3) and  G.has_edge(v3, v1)):
						return True,v2,v1,v3
					if (not G.has_edge(v1, v2) and G.has_edge(v2, v3) and G.has_edge(v3, v1)):
						return True,v1,v3,v2
	return False,-1,-1,-1

def find_p3_case2_1(G_in,B,X):
	"""
	Find P3 that satisfy the case 2_1 
	"""
	G=copy.deepcopy(G_in)
	G.remove_nodes_from(X)
	neighbors=[]
	for permanent in B:
		neighbors+=G.neighbors(permanent)
	neighbors=list(set(neighbors))+B
	for v1 in G.nodes():
		for v2 in G.nodes():
			for v3 in G.nodes():
				if (not v1==v2) and (not v2==v3) and (not v1==v3):
					if (G.has_edge(v1, v2) and G.has_edge(v2, v3) and not G.has_edge(v3, v1)):
						if v1 in B and v3 not in neighbors:
							return True,v1,v2,v3
						if v3 in B and v1 not in neighbors:
							return True,v3,v2,v1
					if (G.has_edge(v1, v2) and not G.has_edge(v2, v3) and  G.has_edge(v3, v1)):
						if v2 in B and v3 not in neighbors:
							return True,v2,v1,v3
						if v3 in B and v2 not in neighbors:
							return True,v3,v1,v2
					if (not G.has_edge(v1, v2) and G.has_edge(v2, v3) and G.has_edge(v3, v1)):
						if v1 in B and v2 not in neighbors:
							return True,v1,v3,v2
						if v2 in B and v1 not in neighbors:
							return True,v2,v3,v1
	return False,-1,-1,-1

def s_notAdj2v(G,nonPermanent_neighbors_u,v):
	for s in nonPermanent_neighbors_u:
		if not G.has_edge(v,s):
			return True
	return False
def find_p3_case2_2(G_in,B,X):
	"""
	Find P3 that satisfy the case 2_2
	"""
	G=copy.deepcopy(G_in)
	G.remove_nodes_from(X)
	neighbors=[]
	for permanent in B:
		neighbors+=G.neighbors(permanent)
	neighbors=list(set(neighbors))
	for v1 in G.nodes():
		for v2 in G.nodes():
			for v3 in G.nodes():
				if (not v1==v2) and (not v2==v3) and (not v1==v3):
					if (G.has_edge(v1, v2) and G.has_edge(v2, v3) and not G.has_edge(v3, v1)):
						if v1 in B and v3 in neighbors and s_notAdj2v(G,list(set(G.neighbors(v1))-set(B)-set([v2])),v2):
							return True,v1,v2,v3
						if v3 in B and v1 in neighbors and s_notAdj2v(G,list(set(G.neighbors(v3))-set(B)-set([v2])),v2):
							return True,v3,v2,v1
					if (G.has_edge(v1, v2) and not G.has_edge(v2, v3) and  G.has_edge(v3, v1)):
						if v2 in B and v3 in neighbors and s_notAdj2v(G,list(set(G.neighbors(v2))-set(B)-set([v1])),v1):
							return True,v2,v1,v3
						if v3 in B and v2 in neighbors and s_notAdj2v(G,list(set(G.neighbors(v3))-set(B)-set([v1])),v1):
							return True,v3,v1,v2
					if (not G.has_edge(v1, v2) and G.has_edge(v2, v3) and G.has_edge(v3, v1)):
						if v1 in B and v2  in neighbors and s_notAdj2v(G,list(set(G.neighbors(v1))-set(B)-set([v3])),v3):
							return True,v1,v3,v2
						if v2 in B and v1 in neighbors and s_notAdj2v(G,list(set(G.neighbors(v2))-set(B)-set([v3])),v3):
							return True,v2,v3,v1
	return False,-1,-1,-1

def find_p3_case2_3(G_in,B,X):
	"""
	Find P3 that satisfy the case 2_3
	"""
	G=copy.deepcopy(G_in)
	G.remove_nodes_from(X)
	neighbors=[]
	for permanent in B:
		neighbors+=G.neighbors(permanent)
	neighbors=list(set(neighbors))
	for v1 in G.nodes():
		for v2 in G.nodes():
			for v3 in G.nodes():
				if (not v1==v2) and (not v2==v3) and (not v1==v3):
					if (G.has_edge(v1, v2) and G.has_edge(v2, v3) and not G.has_edge(v3, v1)):
						if v1 in B and v3 in neighbors and s_notAdj2v(G,list(set(G.neighbors(v2))-set(B)-set([v1,v3])),v1):
							return True,v1,v2,v3
						if v3 in B and v1 in neighbors and s_notAdj2v(G,list(set(G.neighbors(v2))-set(B)-set([v3,v1])),v3):
							return True,v3,v2,v1
					if (G.has_edge(v1, v2) and not G.has_edge(v2, v3) and  G.has_edge(v3, v1)):
						if v2 in B and v3 in neighbors and s_notAdj2v(G,list(set(G.neighbors(v1))-set(B)-set([v2,v3])),v2):
							return True,v2,v1,v3
						if v3 in B and v2 in neighbors and s_notAdj2v(G,list(set(G.neighbors(v1))-set(B)-set([v3,v2])),v3):
							return True,v3,v1,v2
					if (not G.has_edge(v1, v2) and G.has_edge(v2, v3) and G.has_edge(v3, v1)):
						if v1 in B and v2  in neighbors and s_notAdj2v(G,list(set(G.neighbors(v3))-set(B)-set([v1,v2])),v1):
							return True,v1,v3,v2
						if v2 in B and v1 in neighbors and s_notAdj2v(G,list(set(G.neighbors(v3))-set(B)-set([v2,v1])),v2):
							return True,v2,v3,v1
	return False,-1,-1,-1

def find_v_case2_4(G_in,B,X):
	"""
	Find P3 that satisfy the case 2_4 
	"""
	G=copy.deepcopy(G_in)
	G.remove_nodes_from(X)
	neighbors=[]
	for permanent in B:
		neighbors+=G.neighbors(permanent)
	neighbors=list(set(neighbors)-set(B))
	for v1 in B:
		for v2 in list(set(G.nodes())-set(B)):
			for v3 in neighbors:
				if (not v1==v2) and (not v2==v3) and (not v1==v3):
					if (G.has_edge(v1, v2) and G.has_edge(v2, v3) and not G.has_edge(v3, v1)):
						if list(set(G.neighbors(v2))|set([v2]))==list(set(G.neighbors(v1))|set([v1,v2])):
							return True,v2
	return False,-1,


def reductionRule6(G_in,B,X):
	"""
	Remove non permanent vertex which is adjacent more than one permanent vertex
	"""
	G=copy.deepcopy(G_in)
	G.remove_nodes_from(X)
	for v1 in G.nodes():
		for v2 in G.nodes():
			for v3 in G.nodes():
				if (not v1==v2) and (not v2==v3) and (not v1==v3):
					if (G.has_edge(v1, v2) and G.has_edge(v2, v3) and not G.has_edge(v3, v1)):
						if v1 in B and v3 in B:
							return True,v2
					if (G.has_edge(v1, v2) and not G.has_edge(v2, v3) and  G.has_edge(v3, v1)):
						if v2 in B and v3 in B:
							return True,v1
					if (not G.has_edge(v1, v2) and G.has_edge(v2, v3) and G.has_edge(v3, v1)):
						if v1 in B and v2 in B:
							return True,v3
	return False,-1
	
	
def notindependent_B(G,B):
	"""
	Check if two permenant vertex are adjacent
	"""
	for p1 in B:
		for p2 in B:
			if not p1==p2 and G.has_edge(p1,p2):
				return True
	return False

def branching(G_in,B,k,d,X):
	
	G=copy.deepcopy(G_in)
	G.remove_nodes_from(list(set(G.nodes()) & set(X)))
	if (d<0) or (k<0):
		return False
		
	#reduction rule own
	if notindependent_B(G,B):
		return False
		
	if d==0: # Base Case 1: check for k-vertex d-CVD; no more guessing of permanent vertex
		solution=cvdp(G,B,k,d)
		if not solution[0]:
			return False
		else:
			global sol
			sol=list(set(solution[1])|set(X))
			return True	
	if k==0: # Base Case 2: check if G is d-CVD; no more vertex deletion
		solution=cvdp(G,B,k,d)
		if not solution[0]:
			return False
		else:
			sol=X
			return True
	
	while(True):#ReductionRule6
		flag,v=reductionRule6(G,B,X)
		if flag:
			k-=1
			X+=[v]
		else:
			break
		
	G.remove_nodes_from(X)
	flag,u,v,w=find_p3_case1(G,B,X)
	if flag:#case1
		return branching(G,B,k-1,d,X+[u]) or branching(G,B+[u],k-1,d-1,X+[w]) or branching(G,B+[u,w],k-1,d-2,X+[v])
	flag,u,v,w=find_p3_case2_1(G,B,X)
	if  flag:#case2_1
		return branching(G,B,k-1,d,X+[w]) or branching(G,B+[w],k-1,d-1,X+[v])
	flag,u,v,w=find_p3_case2_2(G,B,X)
	if  flag:#case2_2
		return branching(G,B,k-1,d,X+[v])
	flag,u,v,w=find_p3_case2_3(G,B,X)
	if  flag:#case2_3
		return branching(G,B,k-1,d,X+[v])
	flag,v=find_v_case2_4(G,B,X)
	if flag:#case2_4
		return branching(G,B,k-1,d,X+[v])
	#print("Case 3")
	if nx.number_connected_components(G)>=d:
		solution=cvdp(G,B,k,d)
		if not solution[0]:
			return False
		else:
			sol= X
			return True
	return False	
	


def main():
	G=get_graph.edge_list()	# read the input instance
	print_graph.input(G)
	k=int(input("Enter k:"))
	d=int(input("Enter d:"))
	G,k,kernel_solution=kernel.kernelization(G,k) # do kernelization
	print("Kernelization",k,kernel_solution)
	if not branching(G,[],k,d,[]):
		print ("No Solution")
	else:
		print("CVD solution: ",sol)
		G.remove_nodes_from(sol)
		print_graph.output(G)
		print_graph.show()
		
if __name__== "__main__":
	main()
