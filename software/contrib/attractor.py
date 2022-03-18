'''
Generic attractor, see 

https://en.wikipedia.org/wiki/Lorenz_system

Default uses well known values of s=10,r=28,b=2.667. 
'''

class attractor:
    def __init__(self, point=(0.,1.,1.05), dt=0.01):
        self.x = point[0]
        self.y = point[1]
        self.z = point[2]
        self.dt = dt
        self.x_min = self.x
        self.y_min = self.y
        self.z_min = self.z
        self.x_max = self.x
        self.y_max = self.y
        self.z_max = self.z
        # arbitrary initial range values    
        self.x_range = 100
        self.y_range = 100
        self.z_range = 100
        
    # The range of values produced depends on the parameters. If we
    # know the range, we can then normalise coordinates for use when
    # generating CV. This method runs through a number of iterations
    # to estimate ranges.
    def estimateRanges(self,steps=100000):
    
        # Execute a number of steps to get upper and lower bounds. 
        for i in range(steps):
            self.step()
            
            self.x_max = max(self.x, self.x_max)
            self.y_max = max(self.y, self.y_max)
            self.z_max = max(self.z, self.z_max)
            self.x_min = min(self.x, self.x_min)
            self.y_min = min(self.y, self.y_min)
            self.z_min = min(self.z, self.z_min)

        self.x_range = self.x_max-self.x_min
        self.y_range = self.y_max-self.y_min
        self.z_range = self.z_max-self.z_min

    def x_scaled(self):
        return (100.0 * (self.x - self.x_min))/self.x_range

    def y_scaled(self):
        return (100.0 * (self.y - self.y_min))/self.y_range

    def z_scaled(self):
        return (100.0 * (self.z - self.z_min))/self.z_range
    
    def step(self):
        '''
        Update the point.
        '''
        pass

