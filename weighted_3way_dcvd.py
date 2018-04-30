import networkx as nx
import matplotlib.pyplot as plt
import copy


G=nx.Graph()
p3s=[]
weight={}
#get graph from file
def get_graph_file():
	print("Enter File:")
	file_name=input().strip("\n")
	fp=open(file_name,"r")
	for lines in fp:
		edge=lines.strip("\n").split(" ")
		G.add_edge(edge[0],edge[1])
	fp.close()

def get_weight_file():
	print("Weight File:")
	file_name=input().strip("\n")
	fp=open(file_name,"r")
	for lines in fp:
		vertex_value=lines.strip("\n").split(" ")
		weight[vertex_value[0]]=int(vertex_value[1])			
	fp.close()

def print_graph(G):
	plt.figure()
	pos = nx.spring_layout(G)
	nx.draw(G,pos,with_labels=True)
def get_p3(G):
	for n1 in G:
		for n2 in G:
			for n3 in G:
				if not ((n1 == n2) or (n2 == n3) or (n1 == n3)):
					if ((G.has_edge(n1, n2) and G.has_edge(n2, n3) and not G.has_edge(n3, n1)) or (G.has_edge(n1, n2) and not G.has_edge(n2, n3) and  G.has_edge(n3, n1)) or (not G.has_edge(n1, n2) and G.has_edge(n2, n3) and G.has_edge(n3, n1))):
						p3=[n1,n2,n3]
						if sorted(p3) not in p3s:
							p3s.append(sorted(p3))			


def delete_vertex(p_3s,v):
	p3ss=copy.deepcopy(p_3s)
	for p_3 in p3ss:
		if v in p_3:
			p_3s.remove(p_3)
	return p_3s

def d_cvd(G,d,k,solution):
	number_cliques=nx.number_connected_components(G)
	if number_cliques<d:
		return False
	if number_cliques==d:
		return True
	else:
		cliques={}
		for connected_component in nx.connected_component_subgraphs(G):
			cc_nodes=connected_component.nodes()
			weight_clique=0
			for node in cc_nodes:
				weight_clique+=weight[node]
			if weight_clique not in cliques:
				cliques[weight_clique]=[cc_nodes]
			else:
				cliques[weight_clique].append(cc_nodes)
		#print(cliques)
		while (not number_cliques==d) and k>0:
			#print(cliques)
			key=sorted(cliques)[0]
			del_clique=cliques[key].pop(0)
			solution+=del_clique
			k-=key
			if cliques[key]==[]:
				del cliques[key]
			number_cliques-=1
		if k>=0 and number_cliques==d:
			return True
		return False

def three_way_branching(p3s0,k,d,solution):
	p3s1=copy.deepcopy(p3s0)
	p3s2=copy.deepcopy(p3s0)
	p3s3=copy.deepcopy(p3s0)
	
	if k<0:
		return False
	if len(p3s0)==0:
		G1=copy.deepcopy(G)
		G1.remove_nodes_from(solution)		
		if d_cvd(G1,d,k,solution):
			print ("Solution:",solution)
			G1.remove_nodes_from(solution)
			print_graph(G1)
			return True
		return False
	
	p3=p3s0[0]
	p3s1 = delete_vertex(p3s1,p3[0])
	p3s2 = delete_vertex(p3s2,p3[1])
	p3s3 = delete_vertex(p3s3,p3[2])
	return three_way_branching(p3s1,k-weight[p3[0]],d,solution+[p3[0]]) or three_way_branching(p3s2,k-weight[p3[1]],d,solution+[p3[1]]) or three_way_branching(p3s3,k-weight[p3[2]],d,solution+[p3[2]])


		
def print_g(G):
	nx.draw(G)
	plt.show()

	
get_graph_file()
get_weight_file()
#print(weight)
get_p3(G)
#print(p3s)
k=int(input("k:"))
d=int(input("d:"))
solution=list()
if not three_way_branching(p3s,k,d,solution):
	print ("No Solution")
plt.show()
