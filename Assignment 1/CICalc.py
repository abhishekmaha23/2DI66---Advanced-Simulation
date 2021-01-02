from scipy import stats
from numpy import std, mean

def Q1CI(n):
    p1_probs = list()
    p2_probs = list()
    draw_probs = list()
    for i in range(n):
        temp = Question1(3, 100000)
        p1_probs.append(temp[0])
        p2_probs.append(temp[1])
        draw_probs.append(temp[2])
        print(i)
    return (p1_probs, p2_probs, draw_probs)

runs = 10

list_probs = Q1CI(runs)
print(list_probs)

std_p1_prob = std(list_probs[0])
p1_halfwidth = 1.96 * std_p1_prob/ (runs ** 0.5)

p1_prob = mean(list_probs[0])
p1_ci = (p1_prob - p1_halfwidth, p1_prob + p1_halfwidth)

print(p1_prob)
print(p1_ci)

std_p2_prob = std(list_probs[1])
p2_halfwidth = 1.96 * std_p2_prob/ (runs ** 0.5)

p2_prob = mean(list_probs[1])
p2_ci = (p2_prob - p2_halfwidth, p2_prob + p2_halfwidth)

print(p2_prob)
print(p2_ci)

std_draw_prob = std(list_probs[2])
draw_halfwidth = 1.96 * std_draw_prob/ (runs ** 0.5)

draw_prob = mean(list_probs[2])
draw_ci = (draw_prob - draw_halfwidth, draw_prob + draw_halfwidth)

print(draw_prob)
print(draw_ci)
