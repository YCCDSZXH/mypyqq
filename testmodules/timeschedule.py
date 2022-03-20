import math
dayup, dayfactor = 1.0, 0.01
ddup=math.pow((dayup+dayfactor),365)
print("天天向上的力量:{:.2f}",format(ddup))
i=0.01
while 1:
    i+=0.001
    for n in range(1,366) :
        m =n%7
        print(m)
        if 0 <= m <5:
            dayup =dayup*(i+1)
        else: dayup = dayup*0.99
    if dayup>ddup:
        dayfactor=i
        break
print(dayfactor)