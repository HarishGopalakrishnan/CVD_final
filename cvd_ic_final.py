import networkx as nx
import matplotlib.pyplot as plt
import copy
import math
import itertools

#user defined functions
import kernelization as kernel
import get_graph


#visualizatio of the input graph
def print_input_graph(G):
	plt.figure(1)
	number_of_connect_components=nx.number_connected_components(G)
	if number_of_connect_components==1:
		pos = nx.spring_layout(G)
		nx.draw(G,pos,with_labels=True)
	else:
		i=1
		for a in nx.connected_component_subgraphs(G):	
			pos = nx.spring_layout(a)
			plt.subplot(math.ceil(number_of_connect_components/2),2,i)
			i+=1
			nx.draw(a,pos,with_labels=True)		
	
#visualization of the output graph
def print_output_graph(G):
	plt.figure(4)
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
			
#visualization of the intermediate steps
def print_graph_inter(G,sol):
	color_map=[]	
	for nodes in G.nodes():
		if nodes in solution:
			color_map.append('green')
		else:
			color_map.append('red')		
	pos = nx.spring_layout(G)
	nx.draw(G,pos,node_color = color_map,with_labels=True)

#visualization of the bipartite graph
def print_graph_edge(G):
	plt.figure()
	pos = nx.spring_layout(G)
	nx.draw(G,pos,with_labels=True)
	labels = nx.get_edge_attributes(G,'weight')
	nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
	#plt.show()

def is_cluster_graph(G):
	"""
	Input: Graph G
	Output: True if G is a cluster graph else False
	Description: Check if there exists a P3
	"""
	for n1 in G:
		for n2 in G:
			for n3 in G:
				if not ((n1 == n2) or (n2 == n3) or (n1 == n3)):
					if ((G.has_edge(n1, n2) and G.has_edge(n2, n3) and not G.has_edge(n3, n1)) or (G.has_edge(n1, n2) and not G.has_edge(n2, n3) and  G.has_edge(n3, n1)) or (not G.has_edge(n1, n2) and G.has_edge(n2, n3) and G.has_edge(n3, n1))):
						return False
	return True


def diff(first, second):
	#find the difference between two list
        second = set(second)
        return [item for item in first if item not in second]

def intersect(a, b):
	#find the intersection between two list
	return list(set(a) & set(b))

def reduction_rule1(G_guess,out_graph,r_graph):
	"""
	Input: Guess graph G_guess,Out graph out_graph,Remaining graph  r_graph
	Output: Vertices in r_graph that are adjacent to more than one cluster in out_graph
	Description: Identify the vertices of r_graph that are adjacent to more than one cluster in out_graph
	"""
	del_rr1=[]
	for nodes in r_graph:
		count=0
		neighbour_nodes=G_guess.neighbors(nodes)
		for connected_component in nx.connected_component_subgraphs(out_graph):
			if intersect(neighbour_nodes,connected_component):
				count+=1
				if count==2: # if adjacent to more than one cluster in out_graph
					del_rr1.append(nodes)
					break	
	return del_rr1

def reduction_rule2(G_guess,out_graph,r_graph):
	"""
	Input: Guess graph G_guess,Out graph out_graph,Remaining graph  r_graph
	Output: Vertices in r_graph that are adjacent to some but not all vertices of a cluster in out_graph
	Description: Identify the vertices of r_graph that are adjacent to some but not all vertices of a cluster in out_graph
	"""
	del_rr2=[]
	for nodes in r_graph:
		neighbour_nodes=G_guess.neighbors(nodes)
		for connected_component in nx.connected_component_subgraphs(out_graph):
			if (len(intersect(neighbour_nodes,connected_component))>0)and(len(intersect(neighbour_nodes,connected_component)) != len(connected_component)): # adjacent to some but not all vertices of a cluster in out_graph
				del_rr2.append(nodes)
				break
	
	return del_rr2


def edge_between(G_guess,cc1,cc2):
	"""
	Input: Graph G, connected components cc1 and cc2
	Output: Count of edges between cc1 and cc2
	"""
	count=0	
	for n1 in cc1:
		for n2 in cc2:
			if G_guess.has_edge(n1,n2):
				count+=1
	return count
	
def edge_between_out_node(G_guess,cc1,n2):
	"""
	Input: Graph G, connected components cc1 and a node n2
	Output: Count of edges between cc1 and n2
	"""
	for n1 in cc1:
		if G_guess.has_edge(n1,n2):
			return True
	return False
	
	
