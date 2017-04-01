import csv
import numpy as np
import math

train_filename = 'test_data1.csv'
data = []

# produces polynomial basis functions, where upper is the highest power
def poly_basis(class_features, upper):
	track = np.ones(class_features.shape)
	for i in range(1, upper + 1):
		track = np.hstack((track, np.power(class_features, i)))
	return track

# produces sin basis functions, were upper is the highest divisor of x
def sin_basis(class_features, upper):
	track = np.ones(class_features.shape)
	for i in range(1, upper + 1):
		track = np.vstack((track, np.sin(class_features / i)))
	return track.T

class LinReg:
	def __init__(self, eta, lambda_parameter):
		# learning rate
		self.eta = eta
		self.lambda_parameter = lambda_parameter


	# tune given user's weights
	def fit(self, X, y):
		self.y = y
		self.X = X
		self.w = np.multiply(0.1, np.ones(self.X[0].shape))
		for iters in range(15000):
			loss = 0
			delta = np.zeros(len(self.w))
			for k in range(len(self.y)):
				if self.y[k] != -1:
					loss = loss + np.dot(np.dot(self.X[k], self.w), np.dot(self.X[k], self.w))
					delta = np.add(delta, np.add(np.multiply(np.dot(self.X[k], self.w), self.X[k]), np.multiply(self.lambda_parameter, self.w)))
			# should be strictly decreasing
			print(loss)
			self.w = self.w - self.eta * delta

	# use weights to predict not yet rated courses
	def predict_missing(self):
		self.y_updated = []
		for k in range(len(self.y)):
			if self.y[k] == -1:
				self.y_updated.append(np.dot(self.X[k], self.w))
			else:
				self.y_updated.append(-1)
		return self.y_updated

with open(train_filename, 'r') as csv_fh:

    # Parse as a CSV file.
    reader = csv.reader(csv_fh)

    # Skip the header line.
    #next(reader, None)

    class_features = []
    user_ratings = []

    # Loop over the file.
    for row in reader:
    	row = list(map(lambda s: float(s), row))
    	# Store the data.
    	class_features.append(row[:len(row) - 1])
    	user_ratings.append(row[len(row) - 1])

# Turn the data into numpy arrays after applying basis (if necessary)
X = np.array(class_features)
y = np.array(user_ratings)

LinRegRec = LinReg(eta=0.0000015, lambda_parameter=0.000002)
LinRegRec.fit(X, y)
preds = LinRegRec.predict_missing()

print(preds)