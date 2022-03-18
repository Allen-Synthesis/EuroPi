from attractor import attractor
'''
Implementation of a simple Rossler Attractor, see 

https://en.wikipedia.org/wiki/R%C3%B6ssler_attractor

Default uses original values of a=0.2, b=0.2, c=5.7
'''

class rossler(attractor):
    def __init__(self, point=(5.,5.,5.), params=(0.3,0.2,5.7), dt=0.01):
        super().__init__(point,dt)
        self.a = params[0]
        self.b = params[1]
        self.c = params[2]
    
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

