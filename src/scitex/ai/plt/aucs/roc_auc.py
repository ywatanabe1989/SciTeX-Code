#!/usr/bin/env python3

import warnings
from itertools import cycle

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve
import pandas as pd

import scitex


def interpolate_roc_data_points(df):
    df_new = pd.DataFrame(
        {
            "x": np.arange(1001) / 1000,
            "y": np.nan,
            "threshold": np.nan,
        }
    )

    for i_row in range(len(df) - 1):
        x_pre = df.iloc[i_row]["fpr"]
        x_post = df.iloc[i_row + 1]["fpr"]

        indi = (x_pre <= df_new["x"]) * (df_new["x"] <= x_post)

        y_pre = df.iloc[i_row]["tpr"]
        y_post = df.iloc[i_row + 1]["tpr"]

        t_pre = df.iloc[i_row]["threshold"]
        t_post = df.iloc[i_row + 1]["threshold"]

        df_new["y"][indi] = y_pre
        df_new["threshold"][indi] = t_pre

    df_new["y"].iloc[0] = df["tpr"].iloc[0]
    df_new["y"].iloc[-1] = df["tpr"].iloc[-1]

    df_new["threshold"].iloc[0] = df["threshold"].iloc[0]
    df_new["threshold"].iloc[-1] = df["threshold"].iloc[-1]

    df_new["roc_auc"] = df["roc_auc"].iloc[0]

    # import ipdb; ipdb.set_trace()
    # assert df_new["y"].isna().sum() == 0
    return df_new


def to_onehot(labels, n_classes):
    eye = np.eye(n_classes, dtype=int)
    return eye[labels]


