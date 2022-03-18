'''
Implementation of a simple Rossler Attractor, see 

https://en.wikipedia.org/wiki/R%C3%B6ssler_attractor

Default uses original values of a=0.2, b=0.2, c=5.7
'''

class rossler:
    def __init__(self, point=(5.,5.,5.), params=(0.3,0.2,5.7), dt=0.01):
        self.x = point[0]
        self.y = point[1]
        self.z = point[2]
        self.a = params[0]
        self.b = params[1]
        self.c = params[2]
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
    def estimateRanges(self,steps=1000000):
    
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
    
    def __str__(self):
        return (f"({self.x:2.2f},{self.y:2.2f},{self.z:2.2f})({self.a},{self.b},{self.c})")

    def step(self):
        '''
        Update the point.
        '''
        x_dot = -self.y - self.x
        y_dot = self.x + self.a*self.y
        z_dot = self.b + self.z*(self.x - self.c)
        self.x += x_dot * self.dt
        self.y += y_dot * self.dt
        self.z += z_dot * self.dt

def main():
    r = rossler()
    r.estimateRanges()
    print(r)
    print(f"Min x:{r.x_min:8.2f} y:{r.y_min:8.2f} z:{r.z_min:8.2f}")
    print(f"Max x:{r.x_max:8.2f} y:{r.y_max:8.2f} z:{r.z_max:8.2f}")
    print(f"Ran x:{r.x_range:8.2f} y:{r.y_range:8.2f} z:{r.z_range:8.2f}")

if __name__ == "__main__":
    main()

