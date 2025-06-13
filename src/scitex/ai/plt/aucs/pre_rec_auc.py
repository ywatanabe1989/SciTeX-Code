#!/usr/bin/env python3

import warnings
from itertools import cycle

import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve


def solve_the_intersection_of_a_line_and_iso_f1_curve(f1, a, b):
    """
    Determines the intersection of the following lines:
        1) a line: y = a * x + b
        2) the iso-f1 curve: y = f1 * x / (2 * x - f1)
    , where a, b, and f1 are the constant values.
    """
    _a = 2 * a
    _b = -a * f1 + 2 * b - f1
    _c = -b * f1

    x_f = (-_b + np.sqrt(_b**2 - 4 * _a * _c)) / (2 * _a)
    y_f = a * x_f + b

    return (x_f, y_f)


def to_onehot(labels, n_classes):
    eye = np.eye(n_classes, dtype=int)
    return eye[labels]


def pre_rec_auc(plt, true_class, pred_proba, labels):
    """
    Calculates the precision recall curve.
    """

    # Use label_binarize to be multi-label like settings
    n_classes = len(labels)
    true_class_onehot = to_onehot(true_class, n_classes)

    # For each class
    precision = dict()
    recall = dict()
    threshold = dict()
    pre_rec_auc = dict()
    for i in range(n_classes):
        true_class_i_onehot = true_class_onehot[:, i]
        pred_proba_i = pred_proba[:, i]

        try:
            precision[i], recall[i], threshold[i] = precision_recall_curve(
                true_class_i_onehot,
                pred_proba_i,
            )
            pre_rec_auc[i] = average_precision_score(true_class_i_onehot, pred_proba_i)
        except Exception as e:
            print(e)
            precision[i], recall[i], threshold[i], pre_rec_auc[i] = (
                np.nan,
                np.nan,
                np.nan,
                np.nan,
            )

    ## Average precision: micro and macro

    # A "micro-average": quantifying score on all classes jointly
    precision["micro"], recall["micro"], threshold["micro"] = precision_recall_curve(
        true_class_onehot.ravel(), pred_proba.ravel()
    )
    pre_rec_auc["micro"] = average_precision_score(
        true_class_onehot, pred_proba, average="micro"
    )

    # macro
    _pre_rec_aucs = []
    for i in range(n_classes):
        try:
            _pre_rec_aucs.append(
                average_precision_score(
                    true_class_onehot[:, i], pred_proba[:, i], average="macro"
                )
            )
        except Exception as e:
            print(
                f'\nPRE-REC-AUC for "{labels[i]}" was not defined and NaN-filled '
                "for a calculation purpose (for the macro avg.)\n"
            )
            _pre_rec_aucs.append(np.nan)
    pre_rec_auc["macro"] = np.nanmean(_pre_rec_aucs)

    # pre_rec_auc["macro"] = average_precision_score(
    #     true_class_onehot, pred_proba, average="macro"
    # )

    # Plot Precision-Recall curve for each class and iso-f1 curves
    colors = cycle(["navy", "turquoise", "darkorange", "cornflowerblue", "teal"])
    fig, ax = plt.subplots()
    ax.set_box_aspect(1)
    lines = []
    legends = []

    # iso-F1: By definition, an iso-F1 curve contains all points
    #         in the precision/recall space whose F1 scores are the same.
    f_scores = np.linspace(0.2, 0.8, num=4)
    # for f_score in f_scores:
    for i_f, f_score in enumerate(f_scores):
        x = np.linspace(0.01, 1)  # num=50
        y = f_score * x / (2 * x - f_score)
        (l,) = ax.plot(x[y >= 0], y[y >= 0], color="gray", alpha=0.2)

        # ax.annotate("f1={0:0.1f}".format(f_score), xy=(0.9, y[45] + 0.02))
        x_f, y_f = solve_the_intersection_of_a_line_and_iso_f1_curve(f_score, 0.5, 0.5)
        ax.annotate("f1={0:0.1f}".format(f_score), xy=(x_f - 0.1, y_f - 0.1 * 0.5))
        # ax.annotate("f1={0:0.1f}".format(f_score), xy=(y[35] - 0.02 * (3 - i_f), 0.85))

    lines.append(l)
    legends.append("iso-f1 curves")

    """
    ## In this project, average precision-recall curve is not drawn.
    (l,) = ax.plot(recall["micro"], precision["micro"], color="gold", lw=2)
    lines.append(l)
    legends.append("micro-average\n(AUC = {0:0.2f})" "".format(pre_rec_auc["micro"]))
    """

    ## Each Class
    for i, color in zip(range(n_classes), colors):
        (l,) = ax.plot(recall[i], precision[i], color=color, lw=2)
        lines.append(l)
        legends.append("{0} (AUC = {1:0.2f})" "".format(labels[i], pre_rec_auc[i]))

    # fig = plt.gcf()
    fig.subplots_adjust(bottom=0.25)
    ax.set_xlim([-0.01, 1.01])
    ax.set_ylim([-0.01, 1.01])
    ax.set_xticks([0.0, 0.5, 1.0])
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall Curve")
    ax.legend(lines, legends, loc="lower left")

    metrics = dict(
        pre_rec_auc=pre_rec_auc,
        precision=precision,
        recall=recall,
        threshold=threshold,
    )

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

    pre_rec_auc, precision, recall, threshold = \
        calc_pre_rec_auc(true_class, pred_proba, labels, plot=False)
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

    ## Main
    fig, metrics_dict = pre_rec_auc(plt, y_test, predicted_proba, labels)

    fig.show()

    print(metrics_dict.keys())
    # dict_keys(['pre_rec_auc', 'precision', 'recall', 'threshold'])
