#system packages
import networkx as nx
import copy
import random

#user defined programs
import get_graph
import print_graph
import kernelization as kernel


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


def connected_component_minus_w_isclustergraph(Graph):
	"""
	Input: Graph
	Output: critical vertex (v) if the given graph has a critical vertex (i.e G\v is cluster graph) else None 
	Discription: For all vertex in graph check if G\v is cluster graph
	"""

	nodes=Graph.nodes()
	for node in nodes:
		nodes_minus_node=list(set(nodes)-set([node]))
		Graph_minus_node=Graph.subgraph(nodes_minus_node).copy()
		if is_cluster_graph(Graph_minus_node):
			return node
	return

def construct_Hv(Graph,v):
	"""
	Input: Graph G, vertex v for which Hv is constructed
	Output: Graph Hv, N1, N2
	Discription: N1 is neighbors of v, N2 is neighbors of N1 (i.e vertices that are at a distance of 2 from v) Hv contains the vertices N1 and N2, edges of Hv are complement of N1 in graph G and edges between N1 and N2 in graph G
	"""

	N1=Graph.neighbors(v)
	N2=[]
	for nodes in N1:
		N2+=Graph.neighbors(nodes)
	N2=list(set(N2)-set(N1))
	if v in N2:
		N2.remove(v)
	Hv=nx.Graph()
	Hv.add_nodes_from(N1)
	Hv.add_nodes_from(N2)
	for node1 in N1:
		for node2 in N1:
			if (not node1==node2) and (not Graph.has_edge(node1,node2)):
				Hv.add_edge(node1,node2)
	for node1 in N1:
		for node2 in N2:
			if Graph.has_edge(node1,node2):
				Hv.add_edge(node1,node2)
	return Hv,N1,N2

def Hv_rule1(G,Hv,k,solution,permanent):
	"""
	Input: Graph G, auxilary graph Hv of vertex v, parameter k
	Discription: Check if Hv contains a vertex with degree atmost 3 and branch according if one exists
	"""

	for nodes in Hv.nodes():					
		neighbor_node=Hv.neighbors(nodes)
		if len(neighbor_node)>=3:
			G1=copy.deepcopy(G)
			G1.remove_node(nodes)
			G2=copy.deepcopy(G)
			G2.remove_nodes_from(neighbor_node)
			return True, branching(G1,k-1,solution+[nodes],permanent) or branching(G2,k-len(neighbor_node),solution+neighbor_node,permanent)
	return False, False

def Hv_rule2(G,Hv,N1,k,solution,permanent):
	"""
	Input: Graph G, auxilary graph Hv of vertex v, parameter k
	Discription: Check if Hv contains a vertex with degree 1 in N1 and branch according if one exists 
	"""
	for nodes in N1:
		neighbor_node=Hv.neighbors(nodes)
		if len(neighbor_node)==1:
			G1=copy.deepcopy(G)
			G1.remove_nodes_from(neighbor_node)
			return True, branching(G1,k-1,solution+neighbor_node,permanent)
	return False,False

def Hv_rule3(G,Hv,N1,k,solution,permanent):
	"""
	Input: Graph G, auxilary graph Hv of vertex v, parameter k
	Discription: Check if Hv contains a edge within N1 and branch according if one exists 
	"""

	for node1 in N1:
		for node2 in N1:
			if (not node1==node2) and Hv.has_edge(node1,node2):
				G1=copy.deepcopy(G)
				G1.remove_node(node1)
				G2=copy.deepcopy(G)
				G2.remove_node(node2)
				return True, branching(G1,k-1,solution+[node1],permanent) or branching(G2,k-1,solution+[node2],permanent)
	return False,False

def Hv_rule4(G,Hv,N2,k,solution,permanent):
	"""
	Input: Graph G, auxilary graph Hv of vertex v, parameter k
	Discription: Check if Hv contains a cycle and branch according if one exists 
	"""

	try:
		cycle=nx.find_cycle(Hv,source=None,orientation='ignore')
		if len(cycle)%2==0:
			cycle_nodes=set()
			for edge in cycle:
				cycle_nodes.add(edge[0])
				cycle_nodes.add(edge[1])
			N2_cycle=list(cycle_nodes & set(N2))
			G1=copy.deepcopy(G)
			G1.remove_nodes_from(N2_cycle)
			return True, branching(G1,k-len(N2_cycle),solution+N2_cycle,permanent)
		else:
			return False,False
	except:
		return False,False

