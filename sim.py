#coding=utf-8

import matplotlib.pyplot as plt
import numpy as np
import os


def calculate_vinc(v_min, v_max):
    return (v_max - v_min) / 400.0
    

def calculate_p(v_min, v_curr, t_dec, v_max=5.0):
    s0 = v_min * t_dec
    a0 = (v_curr - v_min) / t_dec
    s = s0 + a0 * (0.5 * t_dec * (t_dec - 1.0))
    return s

def calculate_pu(v_min, v_curr, t_dec, v_max=5.0):
    kd = (v_max - v_min) / t_dec #Accelarate
    n = abs(int((v_curr - v_min) / kd))
    s = n * v_min + n*(n+1)*0.5*kd
    return s


def generate(p_total, pic_n, calc_func):
    vdir = 0
    if p_total >= 0:
        vdir = 1
    else:
        vdir = -1
        
    v__min = 0.0005 * vdir
    v__max = 5.0 * vdir
    
#    p_total = 2000
    v_curr = v__min
    delta = calculate_vinc(v__min, v__max)
    p_sum = 0
    p_send = 0
    state_machine = 1

    x_count = 0
    axis_x  = []
    axis_y1 = []
    axis_y2 = []
    axis_y3 = []
    tips = 0

    while True:
        x_count += 1
        axis_x.append(x_count)
        axis_y1.append(v_curr)
        axis_y2.append(p_send)
        axis_y3.append(calc_func(v__min, v_curr, 400.0, v__max))
       
        
        if state_machine == 1:
            v_curr += delta
            if np.fabs(v_curr) > np.fabs(v__max):
                v_curr = v__max

            p_sum += v_curr
            if abs(int(p_sum)) > 0:
                p_sum_int = int(p_sum)
                p_send += p_sum_int
                p_sum -= p_sum_int
                
            remain = p_total - p_send 
            need = calc_func(v__min, v_curr, 400.0, v__max)
            #print(v_curr, need)
            if abs(remain) < abs(int(need)):
                print('加速=>')
                print('当前速度:{:.4f}\n已发送脉冲:{}\n剩余脉冲:{}\n减速所需要脉冲:{:.4f}\n运行计数:{}\n'.format(v_curr, p_send, remain, need, x_count))
                #print(v_curr, p_send, remain, need, x_count)
                state_machine = 2
                
        elif state_machine == 2:
            v_curr -= delta
            if np.fabs(v_curr) < np.fabs(v__min):
                if tips == 0:
                    print('速度减小到偏置速度')
                    print('当前速度:{:.4f}\n已发送脉冲:{}\n剩余脉冲:{}\n运行计数:{}\n'.format(v_curr, p_send, remain, x_count))
                    break
                v_curr = v__min

            p_sum += v_curr
            if abs(int(p_sum)) > 0:
                p_sum_int = int(p_sum)
                p_send += p_sum_int
                p_sum -= p_sum_int

            remain = p_total - p_send
            if int(remain) == 0:
                print('运行完成:\n当前速度:{}\n剩余脉冲数:{}\n'.format(v_curr, remain))
                break

    print('\n\n')
    return axis_x, axis_y1, axis_y2, axis_y3


    
#Application Entry
if __name__ == '__main__':

    #fcalc = calculate_pu
    fcalc = calculate_p
    
    x0, yv0, ys0, yr0 = generate(1000, 0, fcalc)
    x1, yv1, ys1, yr1 = generate(2000, 1, fcalc)

#    try:
#        with open('sim_log.txt', 'w+') as fp:
#            for i in range(0, 495):
#                fp.write('v1:{:.4f}, P1000:{:.4f}, v2:{:.4f}, P2000:{:.4f}\n'.format(yv0[i], ys0[i], yv1[i], ys1[i]))
#    except OSError as e:
#        print(e)

# Draw it
    plt.figure(0)
    plt.xlabel('time(t)')
    plt.ylabel('velocity(v)')
    plt.plot(x0, yv0, color='red', linewidth=1, linestyle='-')
    plt.plot(x1, yv1, color='blue', linewidth=1, linestyle='-')

    plt.figure(1)
    plt.xlabel('time(t)')
    plt.ylabel('Need(pluses)')
    plt.plot(x0, yr0, color='red', linewidth=1, linestyle=':')
    plt.plot(x1, yr1, color='blue', linewidth=1, linestyle=':')

    plt.figure(3)
    plt.xlabel('time(t)')
    plt.ylabel('Position(pluses)')
    plt.plot(x0, ys0, color='red', linewidth=1, linestyle=':')
    plt.plot(x1, ys1, color='blue', linewidth=1, linestyle=':')
    plt.show()
    #os.system('pause')

    
    
