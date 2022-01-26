# distnace.py
import math

def dist(x1,y1,x2,y2):
    return math.sqrt(math.pow(x1-x2, 2)) + math.sqrt(math.pow(y1-y2,2))

# t = dist(1,1,2,2)
# print(t)