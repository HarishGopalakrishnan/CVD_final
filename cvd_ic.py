import networkx as nx
import matplotlib.pyplot as plt
import copy
import math
import itertools

#get graph from file
def get_graph_file():
	G=nx.Graph()
	print("Enter File:",end='')
	file_name=input().strip("\n")
	fp=open(file_name,"r")
	for lines in fp:
		edge=lines.strip("\n").split(" ")
		G.add_edge(edge[0],edge[1])
	fp.close()
	return G

def print_input_graph(G,k):
	plt.figure("Input Graph")
	plt.title("Input Graph G, k="+str(k),fontsize='16')
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
	#plt.show()	
	

def print_output_graph(G):
	#plt.figure()
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
	#plt.show()

def print_graph(G,sol):
	#print(sol)
	color_map=[]	
	for nodes in G.nodes():
		if nodes in solution:
			color_map.append('green')
		else:
			color_map.append('red')		
	pos = nx.spring_layout(G)
	nx.draw(G,pos,node_color = color_map,with_labels=True)

def print_graph_edge(G):
	plt.figure()
	pos = nx.spring_layout(G)
	nx.draw(G,pos,with_labels=True)
	labels = nx.get_edge_attributes(G,'weight')
	nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
	#plt.show()

def is_cluster_graph(G):
	for n1 in G:
		for n2 in G:
			for n3 in G:
				if not ((n1 == n2) or (n2 == n3) or (n1 == n3)):
					if ((G.has_edge(n1, n2) and G.has_edge(n2, n3) and not G.has_edge(n3, n1)) or (G.has_edge(n1, n2) and not G.has_edge(n2, n3) and  G.has_edge(n3, n1)) or (not G.has_edge(n1, n2) and G.has_edge(n2, n3) and G.has_edge(n3, n1))):
						return False
	return True


def diff(first, second):
        second = set(second)
        return [item for item in first if item not in second]

def intersect(a, b):
    return list(set(a) & set(b))

def reduction_rule1(G_guess,out_graph,r_graph):
	#print(r_graph.nodes())	
	del_rr1=[]
	for nodes in r_graph:
		count=0
		neighbour_nodes=G_guess.neighbors(nodes)
		for connected_component in nx.connected_component_subgraphs(out_graph):
			if intersect(neighbour_nodes,connected_component):
				count+=1
				if count==2:
					del_rr1.append(nodes)
					break
	#print(del_rr1)	
	return del_rr1

def reduction_rule2(G_guess,out_graph,r_graph):
	del_rr2=[]
	for nodes in r_graph:
		neighbour_nodes=G_guess.neighbors(nodes)
		for connected_component in nx.connected_component_subgraphs(out_graph):
			if (len(intersect(neighbour_nodes,connected_component))>0)and(len(intersect(neighbour_nodes,connected_component)) != len(connected_component)):
				del_rr2.append(nodes)
				break
	#print(del_rr2)
	return del_rr2


def edge_between(G_guess,cc1,cc2):
	count=0	
	for n1 in cc1:
		for n2 in cc2:
			if G_guess.has_edge(n1,n2):
				count+=1
	return count
def edge_between_out_node(G_guess,cc1,n2):
	for n1 in cc1:
		if G_guess.has_edge(n1,n2):
			return True
	return False
def construct_G(G_guess,out_graph,r_graph):
	out={}
	remaining={}
	remainingout={}
	max_solution=[]
	G_constructed=nx.Graph()
	#print(nx.number_connected_components(out_graph))
	#print(nx.number_connected_components(r_graph))
	#print(G_guess.edges())	
	i=0
	for connected_component2 in nx.connected_component_subgraphs(r_graph):
		i+=1
		j=0
		#remaining.append(sorted(connected_component2.nodes()))
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
			#if cc1_list not in out:		
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
	#print(solution)
	for i in range(len(solution)+1):
		for guess in itertools.combinations(solution, i):
			graph=G.subgraph(solution).copy()
			#print("1",graph.edges())
			graph.remove_nodes_from(guess)
			#print("2",graph.edges())
			if is_cluster_graph(graph):
				G_guess=G.subgraph(diff(G.nodes(),guess)).copy()
				out=G.subgraph(diff(solution,guess)).copy()
				#out=graph.copy()				
				G_S=G.subgraph(diff(G.nodes(),solution)).copy()
				#disjoint version
				#print("guess:",guess)
				rr1=reduction_rule1(G_guess,out,G_S)
				G_S.remove_nodes_from(rr1)
				G_guess.remove_nodes_from(rr1)
				#print("rr1:",rr1)				
				rr2=reduction_rule2(G_guess,out,G_S)
				G_S.remove_nodes_from(rr2)
				G_guess.remove_nodes_from(rr2)
				#print("rr2:",rr2)
				solution_d=construct_G(G_guess,out,G_S)
				if len(solution_d)+len(rr1)+len(rr2)+len(guess)<=k:				
					return list(set().union(solution_d,rr1,rr2,list(guess)))				
	return solution

G_input=get_graph_file()
k=int(input("Enter K:"))
print_input_graph(G_input,k)
#plt.show()
#print(G_input.nodes())
#solution=['1','2','5','6','7','17']
#print(compression(G_input,k,solution))
for nodes in itertools.combinations(G_input.nodes(),k+2):
	break
nodes=list(nodes)
#print(nodes)
G_induced=G_input.subgraph(nodes).copy()
for solution in itertools.combinations(G_input.nodes(),k+1):
	break
solution=list(solution)
#print(solution)
G_nodes=G_input.nodes()
flag=True
i=0
subplot=math.ceil((len(G_nodes)-k)/3)
#print(subplot)
plt.figure(2)
while(True):
	i+=1
	plt.subplot(subplot,3,i)
	plt.title(solution)
	plt.suptitle("Intermediate steps",fontsize='16')
	print_graph(G_induced,solution)
	solution=compression(G_induced,k,solution)
	solution=list(solution)
	if len(solution)>k:
		print("No Solution")
		flag=False
		break
	induced_node=G_induced.nodes()
	remaining_nodes=list(set(G_nodes)-set(induced_node))
	if remaining_nodes:
		solution.append(remaining_nodes[0])
		induced_node.append(remaining_nodes[0])
		G_induced=G_input.subgraph(induced_node).copy()
	
	else:
		break
if flag:
	print(solution)
	plt.figure("Final Graph")
	plt.title("Final Graph",fontsize='16')
	print_graph(G_input,solution)
	plt.figure("Iterative Compression")
	G_ic=G_input.subgraph(diff(G_input.nodes(),solution)).copy()
	print_output_graph(G_ic)
plt.show()


