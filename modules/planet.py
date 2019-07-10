#!/usr/bin/env python3

import numpy as np

from collections import deque

import config
CUSTOM_ACC = config.CUSTOM_ACC
HAS_CHARGE = config.CHARGE
ROUND_SPACE = config.ROUND_SPACE
ACC_MARKERS = config.ACC_MARKERS
N_DIMENSION = config.N_DIMENSION


class Planet():
    __slots__ = 'num_dimension', 'pos', 'vel', 'acc', 'mass', 'collided', \
                'tail', 'tail_len', 'tail_time', 'tail_back', 'tail_coords', 'data'

    def __init__(self, pos=None, vel=None, acc=None, mass=1.,
                 num_dimension=2, tail_len=5, tail_time=.1, tail_back=0,
                 **kwargs):
        self.num_dimension = num_dimension

        self.pos = np.array([0.]*self.num_dimension)
        self.vel = self.pos.copy()
        self.acc = self.pos.copy()

        if pos:
            self.pos[:len(pos)] = pos[:num_dimension]
        if vel:
            self.vel[:len(vel)] = vel[:num_dimension]
        if acc:
            self.acc[:len(acc)] = acc[:num_dimension]        

        '''
        self.pos = np.array(pos) if pos else np.array([0.]*self.num_dimension)
        self.vel = np.array(vel) if vel else np.array([0.]*self.num_dimension)
        self.acc = np.array(acc) if acc else np.array([0.]*self.num_dimension)
        '''
        self.mass = np.array(mass)
        self.collided = False

        # Dict for other data about planet
        self.data = kwargs
        
        # Tail
        self.tail_back = tail_back
        self.tail_len = tail_len
        self.tail_time = tail_time
        self.tail = deque(maxlen=tail_len)
        self.tail.appendleft((self.pos.copy(), 0.))
        self.tail_coords = deque(maxlen=tail_len*2)
        self.tail_coords.extendleft(self.pos[1::-1])

    def update_acc(self, dt, s):
        self.acc.fill(0.)
        '''
        # Add gravity force
        # Start function
        for obj in s.objects:
            if self is not obj:
                dist = np.linalg.norm(self.pos - obj.pos)
                if not(dist < self.round_size() + obj.round_size() or \
                        self.collide_check(obj)):
                    self.acc += (obj.pos - self.pos) * obj.mass * s.grav_const / dist**2
                else:
                    self.collided = obj
                    break
        # End function
        '''
        # See custom functions in file custom_update.py
        CUSTOM_ACC(self, space=s, dt=dt)

    def update_vel(self, dt):
        self.vel += self.acc * dt

    def update_pos(self, dt):
        self.pos += self.vel * dt
        pos = self.pos
        tail = self.tail
        new_dt = dt + tail[0][1]
        if new_dt < self.tail_time / self.tail_len:
            self.tail[0] = (pos.copy(), new_dt)
            self.tail_coords[0] = pos[0]
            self.tail_coords[1] = pos[1]
        else:
            self.tail.appendleft((pos.copy(), dt))
            self.tail_coords.appendleft(pos[1])
            self.tail_coords.appendleft(pos[0])
            if self.tail_back > 0:
                self.tail_back -= 2

    def rotate(self, matrix, matrix_from_origin):
        num = self.num_dimension
        pos = self.pos.copy()
        vel = self.vel.copy()
        acc = self.acc.copy()

        pos.resize(num + 1)
        pos[-1] = 1.
        self.pos = np.resize(np.dot(matrix, pos), num)

        vel.resize(num + 1)
        vel[-1] = 1.
        self.vel = np.resize(np.dot(matrix_from_origin, vel), num)

        acc.resize(num + 1)
        acc[-1] = 1.
        self.acc = np.resize(np.dot(matrix_from_origin, acc), num)

        new_tail = deque(maxlen=self.tail_len)
        new_tail_coords = deque(maxlen=self.tail_len*2)
        
        for tail_pos, tail_dt in self.tail:
            tail_pos = np.resize(tail_pos, num + 1)
            tail_pos[-1] = 1.
            new_tail_pos = np.resize(np.dot(matrix, tail_pos), num)
            
            new_tail.append((new_tail_pos, tail_dt))
            new_tail_coords.append(new_tail_pos[0])
            new_tail_coords.append(new_tail_pos[1])
        
        self.tail = new_tail
        self.tail_coords = new_tail_coords

    def translate(self, matrix):
        num = self.num_dimension
        
        pos = np.zeros(num + 1)
        pos[:num] = self.pos
        pos[-1] = 1.
        self.pos = np.dot(matrix, pos)[:num]

        new_tail = deque(maxlen=self.tail_len)
        new_tail_coords = deque(maxlen=self.tail_len*2)
        
        for tail_pos, tail_dt in self.tail:
            tail_pos = np.resize(tail_pos, num + 1)
            tail_pos[-1] = 1.
            new_tail_pos = np.resize(np.dot(matrix, tail_pos), num)
            
            new_tail.append((new_tail_pos, tail_dt))
            new_tail_coords.append(new_tail_pos[0])
            new_tail_coords.append(new_tail_pos[1])

        self.tail = new_tail
        self.tail_coords = new_tail_coords

    def round_size(self, m=6.):
        return self.mass**(1./self.num_dimension) * m

    def collide_check(self, obj):
        tail = self.tail
        if len(tail) < 2:
            return False

        first = tail[0][0]
        second = tail[1][0]
        d = first - second
        f = second - obj.pos

        a = np.dot(d, d)
        b = 2. * np.dot(f, d)
        c = np.dot(f, f) - obj.round_size()

        discr = b**2 - 4. * a * c

        if discr < 0. or a == 0.:
            return False
        else:
            discr = discr**.5
            t1 = (-b - discr) / (2. * a)
            t2 = (-b + discr) / (2. * a)
            if t2 >= 0. and t2 <= 1.:
                return True
            return False
