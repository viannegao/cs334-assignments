'''
Created on Oct 1, 2016

@author: vianne
'''
from itertools import chain, combinations

#Class of functional dependencies in which lhs --> rhs implies that the rhs can be determined from the lhs.
class fd:
    def __init__(self,lhs,rhs):
        self.lhs = frozenset(lhs)
        self.rhs = frozenset(rhs)
    def __str__(self):
        return str(list(self.lhs)) +'-->' + str(list(self.rhs))
    def __eq__(self,other):
        return (self.lhs == other.lhs) & (self.rhs == other.rhs)
    def __hash__(self):
        return hash(self.lhs) * hash(self.rhs)
    def isTrivial(self): #check if the lhs is part of the rhs
        return self.lhs >= self.rhs


# class relation:
#     def __init__(self, att, allfds, fd1, fd2):
#         self.attributes = att
#         self.allfds =[allfds]
#         self.fd1 = fd1
#         self.fd2 = fd2
        
class closure:
    def __init__(self,attr,given_fds):
        self.attr = attr
        self.given_fds = set()
        self.clsr = set()
        for i in range(0,len(given_fds)):
            self.given_fds.add(getFD(given_fds[i]))
        self.getclosure()
    #generates the closure of the given fd
    def getclosure(self):
        #add trivial fds to the set of all known fds 
        known_fds = self.given_fds.union(usereflexivity(self.attr))
        #repeat using augmentation and transitivity until the closure does not change anymore
        done = False;
        while done == False:
            all_fds = useaugmentation(known_fds,powerset(self.attr))
            all_fds = usetransitivity(all_fds)
            done = len(all_fds)==len(known_fds)
            known_fds = all_fds
        self.clsr = known_fds
        
    def __str__(self):
        toPrint = []
        for f in self.clsr:
            toPrint.append(str(f))
        return str(toPrint)
       
def getFD (fd_id):
    a_fd = fd(fd_id[0],fd_id[1])
    return a_fd       

#generate a list of all possible combinations of attributes in a set
def powerset(a_set):
    return list(chain.from_iterable(combinations(a_set,a) for a in range (1, len(a_set)+1)))

#generate a set of trivial fd for given attributes   
def usereflexivity(r):
    all_ref = set()
    for i in powerset(r):
        for j in powerset(i):
            all_ref.add(fd(i,j))
    return all_ref

#generate a set of augmented fd for the set of fiven fd
#Augmentation: if X -> Y, then XZ -> YZ
#f is a set of fd, PS is the powerset of all attributes in the schema
def useaugmentation(f,PS):
    augmented = set()
    for i in f:
        for j in PS:
            augmented.add(fd(i.lhs.union(j),i.rhs.union(j)))
    return augmented

#generate a set of fds derived from the transitivity rule
#Transitivity: if X -> Y, and Y -> Z, then X -> Z
#param f: set of fd
def usetransitivity(f):
    trans = set()
    for i in f:
        for j in f:
            if i.rhs == j.lhs:
                trans.add(fd(i.lhs,j.rhs))
    return f.union(trans)

#find all the superkeys by looking at the rhs of fds in the closure
def superkeys (attr, clsr):
    skey = set()
    for f in clsr:
        if len(f.rhs) == len(attr):
            skey.add(f.lhs)
    return skey

#find all candidate keys
def getCandidateKey(attr, clsr):
    skey = superkeys(attr,clsr)
    ckey = set()
    sorted_skey = sorted(skey, lambda x,y:cmp(len(x),len(y)))
    for k in sorted_skey:
        addkey = True
        for c in ckey:
            if (k <= c):
                addkey = False
        if addkey:
            ckey.add(k)
    return ckey

#see if there is a fd such that lhs is not a skey
def inBCNF(clsr,skeys):
    for f in clsr:
        if (not f.isTrivial()) and (f.lhs not in skeys):
            return False
    return True

def badFd(clsr, skeys):
    sorted_clsr = sorted(clsr,lambda x,y:cmp(len(x.lhs),len(y.lhs)))
    for f in sorted_clsr:
        if ((not f.isTrivial()) and (f.lhs not in skeys)):
            return f

def decomposeRelation(bad_fd, attr, clsr):
    R1 = bad_fd.lhs | bad_fd.rhs
    R2 = (attr - bad_fd.rhs) | bad_fd.lhs
    R1_clsr = set()
    R2_clsr = set()
    for f in clsr:
        if (f.lhs <= R1) and (f.rhs <= R1):
            R1_clsr.add(f)
        if (f.lhs <= R2) and (f.rhs <= R2):
            R2_clsr.add(f)
    return (R1, R2, R1_clsr, R2_clsr)

def decomposeToBCNF(attr, clsr):
    result = attr #convert from list to set in another function
    print 'The relation to be decomposed is: '+ str(list(attr))
    skeys = superkeys(attr,clsr) #return a set of skeys
    if not inBCNF(clsr,skeys):
        print 'This is not in BCNF'
        fd = badFd(clsr,skeys) #return the key to decompose by
        print 'This relation is decomposed using the fd: '+ str(fd)
        (R1,R2,R1_clsr,R2_clsr) = decomposeRelation(fd,attr,clsr)
        print 'The decomposed relations are: ' + str(list(R1)) +' and '+ str(list(R2)) 
        #recurse
        D1=decomposeToBCNF(R1,R1_clsr)
        D2=decomposeToBCNF(R2,R2_clsr)
        aList = list(D1),list(D2)
        return aList
    else:
        print 'This is in BCNF, so it is not further decomposed.'
        return result

def BCNF(attr,allfds):
    R = set(attr)
    temp = closure(attr,allfds)
    clsr = temp.clsr
    decomposedR = decomposeToBCNF(R, clsr)
    return 'The decomposed relations in BCNF are: ' + str(list(decomposedR))
    
    
    
def main():
    #attributes = [1,2,3,4,5]
    fd1 = ([1],[2])
    fd2 = ([2,3],[5]) 
    fd3 = ([5,4],[1]) #tuples of lists
    allfds =[fd1,fd2,fd3] #list of tuples of lists
#     test = closure(attributes, allfds)
#     test.getclosure(attributes, allfds)
    print(closure([1,2,3,4,5],allfds))
    print(BCNF([1,2,3,4,5],allfds))
    #print (test.attributes, test.allfds, test.fd1, test.fd2)
    #print powerset(attributes)
    #test2 = fd(fd2[0],fd2[1])
    #print test2.lhs, test2.rhs

main()