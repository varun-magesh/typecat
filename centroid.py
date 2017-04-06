import font2img as f2i
from PIL import ImageFont, ImageOps
from font import Font
from math import sin, cos, pi, sqrt

DELTA_RAD = pi/18


def bound(loc, size):
    if(loc[0] >= size[0]):
        loc[0] = size[0] - 1
    if(loc[0] <= 0):
        loc[0] = 0
    if(loc[1] >= size[1]):
        loc[1] = size[1] - 1
    if(loc[1] <= 0):
        loc[1] = 0


def shortest_line(point, imgpx, max_len=20):
    x = point[0]
    y = point[1]
    # it's unlikely a segment will be more than half the size of the img
    shortest_len = max_len
    shortest_pts = ((0, 0), (0, 0))
    for d in range(int(pi / DELTA_RAD)):
        rad = d * DELTA_RAD
        # using sin and cosine will ensure we move exactly 1 pixel each
        # step
        step = (cos(rad), sin(rad))
        nstep = (-cos(rad), -sin(rad))
        # upper is the top point of the line
        upper_loc = [x, y]
        # and lower, naturally, is the bottom part
        lower_loc = [x, y]
        curr_len = 0
        while curr_len < shortest_len:
            # go a little bit further along our angle
            if imgpx[int(upper_loc[0]), int(upper_loc[1])] == 0:
                upper_loc = [upper_loc[0] + step[0],
                             upper_loc[1] + step[1]]
            if imgpx[int(lower_loc[0]), int(lower_loc[1])] == 0:
                lower_loc = [lower_loc[0] + nstep[0],
                             lower_loc[1] + nstep[1]]
            # bound the vars
            bound(upper_loc, img2.size)
            bound(lower_loc, img2.size)
            # calculate length
            curr_len = sqrt((upper_loc[0] - lower_loc[0])**2 +
                            (upper_loc[1] - lower_loc[1]) ** 2)
            # if both are white and we're less than the shortest length
            # stop and move on
            if((imgpx[int(lower_loc[0]), int(lower_loc[1])] == 1 and
                    imgpx[int(upper_loc[0]),
                          int(upper_loc[1])] == 1)) and\
                    curr_len < shortest_len:
                shortest_len = curr_len
                shortest_pts = (tuple(lower_loc), tuple(upper_loc))
    return shortest_len, shortest_pts
font = ImageFont.truetype("/home/varun/.fonts/LibreBaskerville-Regular.ttf", 70)
for c in list(Font.ALPHABET + Font.ALPHABET.upper()):
    img, draw = f2i.single_pil(c, font)
    dr = img.copy()
    bbox = img.getbbox()
    img2 = ImageOps.expand(img, border=1, fill=1)
    imgpx = img2.load()
    i = 0
    for x in range(bbox[0], bbox[2]):
        for y in range(bbox[1], bbox[3]):
            # Check if we've already done the pixel and that the pixel is even a
            # fille in one
            # if img.getpixel((x, y)) == 1 or imgpx[x, y] == 1:
            if img.getpixel((x, y)) == 1 or imgpx[x, y] == 1:
                continue
            shortest_len, shortest_pts = shortest_line((x, y),
                                                       imgpx, img.size[0]/2)
            # Color in center of mass of shortest line
            com = (int((shortest_pts[0][0]+shortest_pts[1][0])/2),
                   int((shortest_pts[0][1]+shortest_pts[1][1])/2))
            dr.putpixel(com, 1)
            ell = ((shortest_pts[0][0]-shortest_len,
                    shortest_pts[0][1]-shortest_len),
                   (shortest_pts[0][0]+shortest_len,
                    shortest_pts[0][1]+shortest_len))
            draw.ellipse(ell, fill=1)
        dr.save("imgs/{}hull.png".format(c), "PNG")
