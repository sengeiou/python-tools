import numpy as np

def GenerateTriangleTable(num) :
    x = np.linspace(0, 2*np.pi, num, endpoint=False)
    y = np.sin(x)
    try:
        with open('sintbl.c', 'w+') as f:
            f.write('const float sine_table[] = { \n')
            for i in y :
                f.write('  {:.6f}\n'.format(i))
            f.write('};')
    except Exception as e:
        print(e)
    
    
if __name__ == '__main__' :
    GenerateTriangleTable(256)
