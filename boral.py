import networkx as nx
import matplotlib.pyplot as plt
import copy
import math
flag=True

#get graph from file
def get_graph_file():
	G=nx.Graph()
	print("Enter file:")
	file_name=input().strip("\n")
	#file_name="g4"
	fp=open(file_name,"r")
	for lines in fp:
		edge=lines.strip("\n").split(" ")
		G.add_edge(edge[0],edge[1])
	fp.close()
	return G

def get_p3(G):
	p3s=[]
	for n1 in G:
		for n2 in G:
			for n3 in G:
				if not ((n1 == n2) or (n2 == n3) or (n1 == n3)):
					if ((G.has_edge(n1, n2) and G.has_edge(n2, n3) and not G.has_edge(n3, n1)) or (G.has_edge(n1, n2) and not G.has_edge(n2, n3) and  G.has_edge(n3, n1)) or (not G.has_edge(n1, n2) and G.has_edge(n2, n3) and G.has_edge(n3, n1))):
						p3=[n1,n2,n3]
						if sorted(p3) not in p3s:
							p3s.append(sorted(p3))	
	return p3s		

def get_universe(p3s):
	universe=set()
	for collection in p3s:
		for element in collection:
			universe.add(element)
	return universe		

def p3s_highest_element(S,p3_s):
	dict_element_count={}
	for vertex in S:
		dict_element_count[vertex]=0	
	for p3 in p3_s:
		for element in p3:
			dict_element_count[element]+=1
	max_element = max(dict_element_count, key=dict_element_count.get)
	return dict_element_count[max_element],max_element
	
def kernelization_hdv(universe,p3s,k,solution):
	if k>0 and len(p3s)>0 :
		#p3ss=copy.deepcopy(p3s)
		count,element=p3s_highest_element(universe,p3s)
		if (count>=(((k+1)*(k+2))/2)):
			k-=1
			solution.append(element)
			universe.remove(element)
			'''for p3 in p3ss:
				if element in p3:
					p3s.remove(p3)'''
			p3s=delete_vertex(p3s,element)
			return kernelization_hdv(universe,p3s,k,solution)
	return universe,p3s,k,solution


def kernelization_wre(p3s,k):
	WRE=[p3s[0]]
	
	for p3_1 in p3s:
		count = 0
		for p3_2 in WRE:
			if len(set(p3_1).intersection(p3_2))<2:
				count+=1/2
		if count==len(WRE):
			WRE.append(p3_1) 
	return WRE

def print_input_graph(G):
	plt.figure(1)
	number_of_connect_components=nx.number_connected_components(G)
	if number_of_connect_components==1:
		pos = nx.random_layout(G)
		nx.draw(G,pos,with_labels=True)
	else:
		i=1
		for a in nx.connected_component_subgraphs(G):	
			pos = nx.random_layout(a)
			plt.subplot(math.ceil(number_of_connect_components/2),2,i)
			i+=1
			nx.draw(a,pos,with_labels=True)		
def print_graph(G):
	plt.figure()
	pos = nx.spring_layout(G)
	nx.draw(G,pos,with_labels=True)

def print_output_graph(G):
	plt.figure(2)
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

def kernelization(G,k):
	solutionI=[]
	p3s=get_p3(G)
	S=get_universe(p3s)
	#print (len(S))
	S,p3s,k,solution=kernelization_hdv(S,p3s,k,[])
	#print(len(S),k,solution)
	G.remove_nodes_from(solution)
	if k>0 and len(p3s)>0:
		#S=get_universe(p3s)
		W=kernelization_wre(p3s,k)
		if len(W)>k*k:
			print ("No Solution")
			k=-1
		else:
			V_W=get_universe(W)
			I=[item for item in S if item not in V_W]
			G_I=nx.subgraph(G,I)
			#print (G_I.number_of_edges(),I)
			if len(I)>=len(W)*3 and G_I.number_of_edges()==0:
				H=[]
				for element in W:
					H.append([element[0],element[1]])
					H.append([element[0],element[2]])
					H.append([element[1],element[2]])
				#print (I,H)
				G_HI=nx.Graph()
				for i in I:
					for h in H:
						a=copy.deepcopy(h)
						a.append(i)
						if a in p3s:
							str1 = ''.join(h)
							G_HI.add_edge(i,str1) 
				for key in nx.bipartite.maximum_matching(G_HI):
					if key in I:
						solutionI.append(element)
	
				G.remove_nodes_from(solutionI)
	return G,k,solution

