import csv
import numpy as np

train_filename = 'rating_data.csv'
data = []
#class_features  = np.zeros((10,5))
#user_ratings = np.zeros((10,1))

def lin_basis(class_features):
	return np.vstack((np.ones(class_features.shape), class_features)).T

# produces polynomial basis functions, where upper is the highest power
def poly_basis(class_features, upper):
	track = np.ones(class_features.shape)
	for i in range(1, upper + 1):
		track = np.vstack((track, np.power(class_features, i)))
	return track.T

# produces sin basis functions, were upper is the highest divisor of x
def sin_basis(class_features, upper):
	track = np.ones(class_features.shape)
	for i in range(1, upper + 1):
		track = np.vstack((track, np.sin(class_features / i)))
	return track.T

# calculate least-squares loss
def find_loss(w, X, Y):
	loss = np.subtract(Y, np.dot(X, w))
	return np.divide(np.dot(loss, loss), 2)

def find_loss(w, X, y):
	loss = 0
	m = 0
	for k in range(10):
		if y[k] != -1:
			m += 1
			loss += (np.dot(X[k],w) - y[k]) ** 2
	loss = 0.5 * m * loss
	return loss

with open(train_filename, 'r') as csv_fh:

    # Parse as a CSV file.
    reader = csv.reader(csv_fh)

    # Skip the header line.
    next(reader, None)

    # Loop over the file.
    for row in reader:

        # Store the data.
        data.append(float(row))
        #class_features.append(float(row[0]))
        #user_ratings.append(float(row[1]))

# Turn the data into numpy arrays.
[class_features, user_ratings] = np.split(data,[5])

# Create the simplest basis, with just the time and an offset.
X = lin_basis(class_features)

# Nothing fancy for outputs.
y = user_ratings

# Find the regression weights using the Moore-Penrose pseudoinverse.
w = np.linalg.solve(np.dot(X.T, X) , np.dot(X.T, Y))

# print least-squares loss
print (find_loss(w, X, Y))