def Hv_rule5(G,Hv,N1,N2,k,solution,permanent):
	"""
	Input: Graph G, auxilary graph Hv of vertex v, parameter k
	Discription: Branch on the longest path between N1 and N2 
	"""

	longest_path=[]
	vertices=[]
	for nodes in Hv.nodes():
		if Hv.degree(nodes)==1:
			vertices.append(nodes)
	for node1 in vertices:
		for node2 in vertices:
			if not node1==node2:
				for path in nx.all_simple_paths(Hv, source=node1, target=node2):
					if len(path)>len(longest_path):
						longest_path=path
	path_intersect_N1=list(set(longest_path)&set(N1))
	path_intersect_N2=list(set(longest_path)&set(N2))
	G1=copy.deepcopy(G)
	G1.remove_nodes_from(path_intersect_N1)
	G2=copy.deepcopy(G)
	G2.remove_nodes_from(path_intersect_N2)
	return branching(G1,k-len(path_intersect_N1),solution+path_intersect_N1,permanent) or branching(G2,k-len(path_intersect_N2),solution+path_intersect_N2,permanent) 

def s_skein(Hv,N1,N2):
	"""
	Input: Auxilary graph Hv of vertex v, NN1 and N2 of v
	Output: True if Hv is a s-skein for some s else False
	Discription: Check if Hv is a s-skein for some s 
	"""
	for y in N1:
		y_neighbor=Hv.neighbors(y)
		if len(y_neighbor)==0:
			continue
		if not len(y_neighbor)==2 :
			return False
		else:
			y_neighbor_in_N2=list(set(y_neighbor)-set(N1))
			if not len(y_neighbor_in_N2)==2:
				return False
	return True


def is_vertexcover(G,vc):
	"""
	Input: Graph G and vertex cover vc
	Output: True if vc is a vertex cover of G else False
	Discription: Check if vc is a vertex cover of G  
	"""
	G.remove_nodes_from(vc)
	if G.edges():
		return False
	return True

def vc_1(Hv):
	"""
	Input: Auxilary graph Hv of vertex v
	Output: True if Hv has a vertex cover of size one else False
	Discription: Check if Hv has a vertex cover of size one
	"""
	for nodes in Hv.nodes():
		Hv1=copy.deepcopy(Hv)
		if is_vertexcover(Hv1,[nodes]):
			return True
		del Hv1
	return False

def vc_2(Hv):
	"""
	Input: Auxilary graph Hv of vertex v
	Output: Vertex cover of size two if Hv has a vertex cover of size two else False
	Discription: Check if Hv has a vertex cover of size two
	"""
	for node1 in Hv.nodes():
		for node2 in Hv.nodes():
			if not node1==node2:
				Hv1=copy.deepcopy(Hv)
				if is_vertexcover(Hv1,[node1,node2]):
					return [node1,node2]
				del Hv1
	return [-1]

def Algo_Hv(G,Hv,N1,N2,k,solution,permanent):
	"""
	Discription: Branching Algorithm on Hv
	Input: Graph G, Auxilary graph Hv of vertex v, N1,N2,K
	
	"""
	Hv_rule1_=Hv_rule1(G,Hv,k,solution,permanent) #Rule 1 where Hv has a vertex with degree 3
	if Hv_rule1_[0]:
		return Hv_rule1_[1]
	else:
		Hv_rule2_=Hv_rule2(G,Hv,N1,k,solution,permanent) #Rule 2 where there is vertex v in N1 with degree 1
		if Hv_rule2_[0]:
			return Hv_rule1_[1]
		else:
			Hv_rule3_=Hv_rule3(G,Hv,N1,k,solution,permanent) #Rule 3 if there is a edge in G[N1]
			if Hv_rule3_[0]:
				return Hv_rule3_[1]
			else:
				Hv_rule4_=Hv_rule4(G,Hv,N2,k,solution,permanent) #Rule 4  if there is a cycle in Hv
				if Hv_rule4_[0]:
					return Hv_rule4_[1]
				else:
					return Hv_rule5(G,Hv,N1,N2,k,solution,permanent)  #Rule 5 longest path

