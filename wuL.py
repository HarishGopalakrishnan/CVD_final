import networkx as nx
import matplotlib.pyplot as plt
import copy
import itertools
import random 
import sys
infinity=9999
#get graph from file
def get_graph_file():
	G=nx.Graph()
	#print("Enter file name:")
	#file_name=input().strip("\n")
	file_name=sys.argv[3]
	fp=open(file_name,"r")
	for lines in fp:
		edge=lines.strip("\n").split(" ")
		G.add_edge(edge[0],edge[1])
	fp.close()
	return G

#prints graph
def print_graph(G):
	plt.figure()
	pos = nx.spring_layout(G)
	nx.draw(G,pos,with_labels=True)



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

def union(a,b):
	return list(set(a)|set(b))

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


def kernelization(G,k):
	solutionI=[]
	p3s=get_p3(G)
	S=get_universe(p3s)
	S,p3s,k,solution=kernelization_hdv(S,p3s,k,[])
	G.remove_nodes_from(solution)
	if k>0 and len(p3s)>0:
		#S=get_universe(p3s)
		W=kernelization_wre(p3s,k)
		if len(W)>k*k:
			print ("No Solution")
			sys.exit()
			k=-1
		else:
			V_W=get_universe(W)
			I=[item for item in S if item not in V_W]
			G_I=nx.subgraph(G,I)
			if len(I)>=len(W)*3 and G_I.number_of_edges()==0:
				H=[]
				for element in W:
					H.append([element[0],element[1]])
					H.append([element[0],element[2]])
					H.append([element[1],element[2]])
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




#2^k vertex cover
def vertex_cover(G_t,G,k,solution):
	for i in range(k+1):
		#print(i)
		for node in itertools.combinations(G.nodes(), i):
			G0=copy.deepcopy(G)
			G0.remove_nodes_from(union(list(node),list(solution)))
			#print(G.nodes(),G0.nodes())
			if G0.number_of_edges()==0:
				return True,list(node)
	return False,[]
				
				
def vertex_cover1(G_temp,G,k,solution):
	if k<0:
		return False,[]
		
	if G.number_of_edges()==0:
		print (solution)
		return True,solution
	edges=G.edges()
	edge=edges[0]
	G0=copy.deepcopy(G)
	G0.remove_node(edge[0])
	G1=copy.deepcopy(G)
	G1.remove_node(edge[1])
	return vertex_cover(G_temp,G0,k-1,solution+[edge[0]]) or vertex_cover(G_temp,G1,k-1,solution+[edge[1]])
	

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


def cvdp(G,B,d,k):
	flag=False
	#print_graph(G)
	#plt.show()
	#check for CVD with given G,k,d
	G_temp=copy.deepcopy(G)
	permanent=list(set(B)&set(G_temp.nodes()))
	G_vc,k,solution=reduction_to_vc(G_temp,k,permanent)
	G_t=copy.deepcopy(G_vc)	
	if k>=0:
		vc_result=vertex_cover(G_t,G_vc,k,solution)
		if vc_result[0]:
			print("Solution",solution,vc_result[1])
			return solution+vc_result[1]
	return

def connected_component_isclique(Graph):
	nodes=Graph.nodes()
	if len(nodes)==1:
		return True
	for i in range(0,len(nodes)):
		if not set(Graph.neighbors(nodes[i]))==(set(nodes)-set([nodes[i]])):
			return False
	return True

def update_L(in_L1,in_L2):
	L1=copy.deepcopy(in_L1)
	L2=copy.deepcopy(in_L2)
	len_L1=len(L1)
	len_L2=len(L2)
	for i in range(len_L1):
		L2.append(infinity)
	for i in range(len_L2):
		L1.append(infinity)
	len_L1=len(L1)
	len_L2=len(L2)
	res_L=[0 for i in range(len_L1)]
	for i in range(len_L1):
		minimum=infinity
		for j in range(0,i+1):
			val=L1[j]+L2[i-j]	
			if val<minimum:
				minimum=val
		res_L[i]=minimum
	while infinity in res_L:
            res_L.remove(infinity)	
	res_L.append(infinity)
	if len(res_L)==1:
		res_L=[0]
	print ("result",in_L1,in_L2,res_L)
	return res_L