def construct_G(G_guess,out_graph,r_graph):
	"""
	Classify each vertex in r_graph,
	Construct a auxillary bipartite graph,
	find the maximun weighted bipartite matching,
	Delete all vertices from the class that are not matched 
	"""
	out={}
	remaining={}
	remainingout={}
	max_solution=[]
	G_constructed=nx.Graph()
	i=0
	for connected_component2 in nx.connected_component_subgraphs(r_graph):
		i+=1
		j=0
		
		cc2_nodes=[]
		for nodes_2 in connected_component2.nodes():
			#print(out_graph.nodes(),nodes_2)
			if not edge_between_out_node(G_guess,out_graph.nodes(),nodes_2):
				cc2_nodes.append(nodes_2)
		remaining["remaining_"+str(i)]=(sorted(diff(connected_component2.nodes(),cc2_nodes)))
		if len(cc2_nodes)>0:
			G_constructed.add_edge("remainingout_"+str(i),"remaining_"+str(i),weight=len(cc2_nodes))
			remainingout["remainingout_"+str(i)]=(cc2_nodes)
		for connected_component1 in nx.connected_component_subgraphs(out_graph):
			j+=1
			number_edges=edge_between(G_guess,connected_component1,connected_component2)
			if number_edges>0:
				G_constructed.add_edge("out_"+str(j),"remaining_"+str(i),weight=(number_edges/len(connected_component1.nodes())))
			cc1_list=sorted(connected_component1.nodes())			
			out["out_"+str(j)]=(cc1_list)
			
	#print(out,remaining,remainingout)
	max_matching=nx.max_weight_matching(G_constructed, maxcardinality=False)
	#print(max_matching)
	max_matching_edges=[]
	for items in max_matching:
		edge1=(items,max_matching[items])
		edge2=(max_matching[items],items)
		max_matching_edges.append(edge1)
		max_matching_edges.append(edge2)
	#print(max_matching_edges)
	non_max_matching=(set(G_constructed.edges())-set(max_matching_edges))
	#print(non_max_matching)
	for items in non_max_matching:
		items=list(items)
		if items[1] in out or items[1] in remainingout:
			items[0],items[1]=items[1],items[0]
		if items[0] in out:
			for node1 in out[items[0]]:
				for node2 in remaining[items[1]]:
					if G_guess.has_edge(node1,node2):
						max_solution.append(node2) 
		if items[0] in remainingout:
			for node1 in remainingout[items[0]]:
				for node2 in remaining[items[1]]:
					if G_guess.has_edge(node1,node2):
						max_solution.append(node1)	
	#print_graph_edge(G_constructed)
	#plt.show()
	return list(set(max_solution))
	
	
	
def compression(G,k,solution):
	"""
	Input: Graph G, parameter k, k+1 sized solution
	Output: A k-sized solution if there exists one else return the k+1 sized solution
	Description: compress the given k+1 solution to obtain a k sized solution
	"""
	for i in range(len(solution)+1): # iterate on all subsets of the k+1 sized solution
		for guess in itertools.combinations(solution, i): 
			graph=G.subgraph(solution).copy()
			graph.remove_nodes_from(guess) # check if the guess is feasible
			if is_cluster_graph(graph):
				G_guess=G.subgraph(diff(G.nodes(),guess)).copy()
				out=G.subgraph(diff(solution,guess)).copy()	# construct the disjoint version of the problem		
				G_S=G.subgraph(diff(G.nodes(),solution)).copy()
				#disjoint version
				rr1=reduction_rule1(G_guess,out,G_S) # reduction rule1
				G_S.remove_nodes_from(rr1)
				G_guess.remove_nodes_from(rr1)
				#print("rr1:",rr1)				
				rr2=reduction_rule2(G_guess,out,G_S) # reduction rule 2
				G_S.remove_nodes_from(rr2)
				G_guess.remove_nodes_from(rr2)
				#print("rr2:",rr2)
				solution_d=construct_G(G_guess,out,G_S) # weighted bipartite matching
				if len(solution_d)+len(rr1)+len(rr2)+len(guess)<=k:	# check for a k- sized solution	
					# return the k sized solution
					return list(set().union(solution_d,rr1,rr2,list(guess))) 		
	# return the k+1 sized solution	
	return solution




G_input=get_graph.edge_list() # get the input instances
k=int(input("Enter K:"))
print_input_graph(G_input) # display the input graph

G,k,solution=kernel.kernelization(G_input,k) # do kernelization
print("Kernelization",k,solution)
G.remove_nodes_from(solution)
for nodes in itertools.combinations(G.nodes(),k+2): # to get a k+2 number of nodes
	break
nodes=list(nodes)
G_induced=G.subgraph(nodes).copy() # induce a graph with k+2 nodes

for solution in itertools.combinations(G.nodes(),k+1): # get a k+1 solution for the graph induced with k+2 nodes
	break
solution=list(solution)
G_nodes=G.nodes()
flag=True
i=0
subplot=math.ceil((len(G_nodes)-k)/3)
plt.figure(2)
while(True):
	i+=1
	plt.subplot(subplot,3,i)
	plt.title(solution)
	plt.suptitle("Intermediate steps",fontsize='16')
	print_graph_inter(G_induced,solution) # print the intermediate step and highlight the k+1 solution
	solution=compression(G_induced,k,solution) # call compression algorithm 
	solution=list(solution)
	if len(solution)>k: #Reduction Rule: if no k-sized solution from the compression algorithm then the instance is "NO INSTANCE"
		print("No Solution")
		flag=False
		break
	induced_node=G_induced.nodes()
	remaining_nodes=list(set(G_nodes)-set(induced_node))  # iteratively increase the graph size
	if remaining_nodes:
		solution.append(remaining_nodes[0])	# add vertex to get a k+1 solution
		induced_node.append(remaining_nodes[0]) # induce a graph
		G_induced=G.subgraph(induced_node).copy()
	
	else:
		break
if flag:
	print(solution)
	plt.figure("Final Graph")
	plt.title("Final Graph",fontsize='16')
	print_graph_inter(G,solution) # display the final compression solution
	plt.figure("Iterative Compression")
	G_ic=G.subgraph(diff(G.nodes(),solution)).copy()
	print_output_graph(G_ic) # display the cluster graph
plt.show()


