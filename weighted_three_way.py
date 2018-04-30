import networkx as nx
import matplotlib.pyplot as plt
import copy,math


G=nx.Graph()
p3s=[]
weight={}
#get graph from file
def get_graph_file():
	print("Enter File:",end='')
	file_name=input().strip("\n")
	fp=open(file_name,"r")
	for lines in fp:
		edge=lines.strip("\n").split(" ")
		G.add_edge(edge[0],edge[1])
	fp.close()

def get_weight_file():
	print("Weight File:",end='')
	file_name=input().strip("\n")
	fp=open(file_name,"r")
	for lines in fp:
		vertex_value=lines.strip("\n").split(" ")
		weight[vertex_value[0]]=int(vertex_value[1])			
	fp.close()
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

def three_way_branching(p3s0,k,solution):
	p3s1=copy.deepcopy(p3s0)
	p3s2=copy.deepcopy(p3s0)
	p3s3=copy.deepcopy(p3s0)
	
	if k<0:
		return False
	if len(p3s0)==0:
		print (solution)
		G.remove_nodes_from(solution)
		return True
	
	p3=p3s0[0]
	p3s1 = delete_vertex(p3s1,p3[0])
	p3s2 = delete_vertex(p3s2,p3[1])
	p3s3 = delete_vertex(p3s3,p3[2])
	return three_way_branching(p3s1,k-weight[p3[0]],solution+[p3[0]]) or three_way_branching(p3s2,k-weight[p3[1]],solution+[p3[1]]) or three_way_branching(p3s3,k-weight[p3[2]],solution+[p3[2]])

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

		
def print_g(G):
	nx.draw(G)
	plt.show()

def main():	
	get_graph_file()
	get_weight_file()
	#print(weight)
	get_p3(G)
	#print(p3s)
	print_input_graph(G)
	k=int(input("k:"))
	solution=list()
	if not three_way_branching(p3s,k,solution):
		print ("No Solution")
	print_output_graph(G)

if __name__== "__main__":
	main()
