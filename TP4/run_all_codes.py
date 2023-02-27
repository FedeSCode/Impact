import time
import os

def compute_time(func,N,VERBOSE=False):
    # func: chaîne de caractères permettant de lancer une commande, comme 'python3 python_sort.py'
    # N: taille du tableau à trier
    t1=time.time()
    res = os.popen(func + " " + str(N)).read()
    t2 = time.time()
    if VERBOSE:
        print(func + ", temps de calcul total = "+str(t2-t1) + " secondes")
        print("temps pour le tri = "+str(res))
    return t2-t1
    

def compute_times(func,all_N,t_pause=0,VERBOSE=False):
    # computation time for func(n) for n in all_N
    all_t = []
    for n in all_N:
        t = compute_time(func,n,VERBOSE)
        time.sleep(t_pause)
        all_t.append(t)
    return all_t


def run_all_codes():

    data = []

    cmd0= ['py python_sort.py']
    cmd1=['gcc -o quick_sort quick_sort.c |  quick_sort.exe']
    cmd2=['java quickSort.java']

    list= [10,40,60,80,100]

    cmd0.append(list)
    cmd1.append(list)
    cmd2.append(list)

    data.append(cmd0)
    data.append(cmd1)
    data.append(cmd2)

    for i in range(len(data)):
        dataToAppend = compute_times(data[i][0],data[i][1])
        cmd = data[i]
        cmd.append(dataToAppend)
        data[i] = cmd
    
    return data


data = run_all_codes()
print (data[0][2])