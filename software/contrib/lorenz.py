from attractor import attractor
'''
Implementation of a simple Lorenz Attractor, see 

https://en.wikipedia.org/wiki/Lorenz_system

Default uses well known values of s=10,r=28,b=2.667. 
'''

class lorenz(attractor):
    def __init__(self, point=(0.,1.,1.05), params=(10,28,2.667), dt=0.01):
        super().__init__(point, dt)
        self.s = params[0]
        self.r = params[1]
        self.b = params[2]

    def __str__(self):
        return (f"({self.x:2.2f},{self.y:2.2f},{self.z:2.2f})({self.s},{self.r},{self.b})")

    def step(self):
        '''
        Update the point.
        '''
        x_dot = self.s*(self.y - self.x)
        y_dot = self.r*self.x - self.y - self.x*self.z
        z_dot = self.x*self.y - self.b*self.z
        self.x += x_dot * self.dt
        self.y += y_dot * self.dt
        self.z += z_dot * self.dt

def main():
    l = lorenz()
    l.estimateRanges()
    print(l)
    print(f"Min x:{l.x_min:8.2f} y:{l.y_min:8.2f} z:{l.z_min:8.2f}")
    print(f"Max x:{l.x_max:8.2f} y:{l.y_max:8.2f} z:{l.z_max:8.2f}")
    print(f"Ran x:{l.x_range:8.2f} y:{l.y_range:8.2f} z:{l.z_range:8.2f}")

if __name__ == "__main__":
    main()

