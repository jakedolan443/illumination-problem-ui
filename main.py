import tkinter as tk
import math
import shapely
from shapely.geometry import LineString, Point
from functools import wraps

k = 60
incr = 360/k
max_bounce = 12
#polygon = [[200,200], [300,100], [400, 200], [600, 200], [700, 200], [400, 700], [200, 200]]
#polygon = [[100, 100], [100, 400], [800, 400], [800, 100], [700, 100], [700, 350], [200, 350], [200, 100], [100, 100]]
 
#polygon = [[100,100], [120,100], [120,120], [140,120], [140,140], [180, 140], [180, 120], [200, 120], [200, 100], [220, 120], [240, 120], [240, 140], [220, 140], [220, 160], [200, 180], [200, 160], [180, 160], [160, 180], [160, 160], [140, 160], [120, 180], [120, 160], [100, 160], [100, 140], [80, 140], [100, 120], [100, 100]]

polygon = [[100, 400], [500, 100], [900, 400], [500, 250], [100, 400]] 

#for i in range(len(polygon)):
#    polygon[i] = [(polygon[i][0]*4)-100, (polygon[i][1]*4)-200]
 
class DummyEvent:
    def __init__(self, x, y):
        self.x, self.y = x, y
 
dummy_event = DummyEvent(104,398) 
#dummy_event = None




def dot(vA, vB):
    return vA[0]*vB[0]+vA[1]*vB[1]

def ang(lineA, lineB):
    # Get nicer vector form
    vA = [(lineA[0][0]-lineA[1][0]), (lineA[0][1]-lineA[1][1])]
    vB = [(lineB[0][0]-lineB[1][0]), (lineB[0][1]-lineB[1][1])]
    # Get dot prod
    dot_prod = dot(vA, vB)
    # Get magnitudes
    magA = dot(vA, vA)**0.5
    magB = dot(vB, vB)**0.5
    # Get cosine value
    cos_ = dot_prod/magA/magB
    # Get angle in radians and then convert to degrees
    angle = math.acos(dot_prod/magB/magA)
    # Basically doing angle <- angle mod 360
    ang_deg = math.degrees(angle)%360
    
    if ang_deg-180>=0:
        # As in if statement
        return 360 - ang_deg
    else: 
        
        return ang_deg



def calculate_bearings(pointA, pointB):
    startx,starty,endx,endy=pointA[0],pointA[1],pointB[0],pointB[1]
    angle=math.atan2(endy-starty, endx-startx)
    if angle>=0:
        deg1 = math.degrees(angle)
    else:
        deg1 = math.degrees((angle+2*math.pi))
        
    startx,starty,endx,endy=pointB[0],pointB[1],pointA[0],pointA[1]
    angle=math.atan2(endy-starty, endx-startx)
    if angle>=0:
        deg2 = math.degrees(angle)
    else:
        deg2 = math.degrees((angle+2*math.pi))
    
    return deg1, deg2
        
        

def line_intersection(line1, line2):
    line1 = LineString([line1[0], line1[1]])
    line2 = LineString([line2[0], line2[1]])
    int_pt = line1.intersection(line2)
    
    return int_pt.x, int_pt.y
    
    
def calculate_real_bearing(w, i):
    ri = i-w 
    a1 = w-ri 
    return a1
    
    

class Canvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs, bg='#222')
        
        
        self.cursor_obj = None
        self.lines = []
        self.user_lines = []
        
        self.source_obj = tk.PhotoImage(file="source.png")
        self.__draw_shape()
        print("Generating ...")
        self.motion_bind(dummy_event)
        print("{} lines drawn".format(len(self.lines)))
        self.bind("<Motion>", self.motion_bind)
        #self.bind("<ButtonPress-1>", self.__user_click)
                
    def __user_click(self, event):
        global polygon, dummy_event
        if len(self.user_lines) == 24:
            self.user_lines.append(self.user_lines[0])
            polygon = self.user_lines
            self.__draw_shape()
            self.config(cursor='target')
        elif len(self.user_lines) < 24:
            self.user_lines.append([(event.x // 16) * 16, (event.y // 16) * 16])
            polygon = self.user_lines
            self.__draw_shape()
        else:
            if (dummy_event == None):
                dummy_event = DummyEvent(event.x, event.y) 
                self.__draw_shape()
                self.motion_bind(dummy_event)
                self.config(cursor='')
            

    def __user_shape(self):
        lines = []
                
    def __draw_shape(self):
        for i in range(len(polygon)):
            if ((i+1) < len(polygon)):
                bbox_0 = polygon[i]
                bbox_1 = polygon[i+1]
                self.create_line(*bbox_0, *bbox_1, fill='#fff', width=1, smooth=True)
        
    def __get_closest_intercept(self, event, intercepts, saved_intercept, ignore_first=False):
        tmp = None
        intercept_1 = None
        intercept_2 = None
        tmp_min_1 = 1000000;
        tmp_min_2 = 1000000;
        for intercept in intercepts:
            dist = math.sqrt( (intercept[0][0] - event[0])**2 + (intercept[0][1] - event[1])**2 )
            if dist < tmp_min_1:
                if intercept[1] == saved_intercept:
                    continue
                tmp_min_1 = dist
                intercept_1 = intercept
        return intercept_1
        
    def bounce_rays(self, origin, angle, line_angle, saved_intercept, maximum=3):
        x = 1024*math.cos(math.radians(angle-90))
        y = 1024*math.sin(math.radians(angle-90))
        #self.lines.append(self.create_line(*origin, origin[0]+x, origin[1]+y, fill='blue'))
        
        maximum = maximum - 1
        
        
        intercepts = []
        for i in range(len(polygon)):
            try:
                try:
                    intercept = (line_intersection([[origin[0], origin[1]], [origin[0]+x, origin[1]+y]], [[polygon[i][0], polygon[i][1]], [polygon[i+1][0], polygon[i+1][1]]]), i)
                except IndexError:
                    intercept = (line_intersection([[origin[0], origin[1]], [origin[0]+x, origin[1]+y]], [[polygon[i][0], polygon[i][1]], [polygon[0][0], polygon[0][1]]]), i)
            except Exception as e:
                continue
            intercepts.append(intercept)
        
        intercept = self.__get_closest_intercept([origin[0], origin[1]], intercepts, saved_intercept)
        
        self.lines.append(self.create_line(*origin, intercept[0][0], intercept[0][1], fill='yellow', width=1))
        
        angle = -math.degrees(math.atan2(intercept[0][1]-origin[1], intercept[0][0]-origin[0]))
        angle = (((-angle + 90) + 360) % 360)
        #angle = angle - 90
        new_angle = 180-90-incr
        start = polygon[intercept[1]]
        try:
            end = polygon[intercept[1]+1]
        except IndexError:
            end = polygon[0]


            
        line_angle = (math.degrees(math.atan2(-end[1] - -start[1], end[0]-start[0])))
        line_angle = ((-line_angle + 90) + 360) % 360 # conversion
        

        angle_bearing = calculate_real_bearing(line_angle, angle)
        
        if maximum < 1:
            return
        
        self.bounce_rays([intercept[0][0], intercept[0][1]], angle_bearing, line_angle, intercept[1], maximum=maximum)
        #self.lines.append(self.create_line(origin[0]+x, origin[1]+y, intercept[0][0], intercept[0][1], fill='green', width=4))
        
        


        
    def motion_bind(self, event):

            self.delete(self.cursor_obj)
            self.__draw_shape()
            
            self.config(cursor='none')
            
            
            
            for line in self.lines:
                self.delete(line)
            self.lines = []
            
            for i in range(k):
                x = 1024*math.cos(math.radians(i*incr))
                y = 1024*math.sin(math.radians(i*incr))

                intercepts = []
                for i in range(len(polygon)):
                    try:
                        try:
                            intercept = (line_intersection([[event.x, event.y], [event.x+x, event.y+y]], [[polygon[i][0], polygon[i][1]], [polygon[i+1][0], polygon[i+1][1]]]), i)
                        except IndexError:
                            intercept = (line_intersection([[event.x, event.y], [event.x+x, event.y+y]], [[polygon[i][0], polygon[i][1]], [polygon[0][0], polygon[0][1]]]), i)
                    except Exception as e:
                        continue
                    intercepts.append(intercept)
                
                intercept = self.__get_closest_intercept([event.x, event.y], intercepts, None)
                try:
                    self.lines.append(self.create_line(event.x, event.y, intercept[0][0], intercept[0][1], fill='yellow', width=3))
                    angle = -math.degrees(math.atan2(intercept[0][1]-event.y, intercept[0][0]-event.x))
                    angle = (((-angle + 90) + 360) % 360)
                    #angle = angle - 90
                    new_angle = 180-90-incr
                    start = polygon[intercept[1]]
                    try:
                        end = polygon[intercept[1]+1]
                    except IndexError:
                        end = polygon[0]


                        
                    line_angle = (math.degrees(math.atan2(-end[1] - -start[1], end[0]-start[0])))
                    line_angle = ((-line_angle + 90) + 360) % 360 # conversion
                    

                    angle_bearing = calculate_real_bearing(line_angle, angle)
                    self.bounce_rays([intercept[0][0], intercept[0][1]], angle_bearing, line_angle, intercept[1], maximum=max_bounce)
                except TypeError as e:
                    pass
            self.cursor_obj = self.create_image(event.x, event.y, image=self.source_obj)

                        

        
"""
incidence b    wall1 b     wall2 b     normal1 b1     normal2    reflected b    incidence s    tmp     normal s    reflected s
90    0    180    90    270    270    todo...
330    135    315    45    225    todo    todo...
210    315    135    225    45    todo    todo...
"""
        
        
        
        



class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("1024x720")
        
        self.canvas = Canvas(self, width=1024, height=720); self.canvas.pack()
        
        self.title("Illumination Simulation")
        self.mainloop()
        
        
if __name__ == "__main__":
    App()
