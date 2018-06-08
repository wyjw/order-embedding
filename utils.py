"""
Helper functions for multimodal-ranking
"""
import theano
import theano.tensor as tensor
import numpy
import warnings
import pandas
import math

from collections import OrderedDict

def load_dataset(path):
    dataframe = pandas.read_csv(path, usecols = [1], engine = 'python', skipfooter = 3)
    

def zipp(params, tparams):
    """
    Push parameters to Theano shared variables
    """
    for kk, vv in params.iteritems():
        tparams[kk].set_value(vv)

def unzip(zipped):
    """
    Pull parameters from Theano shared variables
    """
    new_params = OrderedDict()
    for kk, vv in zipped.iteritems():
        new_params[kk] = vv.get_value()
    return new_params

def itemlist(tparams):
    """
    Get the list of parameters.
    Note that tparams must be OrderedDict
    """
    return [vv for kk, vv in tparams.iteritems()]

def _p(pp, name):
    """
    Make prefix-appended name
    """
    return '%s_%s'%(pp, name)

def init_tparams(params):
    """
    Initialize Theano shared variables according to the initial parameters
    """
    tparams = OrderedDict()
    for kk, pp in params.iteritems():
        tparams[kk] = theano.shared(params[kk], name=kk)
    return tparams

def load_params(path, params):
    """
    Load parameters
    """
    pp = numpy.load(path)
    for kk, vv in params.iteritems():
        if kk not in pp:
            warnings.warn('%s is not in the archive'%kk)
            continue
        params[kk] = pp[kk]
    return params

def ortho_weight(ndim):
    """
    Orthogonal weight init, for recurrent layers
    """
    W = numpy.random.randn(ndim, ndim)
    u, s, v = numpy.linalg.svd(W)
    return u.astype('float32')

def norm_weight(nin,nout=None, scale=0.1, ortho=True):
    """
    Uniform initalization from [-scale, scale]
    If matrix is square and ortho=True, use ortho instead
    """
    if nout == None:
        nout = nin
    if nout == nin and ortho:
        W = ortho_weight(nin)
    else:
        W = numpy.random.uniform(low=-scale, high=scale, size=(nin, nout))
    return W.astype('float32')

def xavier_weight(nin,nout=None):
    """
    Xavier init
    """
    if nout == None:
        nout = nin
    r = numpy.sqrt(6.) / numpy.sqrt(nin + nout)
    W = numpy.random.rand(nin, nout) * 2 * r - r
    return W.astype('float32')

def tanh(x):
    """
    Tanh activation function
    """
    return tensor.tanh(x)

def linear(x):
    """
    Linear activation function
    """
    return x

def l2norm(X):
    """
    Compute L2 norm, row-wise
    """
    norm = tensor.sqrt(tensor.pow(X, 2).sum(1))
    X /= norm[:, None]
    return X

def maxnorm(t, threshold):
    """
    Rescale given tensor to have norm at most equal to threshold
    """
    norm = (t**2).sum()
    return tensor.switch(norm > (threshold**2),
                         t / tensor.sqrt(norm) * threshold,
                         t)


def concatenate(tensor_list, axis=0):
    """
    Alternative implementation of `theano.tensor.concatenate`.
    """
    concat_size = sum(tt.shape[axis] for tt in tensor_list)

    output_shape = ()
    for k in range(axis):
        output_shape += (tensor_list[0].shape[k],)
    output_shape += (concat_size,)
    for k in range(axis + 1, tensor_list[0].ndim):
        output_shape += (tensor_list[0].shape[k],)

    out = tensor.zeros(output_shape)
    offset = 0
    for tt in tensor_list:
        indices = ()
        for k in range(axis):
            indices += (slice(None),)
        indices += (slice(offset, offset + tt.shape[axis]),)
        for k in range(axis + 1, tensor_list[0].ndim):
            indices += (slice(None),)

        out = tensor.set_subtensor(out[indices], tt)
        offset += tt.shape[axis]

    return out
