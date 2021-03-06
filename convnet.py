import keras
from keras.models import Sequential
from keras.layers import Layer, Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D, ZeroPadding2D
from keras.optimizers import RMSprop, SGD
from keras.layers.normalization import BatchNormalization
from keras.models import Model

# full length: 96 x 1366 

def build_convnet_model():
	''' Build a convnet with options:

		    num_conv_layers = 5
		    num_feature_maps = [32, 128, 128, 192, 256]
		    pool_sizes = [(2,4),(2,4),(2,4),(3,5),(4,4)]
		    conv_sizes = [(3,3), (3,3), (3,3), (3,3), (3,3)]
		    dropout_conv = 0.5
		    model_type = 'vgg_simple'
		    memo = 'conv2d_fcn5_smaller_32-256'

	'''
	model = design_2d_convnet_model()	
	return model

def design_2d_convnet_model():
	num_channels = 1
	height_input  =96
	width_input = 1366
	num_conv_layers = 5
	nums_feat_maps = [32,128,128,192,256]
	feat_scale_factor = 1
	conv_sizes = [(3,3),(3,3),(3,3),(3,3),(3,3)]
	pool_sizes = [(2,4),(2,4),(2,4),(3,5),(4,4)]
	dropout_conv = 0.5
	dim_labels = 50
	# prepre modules
	model = Sequential()
	model.add(BatchNormalization(axis=3, input_shape=(num_channels, height_input, width_input))) # per each frequency.
	args = [num_conv_layers, nums_feat_maps, feat_scale_factor, conv_sizes, \
			pool_sizes,	dropout_conv, (num_channels, height_input, width_input)]
	model.add(get_convBNeluMPdrop(*args))
	
	model.add(Flatten()) # use model.output_shape (which is e.g. (None, 32)) for the following layer
		
	#[Output layer]
	model.add(Dense(dim_labels, activation='sigmoid'))

	return model	

def get_convBNeluMPdrop(num_conv_layers, nums_feat_maps, feat_scale_factor, conv_sizes, pool_sizes, dropout_conv, input_shape):
	#[Convolutional Layers]
	model = Sequential()
	input_shape_specified = False
	for conv_idx in xrange(num_conv_layers):
		# add conv layer
		n_feat_here = int(nums_feat_maps[conv_idx]*feat_scale_factor)
		if not input_shape_specified:
			print ' ---->>First conv layer is being added! with %d' % n_feat_here
			model.add(Convolution2D(n_feat_here, conv_sizes[conv_idx][0], conv_sizes[conv_idx][1], 
									input_shape=input_shape,
									border_mode='same',  
									init='he_normal'))
			input_shape_specified = True
		else:
			print ' ---->>%d-th conv layer is being added with %d units' % (conv_idx, n_feat_here)
			model.add(Convolution2D(n_feat_here, conv_sizes[conv_idx][0], conv_sizes[conv_idx][1], 
									border_mode='same',
									init='he_normal'))
		# add BN, Activation, pooling, and dropout
		model.add(BatchNormalization(axis=1, mode=2))
		model.add(keras.layers.advanced_activations.ELU(alpha=1.0)) # TODO: select activation
		
		model.add(MaxPooling2D(pool_size=pool_sizes[conv_idx]))
		if not dropout_conv == 0.0:
			model.add(Dropout(dropout_conv))
			print ' ---->>Add dropout of %f for %d-th conv layer' % (dropout_conv, conv_idx)
	model.summary()
	return model

