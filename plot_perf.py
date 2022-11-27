import pickle
import numpy as np
import json


def one2two(label):
    VF_list = [1,2,4,8,16] # TODO: change this to match your hardware
    IF_list = [1,2,4,8,16] # TODO: change this to match your hardware
    y1 = VF_list[int(int(label) / 5)]
    y2 = IF_list[int(int(label) % 5)]
    return (y1, y2)


f = open('lore_runtimes.pickle', 'rb')
runtimes = pickle.load(f)    
f.close()
f = open('lore_runtimes_none_pragma.pickle', 'rb')
base_runtimes = pickle.load(f)    
f.close()

vf_if = {}
times = {}
files_VF_IF = runtimes.keys()
vf_list = []
if_list = []
baseline = {}
sp = {}
for file_VF_IF in files_VF_IF:
    tmp = file_VF_IF.rpartition('.')
    fn = tmp[0]
    tmp = tmp[2].split('-')
    VF = int(tmp[0])
    IF = int(tmp[1])
    fn_c = fn
    rt_mean = np.mean(runtimes[file_VF_IF])
    base_mean = np.mean(base_runtimes[fn])
    if fn_c not in vf_if.keys():
        vf_if[fn_c] = (rt_mean, VF, IF)
    else:
        rt_mean_pre = vf_if[fn_c][0]
        if rt_mean < rt_mean_pre:
            vf_if[fn_c] = (rt_mean, VF, IF)    
    if fn_c not in times.keys():
        times[fn_c] = {}
    if VF not in times[fn_c].keys():
        times[fn_c][VF] = {}
    if IF not in times[fn_c][VF].keys():
        times[fn_c][VF][IF] = rt_mean
    else:
        rt_mean_pre = times[fn][VF][IF]
        if (rt_mean < rt_mean_pre):                      
            times[fn_c][VF][IF] = rt_mean
    if fn_c not in baseline.keys():
        baseline[fn_c] = base_mean
    else:
        base_mean_pre = baseline[fn_c]
        if base_mean < base_mean_pre:       
            baseline[fn_c] = base_mean

for f in baseline:
    sp[f] = baseline[f] / vf_if[f][0]

#sp_sort = dict(sorted(sp.items(), key=lambda item: item[1]))
#top5 = list(sp_sort.keys()][0:5]
#print("top = ", list(sp_sort.values())[0:5])
benchmarks = ['poly', 'spec', 'npb']
methods = ['autograph', 'neurovec']
for benchmark in benchmarks:
    f = open('lore_testing_autograph_800k_'+benchmark+'.json', 'rb')
    pred = json.load(f)
    f.close()
    files = list(pred.keys())
    sp_bench = {}
    for f in files:
        sp_bench[f] = sp[f]
    sp_bench_sort = dict(sorted(sp_bench.items(), key=lambda item: item[1], reverse=True))
    print("benchmark = ", benchmark)
    top5 = list(sp_bench_sort.keys())[0:5]
    print("top 5 = ", top5)
    print("top 5 = ", list(sp_bench_sort.values())[0:5])
    for method in methods:
        f = open('lore_testing_'+method+'_800k_'+benchmark+'.json', 'rb')
        pred = json.load(f)
        f.close()
        print("method  = ", method)
        #print("benchmark = ", benchmark, " method = ", method)
        for f in top5:
            VF, IF = one2two(pred[f])
            print("speedup = ", baseline[f] / times[f][VF][IF])
