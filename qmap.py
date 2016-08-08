import numpy as np

class QMap():
    def __init__(self, step=0.01):
        self.step = step

    def fit(self, x, y, axis=None):
        if axis not in (None, 0):
            raise ValueError("Axis should be None or 0")
        self.axis = axis
        steps = np.arange(0, 100, self.step)
        self.x_map = np.percentile(x, steps, axis=axis)
        self.y_map = np.percentile(y, steps, axis=axis)
        return self

    def predict(self, y):
        idx = [np.abs(val - self.y_map).argmin(axis=self.axis) for val in y]
        if self.axis == 0:
            out = np.asarray([self.x_map[k, range(y.shape[1])] for k in idx])
        else:
            out = self.x_map[idx]
        return out

def test_qmap():
    np.random.seed(0)
    x = np.random.normal(10, size=(10,20))
    y = np.random.normal(100, size=(10, 20))
    mapped = np.zeros(x.shape)
    for j in range(x.shape[1]):
        qmap = QMap()
        qmap.fit(x[:,j], y[:,j])
        mapped[:, j] = qmap.predict(y[:,j])

if __name__ == "__main__":
    test_qmap()