def reductionRule2(G,U0,U1,U2,B,L):
	G1=G.subgraph(list(set(U1)|set(U2))).copy()
	print("InRR2",G1.nodes())
	cliques=[]
	for connected_component in nx.connected_component_subgraphs(G1):	
		if connected_component_isclique(connected_component):
			cc_nodes=connected_component.nodes()
			U0.append(cc_nodes)
			#B=list(set(B)-set(cc_nodes))
			cliques.append(len(cc_nodes))
			U1=list(set(U1)-set(cc_nodes))
			U2=list(set(U2)-set(cc_nodes))
	for clique in cliques:
		"""Alternative list property:P3"""
		L=update_L(L,[clique,0,infinity])
	del G1
	return U0,U1,U2,B,L

def is_cluster_graph(Graph):
	cliques=[]
	for connected_component in nx.connected_component_subgraphs(Graph):
		cliques.append(connected_component)
		if not connected_component_isclique(connected_component):
			return False,[]
		
	return True,cliques

def connected_component_isclique(Graph):
	nodes=Graph.nodes()
	if len(nodes)==1:
		return True
	for i in range(0,len(nodes)):
		if not set(Graph.neighbors(nodes[i]))==(set(nodes)-set([nodes[i]])):
			return False
	return True


def connected_component_has_critical_vertex(Graph):
	nodes=Graph.nodes()
	for node in nodes:
		nodes_minus_node=list(set(nodes)-set([node]))
		Graph_minus_node=Graph.subgraph(nodes_minus_node).copy()
		result=is_cluster_graph(Graph_minus_node)
		if result[0]:
			return True,result[1],node
	return False,[],-1


def reductionRule3(G,U0,U1,U2,B,L,X):
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
				#critical vertex  itself is a clique
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
			#print("Alternating List",L_before,L_criticalVertex,L)
			cc_nodes=connected_component.nodes()
			U0.append(cc_nodes)
			#B=list(set(B)-set(cc_nodes))
			U1=list(set(U1)-set(cc_nodes))
			U2=list(set(U2)-set(cc_nodes))
			#X.append(result[2])
	return U0,U1,U2,B,L,X

def reductionRule4(G,U0,U1,U2,B,k,d,L,X):
	print("In_RR4",U0,U1,U2,B,k,d,L,X)
	if not len(U1) == 0 and not len(U2) == 0:
		for node1 in U1:
			for node2 in U2:
				if G.has_edge(node1,node2):
					return True,U0,U1,U2,L
		G_U1=G.subgraph(U1).copy()
		print("..........RR4............",U0,U1,U2,B,k,d,L,X)
		kprime=cvdp(G_U1,B,d,k)
		if kprime==None:
			print("No solution")
			return False,U0,U1,U2,L
		elif len(kprime)>0:
			"""Search(G,U0,[],U2,[],d,k-cvdp(G,B,d,k),d,L,X)"""
			search(G,U0,[],U2,[],k-len(kprime),d,L,X)
			return False,U0,U1,U2,L
	return True,U0,U1,U2,L



def reductionRule5(B,k,L):
	minL=min(L)
	if min(L)>0:
		k-=minL
		for val in range(len(L)-1):	
			L[val]=L[val]-minL
	return k,L
