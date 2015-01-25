
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import ctypes
import os.path
import argparse

ap = argparse.ArgumentParser(description='Put your TODO list on desktop')
ap.add_argument('-freemind', help='Get TODO list from a Freemind file', dest='source_mm_fpath', default='./test/todo.mm')
ap.add_argument('-input_image', help='Input image file', dest='in_img_fpath', default='./test/in.jpg');
ap.add_argument('-output_image', help='Output image file', dest='out_img_fpath', default='./test/out.jpg');
cfg = ap.parse_args()

cfg.desktop_width = 1920
cfg.desktop_height = 1080

cfg.to_desktop_left_pct = 20
cfg.to_desktop_right_pct = 20
cfg.to_desktop_top_pct = 10
cfg.to_desktop_bot_pct = 10

cfg.line_color = (255, 255, 255)
cfg.line_width = 2

cfg.to_quad_left_pixel = 20
cfg.to_quad_top_pixel = 20

cfg.text_color = dict()
cfg.text_color[1] = (0, 0, 0)
cfg.text_color[2] = (0, 0, 0)
cfg.text_color[3] = (0, 0, 0)
cfg.text_color[4] = (0, 0, 0)
cfg.has_text_outline = dict()
cfg.has_text_outline[1] = True
cfg.has_text_outline[2] = True
cfg.has_text_outline[3] = True
cfg.has_text_outline[4] = True
cfg.text_outline_color = dict()
cfg.text_outline_color[1] = (255, 255, 255)
cfg.text_outline_color[2] = (255, 255, 255)
cfg.text_outline_color[3] = (255, 255, 255)
cfg.text_outline_color[4] = (255, 255, 255)
cfg.text_outline_width = 2

cfg.text_font = './FreeSerif.ttf'
cfg.text_size = 30
cfg.line_space = 10

cfg.line_height = cfg.text_size + cfg.line_space

