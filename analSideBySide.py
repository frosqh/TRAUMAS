from os import listdir

d = {"HEFT": "0;0;0;1;0;1;0", "BIL": "2;0;1;1;0;1;0", "HPS": "4;0;0;1;0;1;0", "DLS": "0;1;4;0;0;0;0",
     "GDL": "0;1;5;0;0;0;0", "MCT": "1;0;0;1;0;0;0", "MET": "1;0;3;1;0;0;0", "OLB": "1;0;2;1;0;0;0"}
hs = ["HEFT", "BIL", "HPS", "DLS", "GDL", "MCT", "MET", "OLB"]
dv = d.values()


def get_key(dict, val):
    for key, value in dict.items():
        if val == value:
            return key

    return "key doesn't exist"


if __name__ == '__main__':
    m = []
    for i in range(len(d)):
        l = []
        for j in range(len(d)):
            l += [[0,0,0]]
        m += [l]
    print(m)
    listFile = listdir("res")

    for fileName in listFile:
        file = open("res/" + fileName, 'r')
        res = {}
        for l in file.readlines():
            for v in dv:
                if l.startswith(v):
                    res[get_key(d, v)] = l.split(";")[-2]
        for i in d:
            for j in d:
                if i != j:
                    if res[i] > res[j]:
                        m[hs.index(i)][hs.index(j)][0] += 1
                    elif res[i] == res[j]:
                        m[hs.index(i)][hs.index(j)][1] += 1
                    else:
                        m[hs.index(i)][hs.index(j)][2] += 1
    print(m)