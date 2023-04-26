'''
"Unpickler" for best_weights.dat.
Prints:
w1 - numpy 4x7 array;
w2 - numpy 7x2 array.
'''
import pickle

with open('best_weights.dat', 'rb') as bpickle:
    w1 = pickle.load(bpickle)
    w2 = pickle.load(bpickle)

    print(w1)
    print(w2)