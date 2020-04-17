import numpy as np
import os

def convertToOneHot(vector, num_classes=None):
    
    assert isinstance(vector, np.ndarray)
    assert len(vector) > 0

    if num_classes is None:
        num_classes = np.max(vector)+1
    else:
        assert num_classes > 0
        assert num_classes >= np.max(vector)

    result = np.zeros(shape=(len(vector), num_classes))
    result[np.arange(len(vector)), vector] = 1
    return result.astype(int)

def read_skel(data_dir, u):
    
    skelone = np.zeros((1,8,3))
    for line in open(data_dir + "user_{0}.txt".format(u+1)):
        numbers = line.split(" ")[2:]
        numbers[-1] = numbers[-1][:-1]
        frame = np.zeros((1,8,3))
        k = 0
        for j in range(8):
            for d in range(3):
                frame[0,j,d] = np.float(numbers[k])
                k += 1
        skelone = np.concatenate((skelone,frame),0)
    skelone = skelone[1:]
    return skelone

def read_annotations(path):
    annotations = {}
    annotations['w'] = [[],[],[],[],[],[]]
    annotations['s'] = [[],[],[],[],[],[]]
    annotations['r'] = [[],[],[],[],[],[]]
    annotations['p'] = [[],[],[],[],[],[]]
    
    for line in open(path + "annotation.txt"):
        anno = line.split(" ")
        action, pair, _rec, start, stop, leader = anno[0], int(anno[1]), int(anno[2]), int(anno[3]), int(anno[4]),  int(anno[5])
        annotations[action][pair-1].append([start,stop, leader])
        
    return annotations


def filterme(x, d): 
    return (-3*x[d-2]+12*x[d-1]+17*x[d]-3*x[d+2]+12*x[d+1]) / 35.

def smooth_skels(skel_one, skel_two):
    temp_one = np.copy(skel_one)
    temp_two = np.copy(skel_two)
    for t in range(2, skel_one.shape[0]-2):
        temp_one[t] = filterme(skel_one, t)
        temp_two[t] = filterme(skel_two, t)
    return temp_one, temp_two
    

def read_data(path, actions = ["waving", "shaking", "rocket", "parachute"], pairs =  ['1','2','3','4','5'], smooth = False, inc_joints = range(8)): 
    
    

    annotations = read_annotations(path)
        
    actor_one  = []
    actor_two  = []
    action_lab = []
    data_sort  = []
    
    for pairofpeople in pairs:
        for rec in range(2):
            action_counter = -1
            for act in range(len(actions)):
                action_counter += 1
                action = actions[act]
                data_dir    = path + action + "/pair_" + pairofpeople + "_rec_" + str(rec) + "_"
                # read skeletal data
                skel_one    = read_skel(data_dir,0)
                skel_two    = read_skel(data_dir,1)
                if smooth:
                    skel_one, skel_two = smooth_skels(skel_one, skel_two)
                    
                # make labels and set pre- and post-action time stemps to unobserved
                labels      = convertToOneHot(action_counter*np.ones((skel_one.shape[0])).astype('int'), len(actions))   
                start, stop, leader = annotations[action[0]][int(pairofpeople)-1][rec]
                labels[0:start, :] = 1
                labels[stop:, :] = 1
                if leader == 0:
                    actor_one.append(skel_one[:,inc_joints,:])
                    actor_two.append(skel_two[:,inc_joints,:])
                else:
                    actor_one.append(skel_two[:,inc_joints,:])
                    actor_two.append(skel_one[:,inc_joints,:])
                action_lab.append(labels)
                data_sort.append([action, pairofpeople, rec])
    return actor_one, actor_two, action_lab, data_sort
                
                
actions = ["waving", "shaking", "rocket", "parachute" ]
 
path_data = os.getcwd() +  "/data4/"

skel_one, skel_two, labels, ds = read_data(path_data,  actions, smooth=True)