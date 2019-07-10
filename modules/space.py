#!/usr/bin/env python3

from kivy.app import App
from kivy.uix.widget import Widget
# from kivy.uix.effectwidget import EffectWidget # , HorizontalBlurEffect, VerticalBlurEffect, FXAAEffect
from kivy.graphics.vertex_instructions import (Line, Ellipse, Point)
from kivy.graphics.context_instructions import Color

import numpy as np
from mgen import rotation_from_angle_and_plane

from math import log

from modules.planet import Planet, HAS_CHARGE, ROUND_SPACE, ACC_MARKERS, N_DIMENSION


class Space(Widget):
    #   Not working
    # effects: ew.HorizontalBlurEffect(size=0.1), ew.VerticalBlurEffect(size=0.1), ew.FXAAEffect()
    
    __slots__ = 'num_dimension', 'objects', 'tails', \
                'touch_start', 'touch_end', 'touch_planet', \
                'show_acc', 'show_vel', \
                'grav_const', 'inform_speed', \
                '_keyboard_modifiers'


    def __init__(self, **kwargs):
        super(Space, self).__init__(**kwargs)

        # self.effects = [HorizontalBlurEffect(size=0.1),]
        self._keyboard_modifiers = []
        if HAS_CHARGE:
            self.def_charge = 1.
        if ACC_MARKERS:
            self.show_markers = False
            self.markers = []
            

        self.num_dimension = N_DIMENSION
        self.objects = []
        self.objects_to_append = []

        self.tails = []

        self.touch_start = None
        self.touch_end = None
        self.touch_planet = None

        self.show_acc = False
        self.show_vel = False

        self.grav_const = 1000.
        # self.inform_speed = 100. # not used

        self.marker_point = Planet(pos=list(self.to_num_dimension((0., 0.))),
                                   mass=1, 
                                   num_dimension=self.num_dimension,
                                   charge=1.)


    def to_num_dimension(self, arr, up=0):
        num = self.num_dimension + up
        if isinstance(arr, (list, tuple)):
            new_arr = np.array(arr)
        elif isinstance(arr, np.ndarray):
            new_arr = arr.copy()
        else:
            new_arr = np.array([0.]*(self.num_dimension - len(arr)))

        new_arr.resize(num)
        return new_arr
        '''
        return np.array(list(arr) + [0.]*(self.num_dimension - len(arr))) \
               if len(arr) < self.num_dimension \
               else arr
        '''

    def sign_log(self, x, m = 10.):
        '''Normalise vector(np array) by log of it length

        '''
        norm = np.linalg.norm(x)
        return m * log(norm + 1) / (norm + 1) * x

    '''
    def rect_size(self, mass, m=10.):
        return ((mass ** .5) * m,) * 2
    '''

    def update(self, dt, t):

        # Append objects
        for p in self.objects_to_append:
            self.objects.append(p)
        self.objects_to_append.clear()

        # Update physics
        while True:
            for obj in self.objects:
                obj.update_acc(dt, self)
                if obj.collided:
                    self.collide(obj, obj.collided, t)
                    break
            else:
                break
        for obj in self.objects:
            obj.update_vel(dt)
        for obj in self.objects:
            obj.update_pos(dt)

        # Sort by z coordinate for draw nerest last
        if self.num_dimension > 2:
            self.objects.sort(key=lambda x:x.pos[2])

        # Drawing
        self.canvas.clear()
        with self.canvas:
            # Background
            cx, cy = self.center_x, self.center_y
            w, h = self.width, self.height
            if ROUND_SPACE:
                r = min(w, h) / 2 - 10
                Color(1, 1, 1, 1)
                Line(circle=(cx, cy, r))

            
            if ACC_MARKERS and self.show_markers:
                step = 80
                point = self.marker_point
                for x in range(round(cx - step*(cx//step)), w+1, step):
                    for y in range(round(cy - step*(cy//step)), h+1, step):
                        if (x-cx)**2 + (y-cy)**2 > r**2:
                            continue
                        point.pos[:2] = x, y
                        point.update_acc(1., self)
                        pos = x, y
                        acc = self.sign_log(point.acc, m = 5.)

                        px, py = pos[:2]
                        dx, dy = acc[:2]

                        if HAS_CHARGE:
                            Color(1, 0, 0, 1)
                            Line(points=(px, py, px-dx/2., py-dy/2.))
                            Color(0, 0, 1, 1)
                            Line(points=(px, py, px+dx/2., py+dy/2.))
                        else:
                            Color(0, 0, 1, 1)
                            Line(points=(px, py, px+dx, py+dy))


            # Touch white line
            if self.touch_planet:
                self.touch_planet.vel = self.to_num_dimension([0.])
                self.touch_planet.pos = self.to_num_dimension(self.touch_end)
                Color(1, 1, 1, .6)
                Line(points=[self.touch_start[0], self.touch_start[1], 
                             self.touch_end[0], self.touch_end[1]],
                     width=2)

            # Space tails
            for tail in self.tails:
                if tail[1] + 2 == tail[2]:
                    self.tails.remove(tail)
                    continue

                coords = list(tail[0])

                Color(1, .0, .0, .3)
                Line(points=coords,
                     width=2,
                     joint='round')

                Color(1., .0, .5, .3)
                len_coords1 = (tail[2] * 2 // 3) // 2 * 2
                if len_coords1 - tail[1] > 2:
                    if len_coords1 < 2:
                        len_coords1 = 2
                    Line(points=coords[:len_coords1 - tail[1]],
                         width=tail[3] / 2.,
                         joint='round')
                
                Color(1., .0, .6, .5)
                len_coords1 = (tail[2] // 3) // 2 * 2
                if len_coords1 - tail[1] > 2:
                    if len_coords1 < 2:
                        len_coords1 = 2
                    Line(points=coords[:len_coords1 - tail[1]],
                         width=tail[3],
                         joint='round')

                # print(f'tail = {tail}')
                tail[0].pop()
                tail[0].pop()
                tail[1] += 2

            # Planets
            for obj in self.objects:
                # Tail
                # TODO new Tail
                coords = list(obj.tail_coords)
                # Color(1, 1, 1, 1)
                # Point(points=coords)
                len_coords = len(coords)
                if len_coords < 2:
                    continue
                
                Color(1, 0, 0, .3)
                Line(points=coords,
                     width=2,
                     joint='round')
                
                Color(1, 0, 0.5, .3)
                len_coords1 = (len_coords * 2 // 3) // 2 * 2 + obj.tail_back
                if len_coords1 < 2:
                    len_coords1 = 2
                Line(points=coords[:len_coords1],
                     width=obj.round_size() / 2.,
                     joint='round')
                
                Color(1, 0, .6, .5)
                len_coords1 = (len_coords // 3) // 2 * 2 + obj.tail_back
                if len_coords1 < 2:
                    len_coords1 = 2
                Line(points=coords[:len_coords1],
                     width=obj.round_size(),
                     joint='round')


            for obj in self.objects:
                _, sum_pos1, _, _ = self.sum_attrib()
                pos1 = obj.pos
                dist_to_viewer = 1 # 0 to 1
                if len(pos1) > 2:
                    back_dist = 100.
                    dist_to_viewer = (pos1[2] - sum_pos1[2] + back_dist) / back_dist / 2.
                    if dist_to_viewer > 1.:
                        dist_to_viewer = 1.
                    if dist_to_viewer < 0.:
                        dist_to_viewer = 0.
                
                r_size = obj.round_size()
                if HAS_CHARGE:
                    charge = obj.data.get('charge', 0.)
                    # print(f'mass={r_size}, charge={charge}')
                    colors = [0.,
                              1. * dist_to_viewer,
                              0.,
                              0.9]
                    if charge > 1.:
                        colors = [1.,
                                  1. * dist_to_viewer / charge,
                                  0.,
                                  0.9]
                    elif charge < -1.:
                        colors = [.0,
                                  1. * dist_to_viewer / -charge,
                                  1.,
                                  0.9]
                    elif charge > 0.:
                        colors = [charge,
                                  1. * dist_to_viewer,
                                  0.,
                                  0.9]
                    elif charge < 0.:
                        colors = [0.,
                                  1. * dist_to_viewer,
                                  -charge,
                                  0.9]
                    Color(*colors)
                else:
                    Color(1 * dist_to_viewer,
                          1 * dist_to_viewer,
                          0.,
                          0.9)
                '''
                '''
                # (1. - dist_to_viewer) * 2. if dist_to_viewer < .5 else
                Ellipse(pos=[pos1[0] - r_size, pos1[1] - r_size], size=[r_size*2., r_size*2.])

            sum_pos = self.to_num_dimension([0.])
            sum_vel = self.to_num_dimension([0.])
            sum_acc = self.to_num_dimension([0.])
            sum_mass = 0.
            # Debug
            if self.show_vel or self.show_acc:
                for obj in self.objects:
                    sum_acc += obj.acc * obj.mass # must be == 0
                    sum_vel += obj.vel * obj.mass
                    sum_pos += obj.pos * obj.mass
                    sum_mass += obj.mass

                    if self.show_vel:
                        Color(0, 0, 1, 1)
                        # norm_vel = self.sign_log(obj.vel)
                        norm_vel = obj.vel
                        Line(points=(obj.pos[0],               obj.pos[1],
                                     obj.pos[0] + norm_vel[0], obj.pos[1] + norm_vel[1]))
                    if self.show_acc:
                        Color(0, 1, 0, 1)
                        # norm_acc = self.sign_log(obj.acc)
                        norm_acc = obj.acc
                        Line(points=(obj.pos[0],               obj.pos[1],
                                     obj.pos[0] + norm_acc[0], obj.pos[1] + norm_acc[1]))

                sum_pos = sum_pos / sum_mass if sum_mass != 0. else self.to_num_dimension([0.])
                sum_vel = sum_vel / sum_mass if sum_mass != 0. else self.to_num_dimension([0.])
                sum_acc = sum_acc / sum_mass if sum_mass != 0. else self.to_num_dimension([0.])

                # Sum position mark
                mark_size = 10.
                Color(1, 0, 0, 1)
                # print(f'sum_pos = {sum_pos}\nsum_vel = {sum_vel}\nsum_acc = {sum_acc}\n')
                Line(points=(sum_pos[0], sum_pos[1] - mark_size,
                             sum_pos[0], sum_pos[1] + mark_size))
                Line(points=(sum_pos[0] - mark_size, sum_pos[1],
                             sum_pos[0] + mark_size, sum_pos[1]))
                # Sum vel
                Color(0, 0, 1, 1)
                Line(points=(sum_pos[0],              sum_pos[1], 
                             sum_pos[0] + sum_vel[0], sum_pos[1] + sum_vel[1]))
                # Sum acc
                Color(0, 0, 1, 1)
                Line(points=(sum_pos[0],              sum_pos[1],
                             sum_pos[0] + sum_acc[0], sum_pos[1] + sum_acc[1]))

    def set_vel(self, end_vel):
        sum_vel = self.to_num_dimension([0.])
        sum_mass = 0.
        for obj in self.objects:
            sum_vel += obj.vel * obj.mass
            sum_mass += obj.mass

        sum_vel = sum_vel if sum_mass != 0. else self.to_num_dimension([0.])

        dvel = self.to_num_dimension(end_vel) * sum_mass - sum_vel

        '''
        print('')
        print(sum_vel)
        print(dvel)
        '''

        for obj in self.objects:
            obj.vel = obj.vel + dvel / sum_mass

    def set_pos(self, end_pos):
        num = self.num_dimension

        sum_pos = self.to_num_dimension([0.])
        sum_mass = 0.
        for obj in self.objects:
            sum_pos += obj.pos * obj.mass
            sum_mass += obj.mass

        sum_pos = sum_pos / sum_mass if sum_mass != 0. else self.to_num_dimension([0.])

        dpos = self.to_num_dimension(end_pos) - sum_pos

        for obj in self.objects:
            matrix_translate = np.eye(num + 1)
            matrix_translate[0:num, num:num+1] = np.reshape(dpos, (num, 1))
            obj.translate(matrix_translate)
            # Old
            # obj.pos = obj.pos + dpos

    def rotate(self, angle, vector1, vector2, rot_point):
        tnd = self.to_num_dimension

        num = self.num_dimension + 1

        rot_pos = tnd(rot_point).reshape(num - 1, 1)

        matrix_translate = np.eye(num)
        matrix_translate[0:num-1, num-1:num] = rot_pos * -1.

        matrix_rot = rotation_from_angle_and_plane(angle,
                                                   tnd(vector1, up=1),
                                                   tnd(vector2, up=1))

        matrix_from_origin = matrix_rot.copy()

        matrix_rot = np.dot(matrix_rot, matrix_translate)

        matrix_translate[0:num-1, num-1:num] = rot_pos

        matrix_rot = np.dot(matrix_translate, matrix_rot)

        # print(matrix_rot)

        for obj in self.objects:
            obj.rotate(matrix_rot, matrix_from_origin)

    def sum_attrib(self):
        sum_pos = self.to_num_dimension([0.])
        sum_vel = self.to_num_dimension([0.])
        sum_acc = self.to_num_dimension([0.])
        sum_mass = 0.
        for obj in self.objects:
            sum_acc += obj.acc * obj.mass # must be == 0
            sum_vel += obj.vel * obj.mass
            sum_pos += obj.pos * obj.mass
            sum_mass += obj.mass

        sum_pos = sum_pos / sum_mass if sum_mass != 0. else self.to_num_dimension([0.])
        sum_vel = sum_vel / sum_mass if sum_mass != 0. else self.to_num_dimension([0.])
        sum_acc = sum_acc / sum_mass if sum_mass != 0. else self.to_num_dimension([0.])
        
        return sum_mass, sum_pos, sum_vel, sum_acc

    def collide(self, p1, p2, t):
        assert isinstance(p2, Planet)
        
        pos = list((p1.pos * p1.mass + p2.pos * p2.mass) / (p1.mass + p2.mass))
        vel = list((p1.vel * p1.mass + p2.vel * p2.mass) / (p1.mass + p2.mass))
        acc = list(np.array([0.] * self.num_dimension))
        mass = p1.mass + p2.mass
        self.tails.append([p1.tail_coords.copy(), p1.tail_back, len(p1.tail_coords) + p1.tail_back, p1.round_size()])
        self.tails.append([p2.tail_coords.copy(), p2.tail_back, len(p2.tail_coords) + p2.tail_back, p2.round_size()])
        p3 = Planet(pos=pos,
                    vel=vel,
                    acc=acc,
                    mass=mass,
                    num_dimension=self.num_dimension,
                    tail_back=max(len(p1.tail_coords) + p1.tail_back,
                                  len(p2.tail_coords) + p2.tail_back))
        if HAS_CHARGE:
            charge1 = p1.data.get('charge', None)
            charge2 = p2.data.get('charge', None)
            if charge1 is not None and charge2 is not None:
                charge3 = charge1 + charge2
                p3.data.update({'charge':charge3})

        self.pop(p1)
        self.pop(p2)
        self.objects.append(p3)
        # print(p3.data)

    # Unsafe for async
    def pop(self, p):
        for i in range(len(self.objects)):
            if p is self.objects[i]:
                self.objects.pop(i)
                break

    # Safe for async
    def append(self, p):
        self.objects_to_append.append(p)

    def on_touch_down(self, touch):
        self.touch_start = touch.pos
        self.touch_end = touch.pos

        if HAS_CHARGE:
            charge = self.def_charge
            '''
            if 'button' in touch.profile:
                if touch.button == 'right':
                    charge = -1.
            '''
            # print(f'keyboard_modifiers {self._keyboard_modifiers}')
            if 'ctrl' in self._keyboard_modifiers:
                charge *= -1.
                # print(f'charge {charge}')
            self.touch_planet = Planet(pos=list(self.to_num_dimension(touch.pos)),
                                       mass=1, 
                                       num_dimension=self.num_dimension,
                                       charge=charge)
        else:
            self.touch_planet = Planet(pos=list(self.to_num_dimension(touch.pos)),
                                           mass=1, 
                                           num_dimension=self.num_dimension)

        self.append(self.touch_planet)
        
        return False

    def on_touch_move(self, touch):
        if self.touch_planet:
            self.touch_end = touch.pos
            self.touch_planet.pos = np.array(self.to_num_dimension(self.touch_end))
            return True
        return False

    def on_touch_up(self, touch):
        if self.touch_planet:
            self.touch_planet.vel = np.array(self.to_num_dimension(self.touch_end)) - \
                                    np.array(self.to_num_dimension(self.touch_start))
            self.touch_planet = None
            return True
        return False

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self._keyboard_modifiers = modifiers
        # print(f'keydown {self._keyboard_modifiers}')

        # In case custom_acc5 use
        if HAS_CHARGE:
            if 'a' == keycode[1]: #or 274 == keycode[0]:
                self.def_charge *= -1.
        if 'f' == keycode[1]:
            self.show_markers = not self.show_markers
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        key = keycode[1]
        if 'ctrl' in key:
            key = 'ctrl'
        if key in self._keyboard_modifiers:
            self._keyboard_modifiers.remove(key)
        # print(f'keyup {self._keyboard_modifiers}')
        return True
