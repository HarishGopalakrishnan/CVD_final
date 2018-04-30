#system packages
import networkx as nx
import copy

#user defined functions
import kernelization as kernel
import print_graph
import get_graph


def d_cvd(G,d,k,solution):
	"""
	Input: Graph G represented by p3s,the parameter k and d, solution
	Output: True,solution if the G has a k-sized d-cvd set or False
	"""
	number_cliques=nx.number_connected_components(G)
	if number_cliques<d: # Case 1: number of connected components is lesser than d
		return False,[]
	if number_cliques==d:  # Case 2: number of connected components is equal than d
		return True,solution
	else:	# Case 3: number of connected components is greater than d
		cliques={}
		for connected_component in nx.connected_component_subgraphs(G): # sort the cliques in non decreasing order
			cc_nodes=connected_component.nodes()
			if len(cc_nodes) not in cliques:
				cliques[len(cc_nodes)]=[cc_nodes]
			else:
				cliques[len(cc_nodes)].append(cc_nodes)
		
		while (not number_cliques==d) and k>0: # delete the cliques until d number of connected components(cliques) 
			key=sorted(cliques)[0]
			del_clique=cliques[key].pop(0)
			solution+=del_clique
			k-=key
			if cliques[key]==[]:
				del cliques[key]
			number_cliques-=1
		if k>=0 and number_cliques==d:
			return True,solution
		return False,[]


#3-way branching algorithm for d-CVD
def three_way_branching(G,p3s0,k,d,solution):
	"""
	Three way branching algorithm for d-CVD
	Input: Graph G represented by p3s,the parameter k and d
	Output: True if the G has a k-sized solution or False
	Select a p3 and do a three way branching 
	"""
	p3s1=copy.deepcopy(p3s0)
	p3s2=copy.deepcopy(p3s0)
	p3s3=copy.deepcopy(p3s0)

	if len(p3s0)==0:# if on p3 then graph is a d-cluster graph
		G1=copy.deepcopy(G)
		G1.remove_nodes_from(solution)
		d_cvd_solution=d_cvd(G1,d,k,solution) # check if solution is a k-vertex d-cvd set		
		if d_cvd_solution[0]:
			global sol
			sol=d_cvd_solution[1]
			print ("Solution:",sol)
			return True
		return False
	if k<=0:# the branch has no solution
		return False
	p3=p3s0[0]
	p3s1 = kernel.delete_vertex(p3s1,p3[0])
	p3s2 = kernel.delete_vertex(p3s2,p3[1])
	p3s3 = kernel.delete_vertex(p3s3,p3[2])
	return three_way_branching(G,p3s1,k-1,d,solution+[p3[0]]) or three_way_branching(G,p3s2,k-1,d,solution+[p3[1]]) or three_way_branching(G,p3s3,k-1,d,solution+[p3[2]])


def main():
	G=get_graph.edge_list()	# read the input instance
	print_graph.input(G)
	k=int(input("Enter k:"))
	d=int(input("Enter d:"))
	G,k,solution=kernel.kernelization(G,k) # do kernelization
	print("Kernelization",k,solution)
	p3s=kernel.get_p3(G)
	if not three_way_branching(G,p3s,k,d,solution):	
		print ("No Solution")
	else:
		G.remove_nodes_from(sol)
		print_graph.output(G)
		print_graph.show()

if __name__== "__main__":
	main()
