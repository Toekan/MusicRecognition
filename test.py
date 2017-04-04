import pickle

entry = 10
pickle.dump(entry, open("save.p", "wb"))

a = pickle.load(open('save.p','rb'))
print(a)