from __future__ import division
import math

def circle(point1, point2, point3):
	x, y, z = complex(point1[0], point1[1]), complex(point2[0], point2[1]), complex(point3[0], point3[1])
	w = z-x
	w /= y-x
	c = (x-y)*(w-abs(w)**2)/2j/w.imag-x
	return ((round(-c.real, 5), round(-c.imag, 5)), round(abs(c+x), 5))

def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def intersection(L1, L2):
    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return False

def rectangular(polar):
	return (round(polar[0] * math.cos(polar[1]), 5), round(polar[0] * math.sin(polar[1]), 5))

def findTriple(radius, inLength, angle, size):
	edge = rectangular((radius, angle + (size * 0.5)))
	pointA = rectangular((radius - inLength, angle))
	pointB = rectangular((radius - inLength, angle + size))
	center, r = circle(pointA, pointB, edge)
	pointADir = (-(pointA[1] - center[1]), pointA[0] - center[0])
	pointBDir = (-(pointB[1] - center[1]), pointB[0] - center[0])
	pointA2 = (pointA[0] + pointADir[0], pointA[1] + pointADir[1])
	pointB2 = (pointB[0] + pointBDir[0], pointB[1] + pointBDir[1])
	lineA = line(pointA, pointA2)
	lineB = line(pointB, pointB2)
	inter = intersection(lineA, lineB)
	return (round(inter[0], 5), round(inter[1], 5))

def addTuple(a, b):
	t = []
	for i in range(len(a)):
		t += [a[i] + b[i]]
	return tuple(t)

def multTuple(a, k):
	t = []
	for i in range(len(a)):
		t += [a[i] * k]
	return tuple(t)

def subTuple(a, b):
	t = []
	for i in range(len(a)):
		t += [a[i] - b[i]]
	return tuple(t)

def roundTuple(a):
	t = []
	for i in range(len(a)):
		t += [round(a[i], 5)]
	return tuple(t)

def getCirclePoints(center, radius, inLength, n):
	step = math.pi * 2.0 / n
	angle = 0
	l = ""
	for i in range(n + 1):
		pointA = rectangular((radius - inLength, angle))
		pointB = rectangular((radius - inLength, angle + step))
		pointControl = findTriple(radius, inLength, angle, step)
		pointA = addTuple(pointA, center)
		pointB = addTuple(pointB, center)
		pointControl = addTuple(pointControl, center)
		if l == "":
			l += "M " + str(pointA[0]) + " " + str(pointA[1])
		l += " Q " + str(pointControl[0]) + " " + str(pointControl[1]) + " " + str(pointB[0]) + " " + str(pointB[1]) + " "
		angle += step
	return l

def printSvg(l):
	print '<path d="' + l + '" stroke="#F1E398" fill="#FBDB14" stroke-width="2" stroke-linecap="round" fill-rule="nonzero"/>'

def getTangent(center, radius, point):
	Cx, Cy = center
	Px, Py = point
	a = radius
	b = math.sqrt((Px - Cx)**2 + (Py - Cy)**2)  # hypot() also works here
	th = math.acos(a / b)  # angle theta
	d = math.atan2(Py - Cy, Px - Cx)  # direction angle of point P from C
	d1 = d + th  # direction angle of point T1 from C
	d2 = d - th  # direction angle of point T2 from C
	T1x = Cx + a * math.cos(d1)
	T1y = Cy + a * math.sin(d1)
	T2x = Cx + a * math.cos(d2)
	T2y = Cy + a * math.sin(d2)
	# print (center, radius, point, roundTuple((T1x, T1y)), roundTuple((T2x, T2y)))
	return roundTuple((T1x, T1y))

def getLinePoints(center, radius, smallRadius, n):
	step = math.pi * 2.0 / n
	angle = 0
	l = ""
	for i in range(n):
		pointA = rectangular((radius, angle))
		pointA = addTuple(pointA, center)
		pointA2 = getTangent(center, smallRadius, pointA)
		# extend the line a bit
		pointA2 = addTuple(pointA, multTuple(subTuple(pointA2, pointA), 1.05))
		angle += step
		l += '<path d="' + "M" + str(pointA[0]) + " " + str(pointA[1])  + " L " + str(pointA2[0]) + " " + str(pointA2[1]) + '" stroke="#F1E398" fill="transparent" stroke-width="4" /> \n'
	return l

printSvg(getCirclePoints((200, 200), 150, 15, 7))
print getLinePoints((200, 200), 135, 15, 7)