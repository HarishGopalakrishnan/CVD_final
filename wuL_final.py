import networkx as nx
import matplotlib.pyplot as plt
import copy,math
import itertools
import random 
import sys

#user defined functions
import kernelization as kernel
import print_graph
import get_graph
infinity=9999

def union(a,b):
	#union of two list
	return list(set(a)|set(b))

def print_graph(G):
	plt.figure()
	number_of_connect_components=nx.number_connected_components(G)
	if number_of_connect_components==1:
		pos = nx.circular_layout(G)
		nx.draw(G,pos,with_labels=True)
	else:
		i=1
		for a in nx.connected_component_subgraphs(G):	
			pos = nx.circular_layout(a)
			plt.subplot(math.ceil(number_of_connect_components/2),2,i)
			i+=1
			nx.draw(a,pos,with_labels=True)	
	plt.show()



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
				return True,list(node)
	return False,[]
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
	"""
				
#reduction of Graph to instance of vertex cover by using the permanent vertices
def reduction_to_vc(G,k,permanent):
	#print("REductionto VC",G.nodes())
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
				solution.add(neighbor)
	
	nodes=set(G.nodes())
	solution=(nodes-neighbors)	
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
	G.remove_edges_from(delete_edges)
	G.add_edges_from(add_edges)
	return G,k,list(solution)		


def cvdp(G,B,d,k,L):
	"""
	Input: Graph G, permanent vertex set B, parameters k and d, alternative list L
	Output: Check if G has a vertex cover of size at most k
	"""
	G_temp=copy.deepcopy(G)
	permanent=list(set(B)&set(G_temp.nodes()))
	G_vc,k,solution=reduction_to_vc(G_temp,k,permanent) # reduction to vertex cover
	G_t=copy.deepcopy(G_vc)
	G_clique=copy.deepcopy(G)	
	if k>=0:
		vc_result=vertex_cover(G_t,G_vc,k,solution) # find vertex cover
		if vc_result[0]:
			G_clique.remove_nodes_from(union(solution,vc_result[1]))
			for connected_component in nx.connected_component_subgraphs(G_clique):
				L=update_L(L,[len(connected_component.nodes()),0,infinity]) # update the alternative list
			return solution+vc_result[1],L
	return None,L

def is_cluster_graph(Graph):
	"""
	Input: Graph
	Output: True if graph is a cluster graph ,false otherwise
	"""
	cliques=[]
	for connected_component in nx.connected_component_subgraphs(Graph):
		cliques.append(connected_component)
		if not connected_component_isclique(connected_component): # check if connected component is clique
			return False,[]
		
	return True,cliques

def connected_component_isclique(Graph):
	"""
	Input: Graph
	Output: True if graph is a clique ,false otherwise
	"""
	nodes=Graph.nodes()
	if len(nodes)==1:
		return True
	for i in range(0,len(nodes)):
		if not set(Graph.neighbors(nodes[i]))==(set(nodes)-set([nodes[i]])):
			return False
	return True


def connected_component_has_critical_vertex(Graph):
	"""
	Input: Graph
	Output: 1) True if graph G\v (v is critical vertex) is a cluster graph ,false otherwise
		2) clique set
		3) critical vertex
	"""
	
	nodes=Graph.nodes()
	for node in nodes:
		nodes_minus_node=list(set(nodes)-set([node]))
		Graph_minus_node=Graph.subgraph(nodes_minus_node).copy()
		result=is_cluster_graph(Graph_minus_node)
		if result[0]:
			return True,result[1],node
	return False,[],-1


def update_L(in_L1,in_L2):
	"""
	Input: Two alternative list in_L1, in_L2
	Output: Resultant alternative list
	"""
	L1=copy.deepcopy(in_L1)
	L2=copy.deepcopy(in_L2)
	len_L1=len(L1)
	len_L2=len(L2)
	for i in range(len_L1):  # adjust alternative list
		L2.append(infinity)
	for i in range(len_L2):
		L1.append(infinity)
	len_L1=len(L1)
	len_L2=len(L2)
	res_L=[0 for i in range(len_L1)]
	for i in range(len_L1): # Property P3: 
		minimum=infinity
		for j in range(0,i+1):
			val=L1[j]+L2[i-j]	
			if val<minimum:
				minimum=val
		res_L[i]=minimum
	while infinity in res_L: # remove trailing infinity
            res_L.remove(infinity)	
	res_L.append(infinity)
	if len(res_L)==1: # reset alternative list
		res_L=[0]
	return res_L

def reductionRule2(G,U0,U1,U2,B,L):
	"""
	Input: Graph G, U0,U1,U2, permanent vertex set B, alternative List L
	Description: Reduction Rule2: Move isolated cliques from U1 and U2 to U0, and update alternative list
	"""
	G1=G.subgraph(list(set(U1)|set(U2))).copy()
	#print("InRR2",G1.nodes())
	cliques=[]
	for connected_component in nx.connected_component_subgraphs(G1):	
		if connected_component_isclique(connected_component):
			cc_nodes=connected_component.nodes()
			U0.append(cc_nodes)
			cliques.append(len(cc_nodes))
			U1=list(set(U1)-set(cc_nodes))
			U2=list(set(U2)-set(cc_nodes))
	for clique in cliques:
		"""Alternative list property:P3"""
		L=update_L(L,[clique,0,infinity])
	del G1
	return U0,U1,U2,B,L



def reductionRule3(G,U0,U1,U2,B,L,X):
	"""
	Input: Graph G, U0,U1,U2, permanent vertex set B, alternative List L
	Description: Reduction Rule3: Move connected component C containing critical vertex v (i.e C\v is cluster graph) from U1 and U2 to U0, and update alternative list
	"""
	G1=G.subgraph(list(set(U1)|set(U2))).copy()
	for connected_component in nx.connected_component_subgraphs(G1):	
		result=connected_component_has_critical_vertex(connected_component)
		if result[0]:
			dPlusG=[0]
			for i in range(len(result[1])):
				dPlusG=update_L(dPlusG,[len(result[1][i]),0,infinity])
			diPlusG=[x+1 for x in dPlusG]
			diMinusG=[infinity for x in diPlusG]
			for i in range(len(result[1])):
				neighbor_criticalVertex=G1.neighbors(result[2])+[result[2]]
				Ci=result[1][i]
				clique_Ci=list(set(Ci)&set(neighbor_criticalVertex))
				is_nodes_clique=clique_Ci+[result[2]]
				G2=G1.subgraph(is_nodes_clique).copy()
				if_clique=is_cluster_graph(G2)
				if if_clique[0]:
					CVDset=union(list(set(Ci)-set(neighbor_criticalVertex)),list(set(neighbor_criticalVertex)-set(Ci)-set([result[2]])))
					dMinusCi=[0]
					for j in range(len(result[1])):
						if list(result[1][j])==list(Ci):
							dMinusCi=update_L(dMinusCi,[len(Ci)-len(list(set(result[1][j])&set(CVDset)))+1,0,infinity])
						elif len(list(set(result[1][j])-set(CVDset)))>0:					
							dMinusCi=update_L(dMinusCi,[len(list(set(result[1][j])-set(CVDset))),0,infinity])
					len_CVDset=len(CVDset)
					dMinusCi=[x+len_CVDset for x in dMinusCi]
					while len(dMinusCi)<len(diMinusG):
						dMinusCi.append(infinity)
					diMinusG=[min(dMinusCi[k],diMinusG[k]) for k in range(len(diMinusG))]
				dMinusCi=[1,0,infinity]
				CVDset=G1.neighbors(result[2])
				for j in range(len(result[1])):
					if len(list(set(result[1][j])-set(CVDset)))>0:					
						dMinusCi=update_L(dMinusCi,[len(list(set(result[1][j])-set(CVDset))),0,infinity])
				len_CVDset=len(CVDset)
				dMinusCi=[x+len_CVDset for x in dMinusCi]
				while len(dMinusCi)<len(diMinusG):
					dMinusCi.append(infinity)
				diMinusG=[min(dMinusCi[k],diMinusG[k]) for k in range(len(diMinusG))]
					
			L_criticalVertex=[min(diPlusG[k],diMinusG[k]) for k in range(max(len(diPlusG),len(diMinusG)))]
			L_before=L
			L=update_L(L,L_criticalVertex)
			cc_nodes=connected_component.nodes()
			U0.append(cc_nodes)
			U1=list(set(U1)-set(cc_nodes))
			U2=list(set(U2)-set(cc_nodes))
	return U0,U1,U2,B,L,X

def reductionRule4(G,U0,U1,U2,B,k,d,L,X):
	"""
	Input: Graph G, U0,U1,U2, permanent vertex set B, alternative List L, parameters k and d
	Description: Reduction Rule4: If no edge between U1 and U2, then U1 and U2 can be solved separately
	"""
	if not len(U1) == 0 and not len(U2) == 0:
		for node1 in U1:
			for node2 in U2:
				if G.has_edge(node1,node2):
					return True,U0,U1,U2,L
		G_U1=G.subgraph(U1).copy()
		kprime,L1=cvdp(G_U1,B,d,k)
		if kprime==None:
			print("No solution")
			return False,U0,U1,U2,L
		elif len(kprime)>0:
			"""Search(G,U0,[],U2,[],d,k-cvdp(G,B,d,k),d,L,X)"""
			search(G,U0,[],U2,[],k-len(kprime),d,L,X)
			return False,U0,U1,U2,L
	return True,U0,U1,U2,L



def reductionRule5(k,L):
	"""
	Input: parameter k and alternative list L 
	Output: updated k and alternative list L
	Description: Update alternative list L  and k with minimum value of alternative list
	"""
	minL=min(L)
	if min(L)>0:
		k-=minL
		for val in range(len(L)-1):	
			L[val]=L[val]-minL
	return k,L
	
	
def reduction_rule(G,U0,U1,U2,B,k,d,L,X):
	U0,U1,U2,B,L=reductionRule2(G,U0,U1,U2,B,L)
	U0,U1,U2,B,L,X=reductionRule3(G,U0,U1,U2,B,L,X)
	flag,U0,U1,U2,L=reductionRule4(G,U0,U1,U2,B,k,d,L,X)
	if flag:
		k,L=reductionRule5(k,L)
		return True,U0,U1,U2,B,k,d,L,X
	return False,U0,U1,U2,B,k,d,L,X



def search(G,U0,U1,U2,B,k,d,L,X):
	flag,U0,U1,U2,B,k,d,L,X=reduction_rule(G,U0,U1,U2,B,k,d,L,X)
	if not flag:
		return False 
		
	#termination conditions
	if k<0 or d<0:
		return False
	#terminal case 1
	len_B=len(B)
	if k==0:
		if (not list(set(U1)|set(U2))) and len(L)>d+len_B and L[d+len_B]==0:
			print("Yes Instance")
			sys.exit()
		return False 	
		
	#terminal case 2
	if d==0:
		G_U1=G.subgraph(U1).copy()
		kprime,L=cvdp(G_U1,B,d,k,L)
		if not kprime==None and len(L)>len_B and len(kprime)+len(U2)+L[len_B]<=k:
			print("Yes Instance")
			sys.exit()
		return False
		
	#terminal case 3
	if len(U2)==0:
		G_U1=G.subgraph(U1).copy()
		kprime,L=cvdp(G_U1,B,d,k,L)
		if not kprime==None and len(L)>d+len_B and len(kprime)+L[d+len_B]<=k:
			print("Yes Instance")
			sys.exit()
		return False
	#case 1
	if len(U1)==0:
		v=random.choice(U2)
		neighbor_v=list((set(G.neighbors(v))-set(X))|set([v]))
		search(G,U0,neighbor_v,list(set(U2)-set(neighbor_v)),B+[v],k,d-1,L,X)
		search(G,U0,[],list(set(U2)-set([v])),B,k-1,d,L,X+[v])
	else:	
		neighbors_U1=[]
		for nodes in U1:
			neighbors_U1+=G.neighbors(nodes)
		neighbors_U1=list(set(neighbors_U1)-set(U1)-set(X))
		G_U1=G.subgraph(U1).copy()
		result=is_cluster_graph(G_U1)
		if (result[0]) and len(neighbors_U1)==1:
			L1=copy.deepcopy(L)
			for i in range(len(result[1])):
				L1=update_L(L1,[len(result[1][i]),0,infinity])
			#case 2
			u=neighbors_U1[0]
			neighbor_u_intersecting_U2=list(set(G.neighbors(u))&set(U2)-set(X))
			for v in neighbor_u_intersecting_U2:
				neighbor_v=list((set(G.neighbors(v))-set(X)-set([u]))|set(v))
				G_neigh_v=G.subgraph(neighbor_v).copy()
				if not connected_component_isclique(G_neigh_v):
					search(G,U0+U1,neighbor_v,list(set(U2)-set(neighbor_v+[u])),B+[v],k-1,d-1,L1,X+[u])
					search(G,U0,U1,list(set(U2)-set([v])),B,k-1,d,L,X+[v])
				
						
		else:
			#case3
			v=random.choice(neighbors_U1)
			neighbor_v=list((set(G.neighbors(v))-set(X))|set([v]))
			neighbor_v_U1=list(set(U1)&set(neighbor_v))
			U0_31=copy.deepcopy(U0)
			U0_32=copy.deepcopy(U0)
			search(G,U0_31,list(set(list(set(U1)|set(neighbor_v)))-set(list(set(U1)&set(neighbor_v)))),list(set(U2)-set(neighbor_v)),B+[v],k-len(neighbor_v_U1),d-1,L,X+neighbor_v_U1)
			search(G,U0_32,U1,list(set(U2)-set([v])),B,k-1,d,L,X+[v])



def main():
	G_in=get_graph.edge_list()	# read the input instance
	G=copy.deepcopy(G_in)
	k=int(input("Enter k:"))
	d=int(input("Enter d:"))
	G,k,kernel_solution=kernel.kernelization(G,k) # do kernelization
	print("Kernelization",k,kernel_solution)
	search_solution=search(G,[],[],G.nodes(),[],k,d,[0],[])
	print("No Solution")
if __name__== "__main__":
	main()
