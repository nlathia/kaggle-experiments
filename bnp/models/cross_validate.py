from os import path
from csv import writer

from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

import pandas as pd
import numpy as np

import dataset


def load_file(data_file, new_feature_files):
    """
    Loads some data and splits into X, y
    :param data_file: Full path to CSV file
    :return: X, y
    """
    print '\tRead', data_file
    data = pd.read_csv(data_file)
    X = data.drop(dataset.TARGET_CLASS, axis=1)
    X.drop(dataset.ROW_ID, axis=1, inplace=True)
    y = data[dataset.TARGET_CLASS]
    row_ids = data[dataset.ROW_ID]

    for new_feature_file in new_feature_files:
        print '\tRead', new_feature_file
        new_features = pd.read_csv(new_feature_file)
        X = pd.concat([X, new_features], axis=1)
    return X, y, row_ids


def load_subset(directory, feature_files):
    """
    Loads a subset of the data
    :param directory: The subset's location
    :param feature_files: Any extra feature files
    :return: training Xs and test ys
    """
    train_features = [path.join(directory, f + dataset.TRAIN_FILE) for f in feature_files]
    test_features = [path.join(directory, f + dataset.TEST_FILE) for f in feature_files]

    X_train, y_train, _ = load_file(path.join(directory, dataset.TRAIN_FILE), train_features)
    X_test, y_test, row_ids = load_file(path.join(directory, dataset.TEST_FILE), test_features)
    return X_train, X_test, y_train, y_test, row_ids


def cross_validate(name, model, features=[]):
    losses = []
    for i in xrange(0, 10):
        print 'Subset', i
        directory = path.join(dataset.DATA_PATH, dataset.SUBSET + str(i))
        X_train, X_test, y_train, y_test, row_ids = load_subset(directory, features)

        print '\tTrain', name
        model.fit(X_train, y_train)
        y_pred = model.predict_proba(X_test)

        loss = log_loss(y_test, y_pred)
        losses.append(loss)
        print '\tLoss: ', loss

        result = pd.DataFrame({dataset.ROW_ID: row_ids, dataset.PREDICTION: y_pred[:, 1]})
        result.to_csv(path.join(directory, name + '.csv'), index=False)
    print 'CV Result', np.mean(losses), np.std(losses)
    return np.mean(losses), np.std(losses)


if __name__ == '__main__':

    name = 'corr-0.9'
    features = ['corr-0.9']
    models = {
        'LogisticRegression': LogisticRegression(),
        'RandomForest-500-gini': RandomForestClassifier(n_estimators=500, criterion='gini', n_jobs=-1),
        'RandomForest-500-entropy': RandomForestClassifier(n_estimators=500, criterion='entropy', n_jobs=-1),
        'ExtraTrees-500-gini': ExtraTreesClassifier(n_estimators=500, criterion='gini', n_jobs=-1),
        'ExtraTrees-500-entropy': ExtraTreesClassifier(n_estimators=500, criterion='entropy', n_jobs=-1)
    }

    with open('corr-0.9-result.csv', 'w') as out:
        rows = writer(out)
        for n, m in models.iteritems():
            avg, std = cross_validate(n, m, features)
            rows.writerow([name, n, avg, std])