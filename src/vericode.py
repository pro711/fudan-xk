#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
Provides verificaton code recognition capabilities for the course chooser.
'''
import struct

class recognizer():
    width = 60
    height = 24

    def __init__(self, image):
        self.image = image
        self.start = 4374-3*60*24	    # image data start address
        self.serial_refer = [[0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0], #0
                            [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1], #1
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1], #2
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], #3
                            [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0], #4
                            [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0], #5
                            [0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0], #6
                            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0], #7
                            [0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0], #8
                            [0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0], #9
                            ]
        
    def get_pixel(self, (x, y)):
        '''Return the pixel of positon (x,y). Position starts from 0.'''
        pos = self.start + 180*(23-y) +3*x
        return self.image[pos:pos+2]
        
    def get_number(self):
        num=[]
        base_sample_pos = ([(7-i,i) for i in range(8)] + [(i,8+i) for i in range(8)])
        for i in range(0,4):
            # calculate start positon
            start_pos_x, start_pos_y = 14*i + 4, 4
            # calculate foreground color position
            fg_pos_x, fg_pos_y = start_pos_x + 4, start_pos_y
            # get foreground color
            fg_color = self.get_pixel((fg_pos_x, fg_pos_y))
            # get sample color
            sample_pos = [0]*len(base_sample_pos)
            for j in range(0,len(base_sample_pos)):
                sample_pos[j] = (base_sample_pos[j][0]+start_pos_x,
                                 base_sample_pos[j][1]+start_pos_y)
            sample_color = [self.get_pixel(p) for p in sample_pos]
            # generate binary serial
            bin_serial = [(1 if c==fg_color else 0) for c in sample_color]
##            print bin_serial
            for j in range(0,10):
                if (bin_serial == self.serial_refer[j]):
                    num.append(j)
                    break
        return num

	
if __name__ == '__main__':
	for i in range(1,12):
		fn = 'xuanke_pic/%02d' % i + ".bmp"
		data = open(fn, 'rb').read()
		reco = recognizer(data)
		print fn,'\n', reco.get_number()
##	raw_input()