def delete_vertex(p_3s,v):
	p3ss=copy.deepcopy(p_3s)
	for p_3 in p3ss:
		if v in p_3:
			p_3s.remove(p_3)
	return p_3s


def is_cluster_graph(Graph):
	for connected_component in nx.connected_component_subgraphs(Graph):
		if not connected_component_isclique(connected_component):
			return False
	return True

def connected_component_isclique(Graph):
	nodes=Graph.nodes()
	if len(nodes)==1:
		return True
	for i in range(0,len(nodes)):
		if not set(Graph.neighbors(nodes[i]))==(set(nodes)-set([nodes[i]])):
			return False
	return True


def connected_component_minus_w_isclustergraph(Graph):
	nodes=Graph.nodes()
	for node in nodes:
		nodes_minus_node=list(set(nodes)-set([node]))
		#print(nodes_minus_node,node)
		Graph_minus_node=Graph.subgraph(nodes_minus_node).copy()
		#print_graph(Graph_minus_node)
		#plt.show()
		if is_cluster_graph(Graph_minus_node):
			return node
	return

def construct_Hv(Graph,v):
	N1=Graph.neighbors(v)
	N2=[]
	for nodes in N1:
		N2+=Graph.neighbors(nodes)
	#print("Neighbors",Graph.nodes(),v,N1,N2)
	N2=list(set(N2)-set(N1))
	if v in N2:
		N2.remove(v)
	#print("Neighbors",v,N1,N2)
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
	for nodes in Hv.nodes():					
		neighbor_node=Hv.neighbors(nodes)
		#print(nodes,neighbor_node)
		if len(neighbor_node)>=3:
			#print("rule1",nodes)
			G1=copy.deepcopy(G)
			G1.remove_node(nodes)
			G2=copy.deepcopy(G)
			G2.remove_nodes_from(neighbor_node)
			return branching(G1,k-1,solution+[nodes],permanent) or branching(G2,k-len(neighbor_node),solution+neighbor_node,permanent)
	return False

def Hv_rule2(G,Hv,N1,k,solution,permanent):
	for nodes in N1:
		neighbor_node=Hv.neighbors(nodes)
		if len(neighbor_node)==1:
			#print("rule2",neighbor_node)
			G1=copy.deepcopy(G)
			G1.remove_nodes_from(neighbor_node)
			return branching(G1,k-1,solution+neighbor_node,permanent)
	return False

def Hv_rule3(G,Hv,N1,k,solution,permanent):
	for node1 in N1:
		for node2 in N1:
			if (not node1==node2) and Hv.has_edge(node1,node2):
				#print("rule3")
				G1=copy.deepcopy(G)
				G1.remove_node(node1)
				G2=copy.deepcopy(G)
				G2.remove_node(node2)
				return branching(G1,k-1,solution+[node1],permanent) or branching(G2,k-1,solution+[node2],permanent)
	return False

def Hv_rule4(G,Hv,N2,k,solution,permanent):
	try:
		cycle=nx.find_cycle(Hv,source=None,orientation='ignore')
		if len(cycle)%2==0:
			#print("rule4")
			cycle_nodes=set()
			for edge in cycle:
				cycle_nodes.add(edge[0])
				cycle_nodes.add(edge[1])
			N2_cycle=list(cycle_nodes & set(N2))
			#print(N2_cycle)
			G1=copy.deepcopy(G)
			G1.remove_nodes_from(N2_cycle)
			return branching(G1,k-len(N2_cycle),solution+N2_cycle,permanent)
		else:
			return False
	except:
		return False

def Hv_rule5(G,Hv,N1,N2,k,solution,permanent):
	longest_path=[]
	for node1 in Hv.nodes():
		for node2 in Hv.nodes():
			if not node1==node2:
				for path in nx.all_simple_paths(Hv, source=node1, target=node2):
					if len(path)>len(longest_path):
						longest_path=path
	path_intersect_N1=list(set(longest_path)&set(N1))
	path_intersect_N2=list(set(longest_path)&set(N2))
	#print("rule5")
	G1=copy.deepcopy(G)
	G1.remove_nodes_from(path_intersect_N1)
	G2=copy.deepcopy(G)
	G2.remove_nodes_from(path_intersect_N2)
	return branching(G1,k-len(path_intersect_N1),solution+path_intersect_N1,permanent) or branching(G2,k-len(path_intersect_N2),solution+path_intersect_N2,permanent) 

