# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""Display a live webcam feed. Require OpenCV (Python 2 only).
"""

try:
    import cv2
except Exception:
    raise ImportError("You need OpenCV for this example.")

import numpy as np
from vispy import app
from vispy import gloo

from moviepy.editor import VideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from vispy.gloo.util import _screenshot

vertex = """
    attribute vec2 position;
    attribute vec2 texcoord;
    varying vec2 v_texcoord;
    void main()
    {
        gl_Position = vec4(position, 0.0, 1.0);
        v_texcoord = texcoord;
    }
"""

fragment = """
    uniform sampler2D texture;
    uniform float u_clock;
    varying vec2 v_texcoord;

    void main()
    {
     vec2 i=v_texcoord;
       vec4 o=gl_FragColor;
        o = texture2D(texture,fract(2*vec2(1,.5)*i));
        o.r*=o.b;
        o=o.bgra;
        if (1==1){
        i.x+=.1*cos(u_clock);
        o.b+=length(.05/length(i-.5));
        i.y+=.1*sin(u_clock);
         o.r+=length(.05/length(i-.5));}
         //if (o.r>o.b+o.g)o.r*=1.5;
        // o*=o;
        gl_FragColor = o;
      
    }
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(800, 600), keys='interactive')
        self.program = gloo.Program(vertex, fragment, count=4)
        self.program['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
        self.program['texcoord'] = [(1, 1), (1, 0), (0, 1), (0, 0)]
        self.program['texture'] = np.zeros((480, 640, 3)).astype(np.uint8)
        self.program['u_clock'] = 0.0
        self.clock = 0
        width, height = self.physical_size
        gloo.set_viewport(0, 0, width, height)

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("There's no available camera.")
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.program['timer'] = self._timer
        self.show()

    def on_resize(self, event):
        width, height = event.physical_size
        gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        gloo.clear('black')
        _, im = self.cap.read()
        self.program['texture'][...] = im
        self.program.draw('triangle_strip')
        
    def on_timer(self, event):
        self.program['u_clock'] +=.1
        self.update()

    def animation(self, t):
        """ Added for animation with MoviePy """
        self.program['u_clock'] = t
        gloo.clear('black')
        _, im = self.cap.read()
        self.program['texture'][...] = im
        self.program.draw('triangle_strip')
        return  _screenshot((0, 0, self.size[0], self.size[1]))[:,:,:3]


def video():
  if 1:
    snd = AudioFileClip("space.mp3")
    clip = VideoClip(c.animation, duration=snd.duration/30.)

    clip = clip.set_audio(snd).set_duration(snd.duration/30.)
    clip.write_videofile('cam.mp4', fps=24)
        
c = Canvas()
app.run()
video()
c.cap.release()
