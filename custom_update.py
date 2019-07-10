#!/usr/bin/env python3

import numpy as np

from modules.utility import _map;

def custom_acc1(obj, space=None, **kwargs):
    '''Simple custom function for update point
    '''
    x, y = 600, 300
    obj.acc = np.array((x, y) + (0.,)*(obj.num_dimension-2)) - obj.pos
    obj.acc /= 100

def custom_acc2(obj, space=None, **kwargs):
    '''Rotate around center
    Delete if collide with edge
    '''
    x, y = space.center_x, space.center_y
    w, h = space.width, space.height
    from math import sin, cos, pi
    a = pi/6.
    c = cos(a)
    s = sin(a)
    rot = np.array([[c, -s],   
                    [s,  c]])
    rot_matrix = np.zeros((obj.num_dimension, obj.num_dimension))
    rot_matrix[:2, :2] = rot
    obj.acc = np.array( (x, y)+(0.,)*(obj.num_dimension-2) ) - obj.pos
    obj.acc = np.dot(rot_matrix, obj.acc)
    obj.vel = obj.vel / 1.02
    ox, oy, *_ = obj.pos
    if ox < x-w/2 or ox > x+w/2 or oy < y-h/2 or oy > y+h/2:
        obj.collided = True

def custom_acc3(obj, space=None, **kwargs):
    '''Collide to the edges and translate to other side
    '''
    num = obj.num_dimension
    x, y = space.center_x, space.center_y
    w, h = space.width, space.height

    ox, oy, *_ = obj.pos

    ox2 = _map(ox, x-w/2, x+w/2, fl=x+w/2, fr=x-w/2)
    oy2 = _map(oy, y-h/2, y+h/2, fl=y+h/2, fr=y-h/2)

    if ox != ox2 or oy != oy2:
        dx, dy = ox2-ox, oy2-oy
        matrix_translate = np.eye(num+1)
        matrix_translate[0:2, num:num+1] = ((dx,), (dy,),)
        obj.translate(matrix_translate)

def custom_acc3_1(obj, space=None, **kwargs):
    '''Collide to the edges and reflect
    '''
    num = obj.num_dimension
    x, y = space.center_x, space.center_y
    w, h = space.width, space.height

    ox, oy, *_ = obj.pos

    ox2 = _map(ox, x-w/2, x+w/2, fl=x-w/2, fr=x+w/2)
    oy2 = _map(oy, y-h/2, y+h/2, fl=y-h/2, fr=y+h/2)

    if ox != ox2 or oy != oy2:
        dx, dy = ox2-ox, oy2-oy
        matrix_translate = np.eye(num+1)
        matrix_translate[0:2, num:num+1] = ((dx,), (dy,),)
        obj.translate(matrix_translate)
        if dx != 0.:
            obj.vel[0] = -obj.vel[0] / 2.
            obj.vel[1] = obj.vel[1] * 0.7
        if dy != 0.:
            obj.vel[1] = -obj.vel[1] / 2.
            obj.vel[0] = obj.vel[0] * 0.7

def custom_acc3_2(obj, space=None, **kwargs):
    '''Round collide space
    '''
    num = obj.num_dimension
    center = np.array((space.center_x, space.center_y))
    w, h = space.width, space.height

    r = min(w, h) / 2 - 10

    # ox, oy, *_ = obj.pos

    pos = obj.pos[:2]

    rp = np.linalg.norm(pos - center) + obj.round_size()

    if rp > r:
        # rp += kwargs.get('dt', 0.) * np.linalg.norm(obj.vel)
        
        pos_to = r / rp * (pos - center) + center
        dpos = pos_to - pos


        '''
        ox2 = (ox - x) / rp * r + x
        oy2 = (oy - y) / rp * r + y 
        dx, dy = ox2-ox, oy2-oy

        from math import sin, cos, pi, atan2
        a = atan2(oy2/rp, ox2/rp) + pi/2.
        if ox2 < 0.:
            a -= pi/2.
        c = cos(a)
        s = sin(a)
        '''
        norm_pos_center = (pos_to - center) / r # why /rp?

        c = norm_pos_center[0]
        s = norm_pos_center[1]
        # print(f'a={a} c={c} s={s}')
        # Reflect in round
        rot_matrix = np.array( ((c**2-s**2, 2*c*s),   
                                (2*c*s,     s**2-c**2)) )
        vel = obj.vel[:2]
        # Energy of collide
        vel *= -0.9
        obj.vel[:2] = np.dot(rot_matrix, vel)

        matrix_translate = np.eye(num + 1)
        matrix_translate[0:2, num:num + 1] = np.reshape(dpos, (2, 1))
        obj.translate(matrix_translate)

        dt = kwargs.get('dt', 0.)
        acc = obj.acc[:2]

        next_dpos = (vel + acc * dt) * dt

        if r + np.dot(next_dpos, norm_pos_center) > r:
            obj.acc[:2] = acc - (np.dot(acc, norm_pos_center) / r**2 * norm_pos_center)
            obj.vel[:2] = vel - (np.dot(vel, norm_pos_center) / r**2 * norm_pos_center)


        
        '''
        if dx != 0.:
            obj.vel[0] = -obj.vel[0] # / 2.
            #obj.vel[1] = obj.vel[1] * 0.7
        if dy != 0.:
            obj.vel[1] = -obj.vel[1] #/ 2.
            #obj.vel[0] = obj.vel[0] * 0.7
        '''
def custom_acc4(obj, space=None, **kwargs):
    '''Sin-like path particles
    '''
    custom_acc3(obj, space=space)

    ox, oy, *_ = obj.pos

    from math import sin, cos

    vx = obj.vel[0]
    if vx == 0.:
        vx = 100
        obj.vel[0] = vx

    obj.vel[1] = 70*sin(ox/20) * vx / abs(vx)
    obj.vel[:2] = obj.vel[:2] / np.linalg.norm(obj.vel[:2]) * 150

def custom_acc5(obj, space=None, **kwargs):
    '''Charged particles in round collide space
    '''

    for other in space.objects:
        if obj is not other:
            dist = np.linalg.norm(obj.pos - other.pos)
            
            if not(dist < obj.round_size() + other.round_size() or \
                    obj.collide_check(other)):
                charge1 = obj.data.get('charge', None)
                charge2 = other.data.get('charge', None)
                charge = charge1 * charge2
                obj.acc += (other.pos - obj.pos) * -charge * space.grav_const / dist**2 / obj.mass
            else:
                obj.collided = other
                break

    custom_acc3_2(obj, space=space, **kwargs)

def custom_acc6(obj, space=None, **kwargs):
    '''Default gravity
    '''

    for other in space.objects:
        if obj is not other:
            dist = np.linalg.norm(obj.pos - other.pos)
            if not(dist < obj.round_size() + other.round_size() or \
                    obj.collide_check(other)):
                obj.acc += (other.pos - obj.pos) * other.mass * space.grav_const / dist**2
            else:
                obj.collided = other
                break