def s_skein(Hv,N1,N2):
	for y in N1:
		y_neighbor=Hv.neighbors(y)
		if len(y_neighbor)==2:
			y_neighbor_in_N2=list(set(y_neighbor)-set(N1))
			if len(y_neighbor_in_N2)==2:
				return True
	return False

def is_vertexcover(G,vc):
	G.remove_nodes_from(vc)
	if G.edges():
		return False
	return True

def vc_1(Hv):
	for nodes in Hv.nodes():
		Hv1=copy.deepcopy(Hv)
		if is_vertexcover(Hv1,[nodes]):
			return True
		del Hv1
	return False

def vc_2(Hv):
	for node1 in Hv.nodes():
		for node2 in Hv.nodes():
			if not node1==node2:
				Hv1=copy.deepcopy(Hv)
				if is_vertexcover(Hv1,[node1,node2]):
					return [node1,node2]
				del Hv1
	return [-1]

def Algo_Hv(G,Hv,N1,N2,k,solution,permanent):
	if Hv_rule1(G,Hv,k,solution,permanent):
		return True
	else:
		if Hv_rule2(G,Hv,N1,k,solution,permanent):
			return True
		else:
			if Hv_rule3(G,Hv,N1,k,solution,permanent):
				return True
			else:
				if Hv_rule4(G,Hv,N2,k,solution,permanent):
					return True
				else:
					return Hv_rule5(G,Hv,N1,N2,k,solution,permanent)

def cc_w_notclique(G,w):
	for connected_component in nx.connected_component_subgraphs(G):
		if w in connected_component:
			return connected_component_isclique(connected_component)
					
def branching(G_branch,k,solution,permanent):
	#print_graph(G_branch)
	#plt.show()
	G=copy.deepcopy(G_branch)
	count=0
	for connected_component in nx.connected_component_subgraphs(G_branch):
		count+=1	
		if connected_component_isclique(connected_component):
			count-=1
			G.remove_nodes_from(connected_component.nodes())
		else: 
			w=connected_component_minus_w_isclustergraph(connected_component)
			if not w==None:
				#print("w",w)
				count-=1
				solution+=[w]
				k-=1
				G.remove_nodes_from(connected_component.nodes())
	if count==0 and k>=0:
		#print("CVD set:",solution)
		global sol
		sol=solution
		return True
	if k<=0:
		return False
	else:
		v=(list(set(G.nodes())-set(permanent)))[0]
		#print("v",v)
		Hv,N1,N2=construct_Hv(G,v)
		#print(N1,N2)
		#print_graph(Hv)
		#plt.show()
		if (s_skein(Hv,N1,N2)):
			G1=copy.deepcopy(G)
			return Algo_Hv(G1,Hv,N1,N2,k,solution,permanent+[v])
		else:
			if vc_1(Hv):
				G1=copy.deepcopy(G)
				return Algo_Hv(G1,Hv,N1,N2,k,solution,permanent+[v])
			vc_2_Hv=vc_2(Hv)
			if len(vc_2_Hv)==2:
				G1=copy.deepcopy(G)
				G2=copy.deepcopy(G)
				G1.remove_node(v)		
				if cc_w_notclique(G1,vc_2_Hv[0]):
					w=vc_2_Hv[0]
				else:
					w=vc_2_Hv[1]
				Hw,N1w,N2w=construct_Hv(G1,w)
				#print(w,Hw,N1w,N2w)
				return Algo_Hv(G1,Hw,N1w,N2w,k-1,solution+[v],permanent+[w]) or Algo_Hv(G2,Hv,N1,N2,k,solution,permanent+[v]) 
			else:
				G1=copy.deepcopy(G)
				G2=copy.deepcopy(G)
				G1.remove_node(v)
				return branching(G1,k-1,solution+[v],permanent) or Algo_Hv(G2,Hv,N1,N2,k,solution,permanent+[v])

									 
G_input=get_graph_file()
print_input_graph(G_input)
k=int(input("k:"))
#print(k)
#k=4
G_kernel,k,solution=kernelization(G_input,k)
print("Main Kernalization",k,solution)
if branching(G_kernel,k,solution,[])==False:
	print("No Solution")
else:
	print(sol)
	G_input.remove_nodes_from(sol)
	print_output_graph(G_input)
plt.show()