def roc_auc(plt, true_class, pred_proba, labels, sdir_for_csv=None, spath=None):
    """
    Calculates ROC-AUC curve.
    Return: fig, metrics (dict)
    """

    # Use label_binarize to be multi-label like settings
    n_classes = len(labels)
    true_class_onehot = to_onehot(true_class, n_classes)

    # For each class
    fpr = dict()
    tpr = dict()
    threshold = dict()
    roc_auc = dict()
    for i in range(n_classes):
        true_class_i_onehot = true_class_onehot[:, i]
        pred_proba_i = pred_proba[:, i]

        try:
            fpr[i], tpr[i], threshold[i] = roc_curve(true_class_i_onehot, pred_proba_i)
            roc_auc[i] = roc_auc_score(true_class_i_onehot, pred_proba_i)
        except Exception as e:
            print(e)
            fpr[i], tpr[i], threshold[i], roc_auc[i] = (
                [np.nan],
                [np.nan],
                [np.nan],
                np.nan,
            )

    ## Average fpr: micro and macro

    # A "micro-average": quantifying score on all classes jointly
    fpr["micro"], tpr["micro"], threshold["micro"] = roc_curve(
        true_class_onehot.ravel(), pred_proba.ravel()
    )
    roc_auc["micro"] = roc_auc_score(true_class_onehot, pred_proba, average="micro")

    # macro
    _roc_aucs = []
    for i in range(n_classes):
        try:
            _roc_aucs.append(
                roc_auc_score(
                    true_class_onehot[:, i], pred_proba[:, i], average="macro"
                )
            )
        except Exception as e:
            print(
                f'\nROC-AUC for "{labels[i]}" was not defined and NaN-filled '
                "for a calculation purpose (for the macro avg.)\n"
            )
            _roc_aucs.append(np.nan)
    roc_auc["macro"] = np.nanmean(_roc_aucs)

    if sdir_for_csv is not None:
        # to dfs
        for i in range(n_classes):
            class_name = labels[i].replace(" ", "_")
            df = pd.DataFrame(
                data={
                    "fpr": fpr[i],
                    "tpr": tpr[i],
                    "threshold": threshold[i],
                    "roc_auc": [roc_auc[i] for _ in range(len(fpr[i]))],
                },
                index=pd.Index(data=np.arange(len(fpr[i])), name=class_name),
            )
            df = interpolate_roc_data_points(df)
            spath = f"{sdir_for_csv}{class_name}.csv"
            scitex.io.save(df, spath)

    # Plot FPR-TPR curve for each class and iso-f1 curves
    colors = cycle(["navy", "turquoise", "darkorange", "cornflowerblue", "teal"])

    fig, ax = plt.subplots()
    ax.set_box_aspect(1)
    lines = []
    legends = []

    ## Chance Level (the diagonal line)
    (l,) = ax.plot(
        np.linspace(0.01, 1),
        np.linspace(0.01, 1),
        color="gray",
        lw=2,
        linestyle="--",
        alpha=0.8,
    )
    lines.append(l)
    legends.append("Chance")

    ## Each Class
    for i, color in zip(range(n_classes), colors):
        (l,) = plt.plot(fpr[i], tpr[i], color=color, lw=2)
        lines.append(l)
        legends.append("{0} (AUC = {1:0.2f})" "".format(labels[i], roc_auc[i]))

    # fig = plt.gcf()
    fig.subplots_adjust(bottom=0.25)
    ax.set_xlim([-0.01, 1.01])
    ax.set_ylim([-0.01, 1.01])
    ax.set_xticks([0.0, 0.5, 1.0])
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_xlabel("FPR")
    ax.set_ylabel("TPR")
    ax.set_title("ROC Curve")
    ax.legend(lines, legends, loc="lower right")

    metrics = dict(roc_auc=roc_auc, fpr=fpr, tpr=tpr, threshold=threshold)

    # Save figure if spath is provided
    if spath is not None:
        scitex.io.save(fig, spath)

    # return fig, roc_auc, fpr, tpr, threshold
    return fig, metrics


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.special import softmax
    from sklearn import datasets, svm
    from sklearn.model_selection import train_test_split

    def mk_demo_data(n_classes=2, batch_size=16):
        labels = ["cls{}".format(i_cls) for i_cls in range(n_classes)]
        true_class = np.random.randint(0, n_classes, size=(batch_size,))
        pred_proba = softmax(np.random.rand(batch_size, n_classes), axis=-1)
        pred_class = np.argmax(pred_proba, axis=-1)
        return labels, true_class, pred_proba, pred_class

    ## Fix seed
    np.random.seed(42)

    """
    ################################################################################
    ## A Minimal Example
    ################################################################################    
    labels, true_class, pred_proba, pred_class = \
        mk_demo_data(n_classes=10, batch_size=256)

    roc_auc, fpr, tpr, threshold = \
        calc_roc_auc(true_class, pred_proba, labels, plot=False)
    """

    ################################################################################
    ## MNIST
    ################################################################################
    from sklearn import datasets, metrics, svm
    from sklearn.model_selection import train_test_split

    digits = datasets.load_digits()

    # flatten the images
    n_samples = len(digits.images)
    data = digits.images.reshape((n_samples, -1))

    # Create a classifier: a support vector classifier
    clf = svm.SVC(gamma=0.001, probability=True)

    # Split data into 50% train and 50% test subsets
    X_train, X_test, y_train, y_test = train_test_split(
        data, digits.target, test_size=0.5, shuffle=False
    )

    # Learn the digits on the train subset
    clf.fit(X_train, y_train)

    # Predict the value of the digit on the test subset
    predicted_proba = clf.predict_proba(X_test)
    predicted = clf.predict(X_test)

    n_classes = len(np.unique(digits.target))
    labels = ["Class {}".format(i) for i in range(n_classes)]

    ## Configures matplotlib
    plt.rcParams["font.size"] = 20
    plt.rcParams["legend.fontsize"] = "xx-small"
    plt.rcParams["figure.figsize"] = (16 * 1.2, 9 * 1.2)

    np.unique(y_test)
    np.unique(predicted_proba)

    y_test[y_test == 9] = 8  # override 9 as 8
    ## Main
    fig, metrics_dict = roc_auc(
        plt, y_test, predicted_proba, labels, sdir_for_csv="./tmp/roc_test/"
    )

    fig.show()

    print(metrics_dict.keys())
    # dict_keys(['roc_auc', 'fpr', 'tpr', 'threshold'])
