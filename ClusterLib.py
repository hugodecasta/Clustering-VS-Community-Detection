from AttClustering import attMethods
from NetClustering import netMethods

# -----------------------------------------------------------
# --------------------------------------------------- LOAD --
def loadData_Att(filename):
	return attMethods.loadData(filename)

def loadData_Net(filename):
	return netMethods.loadData(filename)

# -----------------------------------------------------------
# ---------------------------------------------- TRANSFORM --
def Att2Net(AttObj,method,**kwargs):
	return method(AttObj)

def Net2Att(NetObj,method,**kwargs):
	return method(NetObj)

# -----------------------------------------------------------
# --------------------------------------------- CLUSTERING --
def cluster_Att(method,clusterCount=None,**kwargs):
	return method(clusterCount,kwargs)

def cluster_Net(method,clusterCount=None,**kwargs):
	return method(clusterCount,kwargs)

# -----------------------------------------------------------
# --------------------------------------------- EVALUATION --
def evaluateClustering(terClusters,genClusters,method,**kwargs):
	return method(terClusters,genClusters,kwargs)
