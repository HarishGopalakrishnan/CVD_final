import networkx as nx
import matplotlib.pyplot as plt
import copy,math
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

def get_weight_file():
	print("Enter Weight:",end='')
	file_name=input().strip("\n")
	fp=open(file_name,"r")
	for lines in fp:
		vertex_value=lines.strip("\n").split(" ")
		weight[vertex_value[0]]=int(vertex_value[1])			
	fp.close()

#prints graph
def print_g(G):
	nx.draw(G)
	plt.show()


#2^k vertex cover
def vertex_cover(G_t,G,k,solution):
	if k<0:
		return False
	if G.number_of_edges()==0:
		print (solution)
		global sol
		sol=solution
		return True
	edges=G.edges()
	edge=edges[0]
	G0=copy.deepcopy(G)
	G0.remove_node(edge[0])
	G1=copy.deepcopy(G)
	G1.remove_node(edge[1])
	return vertex_cover(G_temp,G0,k-weight[edge[0]],solution+[edge[0]]) or vertex_cover(G_temp,G1,k-weight[edge[1]],solution+[edge[1]])
	

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
				solution.add(neighbor)
				k-=weight[neighbor]
	
	nodes=set(G.nodes())
	solution=list(solution)+list(nodes-neighbors)	
	#k-=len(solution)
	for vertex_solution in solution:
		k-=weight[vertex_solution]
	#print(neighbors,solution)
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



G=get_graph_file()
weight={}
get_weight_file()
print_input_graph(G)

k=int(input("Enter K:"))
d=int(input("Enter d:"))

#iteratively check for CVD with given G,k,d
for permanent in itertools.combinations(G.nodes(), d):
	k1=k
	G_temp=copy.deepcopy(G)
	G_vc,k1,solution=reduction_to_vc(G_temp,k1,permanent)
	G_t=copy.deepcopy(G_vc)
	if k1>0:
		if vertex_cover(G_t,G_vc,k1,solution):
			print ("Permanent",permanent)
			print("Solution",sol)
			G.remove_nodes_from(sol)
			print_output_graph(G)
			break


