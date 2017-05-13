"""Iterator class, used in create_library_class to take fixed sized
smaller matrix of the input matrix S."""


class MatrixSlide:
    """ITERATOR.

    Used to take a smaller submatrix with chosen width from the input matrix S.
    The iterator first returns the left most submatrix and then each returns
    the submatrix with given stepsize more to the right.

    Also returns the integer pos, which is the position of the middle of the
    submatrix, expressed in the index of the input matrix S."""

    def __init__(self, S, width, stepsize):
        self.S = S
        self.width = width
        self.stepsize = stepsize

    def __iter__(self):
        self.pos = 0
        return self

    def __next__(self):
        if self.pos == self.S.shape[1]:
            raise StopIteration

        Ssub = self.S[:, max(self.pos-self.width/2, 0):
                         min(self.pos+self.width/2, self.S.shape[1])]
        pos = self.pos
        self.pos += self.stepsize
        return Ssub, pos