def cc_w_notclique(G,w):
	"""
	Input: Graph G, vertex w
	Output: True is connected component containing w is a clique else False
	Discription: Check if connected component containing w is not a clique
	"""
	for connected_component in nx.connected_component_subgraphs(G):
		if w in connected_component:
			return connected_component_isclique(connected_component)
					
def branching(G_branch,k,solution,permanent):
	"""
	Discription: Check if there exists a k-vertex CVD set for G_branch
	Input: Graph G_branch, parameter k, solution and permanent vertices
	Output: True if graph contains a k-vertex CVD set  else False
	"""
	G=copy.deepcopy(G_branch)
	count=0
	for connected_component in nx.connected_component_subgraphs(G_branch):
		count+=1	
		if connected_component_isclique(connected_component): #Preprocessing Rule 1: Remove connected component if it is Clique
			count-=1
			G.remove_nodes_from(connected_component.nodes())
		else: 
			w=connected_component_minus_w_isclustergraph(connected_component) #Preprocessing Rule 2: Remove connected component  C if has a vertex v such that C\v is cluster graph
			if not w==None:
				#print("w",w)
				count-=1
				solution+=[w]
				k-=1
				G.remove_nodes_from(connected_component.nodes())
	if count==0 and k>=0: # Base Case 1: Yes Instance
		print("Solution:",solution)
		global sol
		sol=solution
		return True
	if k<=0: # Base Case 2: Branch fails
		return False
	else:
		try:
			v=random.choice(list(set(G.nodes())-set(permanent))) # Pick an Arbitrary vertex v
		except:
			return False
		Hv,N1,N2=construct_Hv(G,v) # Construct Hv for v
		if (s_skein(Hv,N1,N2)):	# Case1: if Hv contains an s-skein
			G1=copy.deepcopy(G)
			return Algo_Hv(G1,Hv,N1,N2,k,solution,permanent+[v])
		else:
			if vc_1(Hv): # Case1 : if Vertex Cover of Hv is one 
				G1=copy.deepcopy(G)
				return Algo_Hv(G1,Hv,N1,N2,k,solution,permanent+[v])
			vc_2_Hv=vc_2(Hv)
			if len(vc_2_Hv)==2: # Case2 : if Vertex Cover of Hv is two
				G1=copy.deepcopy(G)
				G2=copy.deepcopy(G)
				G1.remove_node(v)		
				if cc_w_notclique(G1,vc_2_Hv[0]):
					w=vc_2_Hv[0]
				else:
					w=vc_2_Hv[1]
				Hw,N1w,N2w=construct_Hv(G1,w) 
				# Branch on minimum solution containing v and minimum solution not containing v
				return Algo_Hv(G1,Hw,N1w,N2w,k-1,solution+[v],permanent+[w]) or Algo_Hv(G2,Hv,N1,N2,k,solution,permanent+[v]) 
			else: #Case3: if Vertex Cover of Hv greater than 2
				G1=copy.deepcopy(G)
				G2=copy.deepcopy(G)
				G1.remove_node(v)
				# Branch on minimum solution containing v and minimum solution not containing v
				return branching(G1,k-1,solution+[v],permanent) or Algo_Hv(G2,Hv,N1,N2,k,solution,permanent+[v])


def main():
	G=get_graph.edge_list()	# read the input instance
	print_graph.input(G)	# construct input graph for display
	k=int(input("Enter k:"))
	G,k,solution=kernel.kernelization(G,k) # do kernelization
	print("Kernelization",k,solution)
	if not branching(G,k,solution,[]):	
		print ("No Solution")
	else:
		G.remove_nodes_from(sol)
		print_graph.output(G) # construct output graph for display
		#print_graph.show() # displays the graphs

if __name__== "__main__":
	main()