"""
def reductionRule5(B,k,L):
	lPrime=[]
	len_B=len(B)
	if len(L)>len_B:
		if min(L)>0:
			lPrime=L[len_B:]
			#lPrime=L
			min_lPrime=min(lPrime)
			lPrime=[value-min_lPrime for value in lPrime]
			k-=min_lPrime
		else:
			lPrime=L[len_B:]
	else:
		lPrime=[0]
		#lPrime=L
	return k,lPrime
	
	
	#comment
	min_di=infinity
	len_B=len(B)
	for i in range(len_B):
		lPrime.append(infinity)
	for i in range(len_B,len(L)):
		lPrime.append(L[i])
		if lPrime[i]<min_di:
			min_di=lPrime[i]
	delta=[]
	for i in range(len_B,len(lPrime)):
		if lPrime[i]==infinity:
			delta.append(infinity)
		else:
			delta.append(lPrime[i]-min_di)
	print("delta",delta)
	min_Lprime=min(L)
	if min_Lprime>0:
		k-=min_Lprime
		#update
		L=[value-min_Lprime for value in L if not value ==infinity]
		L.append(infinity)
	if delta==[]:
		delta.append(0)
	return k, L
	#comment
	Lprime=L[d:]
	min_Lprime=min(L)
	if min_Lprime>0:
		k-=min_Lprime
		#update
		L=[value-min_Lprime for value in L if not value ==infinity]
		L.append(infinity)
	return k,L
	"""	
def reduction_rule(G,U0,U1,U2,B,k,d,L,X):
	U0,U1,U2,B,L=reductionRule2(G,U0,U1,U2,B,L)
	print("RR2",U0,U1,U2,B,k,d,L,X)
	U0,U1,U2,B,L,X=reductionRule3(G,U0,U1,U2,B,L,X)
	print("RR3",U0,U1,U2,B,k,d,L,sorted(X))
	"""update search return type"""
	flag,U0,U1,U2,L=reductionRule4(G,U0,U1,U2,B,k,d,L,X)
	if flag:
		print("RR4",U0,U1,U2,B,k,d,L,X)
		k,L=reductionRule5(B,k,L)
		print("RR5",U0,U1,U2,B,k,d,L,sorted(X))
		return True,U0,U1,U2,B,k,d,L,X
	return False,U0,U1,U2,B,k,d,L,X

