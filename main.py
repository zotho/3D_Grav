#!/usr/bin/env python3

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config

# Temp
from kivy.graphics.vertex_instructions import (Line, Ellipse)
from kivy.graphics.context_instructions import Color

from numpy import array2string, pi

from functools import partial
from importlib import import_module

__author__ = "Sviatoslav Alexeev"
__email__ = "svjatoslavalekseef2@gmail.com"
__status__ = "Developed"

'''For more information see:
www.github.com/zotho
'''

from modules.space import Space
from modules.fps import Fps
from modules.lineprinter import LinePrinter

ANGLE = pi/18.

'''Here window start create
For less wait to build
'''
from kivy.core.window import Window
Window.borderless = True
Window.hide()

class GravApp(App):
    def __init__(self, *args, filename=None, **kwargs):
        self.filename = filename
        super(GravApp, self).__init__(*args, **kwargs)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down,
                            on_key_up=self._on_keyboard_up)
        self._keyboard_modifiers = []

        # work aroung bug [1]
        self.y = 0
        '''
                                   'mass={mass} '
                                   'pos={pos} '
                                   'vel={vel} '
                                   'acc={acc} '
        '''
        self.printer = LinePrinter('[{level:<7}] '
                                   '[{sublevel:<12}] '
                                   '[{fps:>5.2f} fps] '
                                   '[{speed:>4.1f}x speed] '
                                   'npoints=[{points}]'
                                   '{debug}'
                                   '{key_form}',
                                   level='INFO',
                                   sublevel='Log',
                                   fps=1.,
                                   speed=1.,
                                   mass=0.,
                                   pos=0.,
                                   vel=0.,
                                   acc=0.,
                                   points=0,
                                   debug='',
                                   key='',
                                   key_form='',
                                   key_form_default=' key=[{key}]')

        self.last_rot = 0., (0., 0., 1.), (0., 1., 0.), Window.center

        self.nparray2string = partial(array2string,
                                      separator=',',
                                      formatter={'float_kind':lambda x: f"{x:6.2f}"})

    # work aroung bug [1] https://github.com/kivy/kivy/issues/5359
    def to_window(self, x, y, initial=True, relative=False):
        return x, y

    def build(self, *args, **kwargs):
        self.draw_fps = True
        self.fps = Fps()

        self.time = 0.
        self.last_time = 0.
        self.time_mult = 1.
        self.time_mult_pause = None

        Clock.schedule_interval(self.update, 0)
        self.event_once = None

        self.root = Space()

        Config.read('config.ini')

        # For my window header
        # dx, dy = -1, -32
        dx, dy = 0, 0

        # if Config.get('graphics', 'position') != 'auto':
        	# Window.left = Config.getint('graphics', 'left') + dx
        	# Window.top = Config.getint('graphics', 'top') + dy
        	# Window.size = (Config.getint('graphics', 'width'), Config.getint('graphics', 'height'),)
            # Window.left, Window.top, Window.size = Config.getint('graphics', 'left') + dx, \
            #                                        Config.getint('graphics', 'top') + dy, \
            #                                        (Config.getint('graphics', 'width'), \
            #                                         Config.getint('graphics', 'height'),)
        if Config.getboolean('graphics', 'maximize'):
            Window.maximize()
        
        Window.show()

        self.root.bind(on_touch_down=self.on_touch_down,
                       on_touch_move=self.on_touch_move,
                       on_touch_up=self.on_touch_up)
        
        if self.filename:
            Clock.schedule_once(partial(import_module(self.filename).set_state, self.root, self), 1)
        
        return self.root

    def update(self, dt):
        # print(f'left={Window.left}, top={Window.top}, width={Window.width}, height={Window.height}')
        # print(self._keyboard_modifiers)
        # self.dt = dt
        self.time += dt * self.time_mult

        if abs(self.time - self.last_time) >= abs(self.time_mult):
            self.last_time = self.time
            mass, pos, vel, acc = self.root.sum_attrib()
            self.printer.print(fps=Clock.get_fps(),
                               mass=mass,
                               pos=self.nparray2string(pos),
                               vel=self.nparray2string(vel),
                               acc=self.nparray2string(acc),
                               points=len(self.root.objects))

        _, pos, _, _ = self.root.sum_attrib()
        # self.root.rotate(-pi/180., (0., 1., 0), (0., 0., 1.))
        # self.root.rotate(dt * self.time_mult * -ANGLE, (1., 0., 0), (0., 0., 1.), pos)

        self.root.update(dt * self.time_mult, self.time)

        if self.draw_fps:
            self.fps.update(dt)
            self.fps.draw(self.root)

    def on_touch_down(self, entity, touch):
        if 'shift' in self._keyboard_modifiers:
            self.last_rot = 0., (0., 0., 1.), (0., 1., 0.), Window.center
            return True
        return False

    def on_touch_move(self, entity, touch):
        if 'shift' in self._keyboard_modifiers:
            if 'pos' in touch.profile:
                # print()
                # print(f'dpos={touch.dpos}')
                dpos = tuple(map(lambda x:x[1]-x[0], zip(touch.opos,touch.pos)))
                length = sum(map(lambda x:x**2, dpos))**.5
                if length == 0:
                    return True
                ndpos = tuple(map(lambda x:x/length+0.01, dpos)) # (dx, dy)
                # Rotation -pi/2
                '''
                rot = ((0., -1.),   
                       (1.,  0.),)
                # ((0., dx), (-1., dy))
                x = ((0., -1.), (dx, dy))
                y = (0., dx)
                # (((0., -1.), (dx, dy)), ((1., 0.), (dx, dy)))
                # (((0.0, 0.0), (-1.0, 1.0)), ((1.0, 0.0), (0.0, 1.0)))

                # print(f'ndpos={tuple(ndpos)}')
                xx = tuple(zip(rot, ((ndpos,)*2)))
                # print(f'xx={xx}')
                yy = tuple(map(lambda x: tuple(zip(*x)), xx))
                # print(f'yy={yy}')
                axis = tuple(map(lambda y: sum(map(lambda z: z[0]*z[1], y)), yy))

                # _, pos, _, _ = self.root.sum_attrib()
                '''
                last_rot = (-self.last_rot[0],) + self.last_rot[1:]
                # print(f'last_rot={last_rot}')
                # print(f'self.last_rot={self.last_rot}')
                self.root.rotate(*last_rot)
                self.last_rot = (ANGLE/40.*length*ndpos[1]/abs(ndpos[1]), (0., 0., 1.), ndpos, Window.center)
                self.root.rotate(*self.last_rot)
                with self.root.canvas:
                    Color(1, 1, 1, .3)
                    Line(points=[touch.opos[0], touch.opos[1],
                                 touch.pos[0], touch.pos[1]],
                         width=2)
            return True
        return False

    def on_touch_up(self, entity, touch):
        if 'shift' in self._keyboard_modifiers:
            self.last_rot = 0., (0., 0., 1.), (0., 1., 0.), Window.center
            return True
        return False

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_up(self, keyboard, keycode):
        '''
        self.event_once.get_callback()()
        self.event_once.cancel()
        '''

        if keycode[1] in self._keyboard_modifiers:
            self._keyboard_modifiers.remove(keycode[1])
            if self.event_once and self.event_once.is_triggered:
                self.event_once.get_callback()()
                self.event_once.cancel()

        if self._keyboard_modifiers:
            self.event_once = Clock.create_trigger(lambda *args: self.printer.print(key_form=self.printer.data['key_form_default'], key='+'.join(self._keyboard_modifiers).upper()), 1)
            '''
            self.printer.print(key_form=self.printer.data['key_form_default'],
                               key='+'.join(self._keyboard_modifiers).upper())
            '''
        else:
            self.event_once = Clock.create_trigger(lambda *args: self.printer.print(key_form=''), 1)
        self.event_once()
        return self.root._on_keyboard_up(keyboard, keycode)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        '''
        print(keycode)
        print(text)
        print(modifiers)
        '''

        if self.event_once and self.event_once.is_triggered:
            # self.event_once.get_callback()()
            self.event_once.cancel()
        
        # format_string = self.printer.format_string
        # data = self.printer.data
        def to_prev(*args, **kwargs):
            '''
            print(f'callback for {modifiers}')
            '''
            #self.printer.format_string = str(format_string)
            #self.printer.data = dict(data)
            '''
            if self._keyboard_modifiers and not kwargs.get('recur'):
                # print(self._keyboard_modifiers)
                self.event_once = Clock.create_trigger(partial(to_prev, recur=True), 1)
                self.printer.print(format_string + ' key=[{key}]',
                                   key='+'.join(self._keyboard_modifiers).upper())
                self.event_once()
            else:
                self.printer.print()
            '''
            self.printer.print(key_form='')

        # self.event_once = Clock.create_trigger(to_prev, 1)
        self.event_once = Clock.create_trigger(lambda *args: self.printer.print(key_form=''), 1)
        if keycode[1] not in modifiers:
            self.event_once()
        text = modifiers + ([keycode[1],] if keycode[1] not in modifiers else [])
        self.printer.print(key='+'.join(text).upper(),
                           key_form=self.printer.data['key_form_default'])

        self._keyboard_modifiers = modifiers

        if 'shift' in modifiers:
            # Rotate
            if 'left' == keycode[1] or 276 == keycode[0]:
                _, pos, _, _ = self.root.sum_attrib()
                self.root.rotate(-ANGLE, (1., 0., 0), (0., 0., 1.), pos)
            if 'right' == keycode[1] or 275 == keycode[0]:
                _, pos, _, _ = self.root.sum_attrib()
                self.root.rotate(ANGLE, (1., 0., 0), (0., 0., 1.), pos)
            if 'down' == keycode[1] or 274 == keycode[0]:
                _, pos, _, _ = self.root.sum_attrib()
                self.root.rotate(ANGLE, (0., 1., 0), (0., 0., 1.), pos)
            if 'up' == keycode[1] or 273 == keycode[0]:
                _, pos, _, _ = self.root.sum_attrib()
                self.root.rotate(-ANGLE, (0., 1., 0), (0., 0., 1.), pos)
        elif not modifiers:            
            # Debug
            if 'd' == keycode[1] or 100 == keycode[0]:
                self.root.show_acc = not self.root.show_acc
                self.root.show_vel = not self.root.show_vel
                sublevels = ('Log', 'Debug')
                debug_format = ' mass={mass} pos={pos} vel={vel} acc={acc}'
                self.printer.print(sublevel=sublevels[self.root.show_acc],
                                   debug=debug_format if self.root.show_acc else '')

            # Speed
            if 'left' == keycode[1] or 276 == keycode[0]:
                self.time_mult -= 0.1
                self.printer.print(speed=self.time_mult)
                if self.time_mult_pause:
                    self.time_mult_pause = None
            if 'right' == keycode[1] or 275 == keycode[0]:
                self.time_mult += 0.1
                self.printer.print(speed=self.time_mult)
                if self.time_mult_pause:
                    self.time_mult_pause = None
            if 'spacebar' == keycode[1] or 32 == keycode[0]:
                if self.time_mult_pause:
                    self.time_mult, self.time_mult_pause = self.time_mult_pause, None
                else:
                    self.time_mult, self.time_mult_pause = 0., self.time_mult
            
            # Speed and Position to zero
            if 'down' == keycode[1] or 274 == keycode[0]:
                self.root.set_vel([0.])
                _, _, vel, _ = self.root.sum_attrib()
                self.printer.print(vel=self.nparray2string(vel))
            if 'up' == keycode[1] or 273 == keycode[0]:
                self.root.set_pos(Window.center)
                _, pos, _, _ = self.root.sum_attrib()
                self.printer.print(vel=self.nparray2string(pos))
        
        # Exit
        if  ('ctrl' in modifiers or not modifiers) and \
            ('escape' == keycode[1] or 27  == keycode[0] or \
             'q'      == keycode[1] or 113 == keycode[0] ):

            del self.printer

            Config.set('graphics', 'position', 'custom')
            Config.set('graphics', 'width', Window.width)
            Config.set('graphics', 'height', Window.height)
            Config.set('graphics', 'left', Window.left)
            Config.set('graphics', 'top', Window.top)
            Config.write()

            App.get_running_app().stop()

        return self.root._on_keyboard_down(keyboard, keycode, text, modifiers)

if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2:
        GravApp(filename=sys.argv[1]).run()
    else:
        GravApp().run()