class bg_img_t:
    def __init__(self, cfg):
        '' # {{{
        assert os.path.isfile(cfg.in_img_fpath), 'Input image file (%s) is not found' % cfg.in_img_fpath
        self.img = Image.open(cfg.in_img_fpath)

        #-------------------------------------------------------
        # crop and resize the image: method fill
        (img_width, img_height) = self.img.size
        if (img_width < cfg.desktop_width) or (img_height < cfg.desktop_height):
            print 'Warning: input image\'s width/height (%d,%d) is less than desktop resolution width/height (%d,%d)' % (img_width, img_height, cfg.desktop_width, cfg.desktop_height)

        current_ratio = float(img_width) / float(img_height)
        target_ratio = float(cfg.desktop_width) / float(cfg.desktop_height)

        if (current_ratio > target_ratio):
            # crop the width
            new_img_width = target_ratio * img_height
            new_img_height = img_height
            delta_width = (img_width - new_img_width) / 2.0
            delta_height = 0
        elif (current_ratio < target_ratio):
            # crop the height
            new_img_width = img_width
            new_img_height = img_width / target_ratio
            delta_width = 0
            delta_height = (img_height - new_img_height) / 2.0
        else:
            # no crop needed
            new_img_width = img_width
            new_img_height = img_height
            delta_width = 0
            delta_height = 0

        self.img = self.img.crop((int(delta_width), int(delta_height), int(new_img_width + delta_width), int(new_img_height + delta_height)))
        self.img = self.img.resize((cfg.desktop_width, cfg.desktop_height), Image.ANTIALIAS)


        new_img_width = cfg.desktop_width * img_height / cfg.desktop_height
        if (new_img_width < cfg.desktop_width):
            new_img_heigth = cfg.desktop_height * img_width / cfg.desktop_width
            assert new_img_height >= cfg.desktop_height

        #-------------------------------------------------------
        # define text region coordinates
        self.main_llx = int(cfg.desktop_width * cfg.to_desktop_left_pct / 100.0)
        self.main_lly = int(cfg.desktop_height * (100.0 - cfg.to_desktop_bot_pct) / 100.0)
        self.main_urx = int(cfg.desktop_width * (100.0 - cfg.to_desktop_right_pct) / 100.0)
        self.main_ury = int(cfg.desktop_height * cfg.to_desktop_top_pct / 100.0)
        self.center_x = int(cfg.desktop_width * 0.5)
        self.center_y = int(cfg.desktop_height * 0.5)

        self.quad_x = dict()
        self.quad_y = dict()

        self.quad_x[2] = self.main_llx
        self.quad_y[2] = self.main_ury

        self.quad_x[1] = self.center_x
        self.quad_y[1] = self.quad_y[2]

        self.quad_x[3] = self.quad_x[2]
        self.quad_y[3] = self.center_y

        self.quad_x[4] = self.quad_x[1]
        self.quad_y[4] = self.quad_y[3]

        #-------------------------------------------------------
        # initialize quadrant list
        self.dt_quad = dict()
        for quadrant in range(1, 5):
            ls_item = list()
            self.dt_quad[quadrant] = ls_item

        self.font = ImageFont.truetype(cfg.text_font, cfg.text_size)
        # }}}

    def add_item(self, text, quadrant):
        self.dt_quad[quadrant].append(text)

    def draw(self):
        #-------------------------------------------------------
        # draw lines
        self.draw = ImageDraw.Draw(self.img)
        self.draw.line([self.main_llx, self.center_y, self.main_urx, self.center_y], fill=cfg.line_color, width=int(cfg.line_width+1.0/2.0)) # horizontal
        self.draw.line([self.center_x, self.main_ury, self.center_x, self.main_lly], fill=cfg.line_color, width=cfg.line_width) # vertical

        #-------------------------------------------------------
        # draw text with outline
        for quadrant in range(1,5):
            for (line, text) in enumerate(self.dt_quad[quadrant]):
                x = self.quad_x[quadrant] + cfg.to_quad_left_pixel
                y = self.quad_y[quadrant] + cfg.to_quad_top_pixel + line * cfg.line_height
                if (cfg.has_text_outline[quadrant]):
                    self.draw.text((x-cfg.text_outline_width, y), text, cfg.text_outline_color[quadrant], font=self.font)
                    self.draw.text((x, y-cfg.text_outline_width), text, cfg.text_outline_color[quadrant], font=self.font)
                    self.draw.text((x+cfg.text_outline_width, y), text, cfg.text_outline_color[quadrant], font=self.font)
                    self.draw.text((x, y+cfg.text_outline_width), text, cfg.text_outline_color[quadrant], font=self.font)
                self.draw.text((x, y), text, cfg.text_color[quadrant], font=self.font)

    def write(self):
        'write to img_fpath and update windows desktop background with it'
        self.img.save(cfg.out_img_fpath)
        ctypes.windll.user32.SystemParametersInfoA(20, 0, cfg.out_img_fpath, 0)

class todo_item_t:
    def __init__(self, text):
        assert len(text) > 0, 'text is empty'
        self.text = text
        self.status = 'todo'

    def change_text(self, new_text):
        len(new_text) > 0, 'text is empty'
        self.text = new_text

    def change_status(self, new_status):
        assert (new_status in ['todo', 'done', 'wait', 'drop']), 'status (%s) is not defined' % new_status
        self.status = new_status

    def todo(self):
        self.change_status('todo')

    def done(self):
        self.change_status('done')

    def wait(self):
        self.change_status('wait')

    def drop(self):
        self.change_status('drop')


if __name__ == '__main__':
    bg = bg_img_t(cfg)

    if (len(cfg.source_mm_fpath) > 0 ):
        import sys
        sys.path.append('../freemind_parser')
        import freemind_parser

        mm = freemind_parser.mm_file_t(cfg.source_mm_fpath)
        dt_quad_node = dict()
        dt_quad_node[1] = mm.root.find_sub_by_text('1*')
        dt_quad_node[2] = mm.root.find_sub_by_text('2*')
        dt_quad_node[3] = mm.root.find_sub_by_text('3*')
        dt_quad_node[4] = mm.root.find_sub_by_text('4*')

        for quad in range(1,5):
            for node in dt_quad_node[quad].ls_sub:
                bg.add_item(node.to_print(), quad)

    bg.draw()
    bg.write()
    print 'TODO LIST AS DESKTOP IS DONE'