def search(G,U0,U1,U2,B,k,d,L,X):
	print("SeR",U0,U1,U2,B,k,d,L,sorted(X))
	flag,U0,U1,U2,B,k,d,L,X=reduction_rule(G,U0,U1,U2,B,k,d,L,X)
	
	if not flag:
		return False 
	#termination conditions
	if k<0 or d<0:
		print("T0")
		return False
	#terminal case 1
	bprime=len(B)-len(set(U1)&set(B))
	print("bprime",bprime)
	if k==0:
		if len(L)>d+bprime:
			if (not list(set(U1)|set(U2))) and L[d+bprime]==0:
				print("Yes T1")
				print(X)
				sys.exit()
		print("T1")
		return False 
		#sys.exit()	
	#terminal case 2
	if d==0:
		G_U1=G.subgraph(U1).copy()
		kprime=cvdp(G_U1,B,d,k)
		print(kprime)
		if kprime==None:
			print("...............",kprime,U2,L)
			print("T2")	
			return False
		else:	
			#print(",,,,,,,,,,",kprime,U2,L,len(kprime)+len(U2)+L[len(B)])
			if len(L)>0+len(B):
				if len(kprime)+len(U2)+L[0+bprime]<=k:
					print("Yes T2")
					print(X,kprime,U2)
					sys.exit()
			print("T2")
			return False
		#sys.exit()
	#terminal case 3
	if len(U2)==0:
		G_U1=G.subgraph(U1).copy()
		kprime=cvdp(G_U1,B,d,k)
		if kprime==None:
			print("T3")
			return False
		if len(L)>d+bprime:
			if len(kprime)+L[d+bprime]<=k:
				print("Yes T3")
				print(X)
				sys.exit()
		print("T3")
		return False
		#sys.exit()

	#case 1
	if len(U1)==0:
		v=random.choice(U2)
		neighbor_v=list(set(G.neighbors(v))-set(X))
		neighbor_v.append(v)
		print("CASE 1 1")
		search(G,U0,neighbor_v,list(set(U2)-set(neighbor_v)),B+[v],k,d-1,L,X)
		print("\n\n\n\n\n\n\nCASE 1 2")
		search(G,U0,[],list(set(U2)-set([v])),B,k-1,d,L,X+[v])
	else:	
		neighbors_U1=[]
		for nodes in U1:
			neighbors_U1+=G.neighbors(nodes)
		neighbors_U1=list(set(neighbors_U1)-set(U1)-set(X))
		print("neigh_U1",neighbors_U1)
		G_U1=G.subgraph(U1).copy()
		result=is_cluster_graph(G_U1)
		if (result[0]) and len(neighbors_U1)==1:
			L1=copy.deepcopy(L)
			for i in range(len(result[1])):
				L1=update_L(L1,[len(result[1][i]),0,infinity])
				print("L1",L1)
			#case 2
			u=neighbors_U1[0]
			neighbor_u=G.neighbors(u)
			neighbor_u_intersecting_U2=list(set(neighbor_u)&set(U2)-set(X))
			for v in neighbor_u_intersecting_U2:
				neighbor_v=G.neighbors(v)
				neighbor_v=list(set(neighbor_v)-set(X))
				neighbor_v.append(v)
				neighbor_v.remove(u)
				G_neigh_v=G.subgraph(neighbor_v).copy()
				if not connected_component_isclique(G_neigh_v):
					print("CASE 2 1")
					search(G,U0+U1,neighbor_v,list(set(U2)-set(neighbor_v+[u])),B+[v],k-1,d-1,L1,X+[u])
					print("\n\n\n\n\n\nCASE 2 2")
					search(G,U0,U1,list(set(U2)-set([v])),B,k-1,d,L,X+[v])
				
						
		else:
			#case3
			neighbors_U1=[]
			for nodes in U1:
				neighbors_U1+=G.neighbors(nodes)
			neighbors_U1=list(set(neighbors_U1)-set(U1)-set(X))
			#v=random.choice(neighbors_U1)
		
			try:
				v=random.choice(neighbors_U1)
			except:
				print(".........Except.........")
				sys.exit()
			"""
				v=random.choice(U2)
				neighbor_v=list(set(G.neighbors(v))-set(X))
				neighbor_v.append(v)
				print("CASE 1 1")
				search(G,U0,neighbor_v,list(set(U2)-set(neighbor_v)),[v],k,d-1,L,X)
				print("\n\n\n\n\n\n\nCASE 1 2")
				search(G,U0,[],list(set(U2)-set([v])),[],k-1,d,L,X+[v])
				return
			"""
			neighbor_v=G.neighbors(v)
			neighbor_v.append(v)
			neighbor_v=list(set(neighbor_v)-set(X))
			neighbor_v_U1=list(set(U1)&set(neighbor_v))
			U0_31=copy.deepcopy(U0)
			U0_32=copy.deepcopy(U0)
			print("CASE 3 1")
			print(U0,U1,U2,B,k,d,L,X)
			search(G,U0_31,list(set(list(set(U1)|set(neighbor_v)))-set(list(set(U1)&set(neighbor_v)))),list(set(U2)-set(neighbor_v)),B+[v],k-len(neighbor_v_U1),d-1,L,X+neighbor_v_U1)
			print("\n\n\n\n\n\n\nCASE 3 2")
			print(U0_32,U1,U2,B,k,d,L,X)
			search(G,U0_32,U1,list(set(U2)-set([v])),B,k-1,d,L,X+[v])
			
def main():
	G=get_graph_file()
	#k=int(input("Enter K:"))
	#d=int(input("Enter d:"))
	k=int(sys.argv[1])
	d=int(sys.argv[2])
	print(k,d,end=' ')
	G,k,solution=kernelization(G,k)
	print()
	print("Kernelization",k,solution)
	"""search(G,U0,U1,U2,B,k,d,L,X)"""
	search(G,[],[],G.nodes(),[],k,d,[0],[])
	"""l1=update_L([0],[5,2,0,infinity])
	l2=update_L(l1,[1,0,infinity])
	l3=update_L(l2,[3,1,0,infinity])
	print(l1,l2,l3)
	#U1=[1,2,3]
	#neighbor_v=[3,4,5]
	print(list(set(list(set(U1)|set(neighbor_v)))-set(list(set(U1)&set(neighbor_v)))))"""
if __name__== "__main__":
	main()
