#!/usr/bin/env python3
import matplotlib
import scitex
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import confusion_matrix as sklearn_confusion_matrix


def conf_mat(
    plt,
    cm=None,
    y_true=None,
    y_pred=None,
    y_pred_proba=None,
    labels=None,
    sorted_labels=None,
    pred_labels=None,
    sorted_pred_labels=None,
    true_labels=None,
    sorted_true_labels=None,
    label_rotation_xy=(15, 15),
    title="Confusion Matrix",
    colorbar=True,
    x_extend_ratio=1.0,
    y_extend_ratio=1.0,
    spath=None,
):
    """
    Plot confusion matrix as a heatmap with inverted y-axis.

    Parameters
    ----------
    plt : matplotlib.pyplot
        Pyplot object for plotting
    cm : array-like, optional
        Pre-computed confusion matrix
    y_true : array-like, optional
        True labels
    y_pred : array-like, optional
        Predicted labels
    y_pred_proba : array-like, optional
        Predicted probabilities
    labels : list, optional
        List of labels
    sorted_labels : list, optional
        Sorted list of labels
    pred_labels : list, optional
        Predicted label names
    sorted_pred_labels : list, optional
        Sorted predicted label names
    true_labels : list, optional
        True label names
    sorted_true_labels : list, optional
        Sorted true label names
    label_rotation_xy : tuple, optional
        Rotation angles for x and y labels
    title : str, optional
        Title of the plot
    colorbar : bool, optional
        Whether to include a colorbar
    x_extend_ratio : float, optional
        Ratio to extend x-axis
    y_extend_ratio : float, optional
        Ratio to extend y-axis
    spath : str, optional
        Path to save the figure

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot
    cm : pandas.DataFrame
        The confusion matrix as a DataFrame

    Example
    -------
    y_true = [0, 1, 2, 0, 1, 2]
    y_pred = [0, 2, 1, 0, 0, 1]
    labels = ['A', 'B', 'C']
    fig, cm = conf_mat(plt, y_true=y_true, y_pred=y_pred, labels=labels)
    plt.show()
    """

    if (y_pred_proba is not None) and (y_pred is None):
        y_pred = y_pred_proba.argmax(axis=-1)

    assert (cm is not None) or ((y_true is not None) and (y_pred is not None))

    if cm is None:
        with scitex.context.suppress_output():
            cm = sklearn_confusion_matrix(y_true, y_pred, labels=labels)

    bacc = calc_bACC_from_cm(cm)

    title = f"{title} (bACC = {bacc:.3f})"

    # Only reconstruct full confusion matrix if we have y_true and y_pred
    # When cm is passed directly, use it as-is
    if labels is not None and y_true is not None and y_pred is not None:
        full_cm = np.zeros((len(labels), len(labels)))
        unique_true = np.unique(y_true)
        unique_pred = np.unique(y_pred)
        for idx_true, true_label in enumerate(labels):
            for idx_pred, pred_label in enumerate(labels):
                if true_label in unique_true and pred_label in unique_pred:
                    full_cm[idx_true, idx_pred] = cm[
                        np.where(unique_true == true_label)[0][0],
                        np.where(unique_pred == pred_label)[0][0],
                    ]
        cm = full_cm

    cm = pd.DataFrame(data=cm).copy()

    labels_to_latex = lambda labels: (
        [scitex.str.to_latex_style(label) for label in labels]
        if labels is not None
        else None
    )
    pred_labels = labels_to_latex(pred_labels)
    true_labels = labels_to_latex(true_labels)
    labels = labels_to_latex(labels)
    sorted_labels = labels_to_latex(sorted_labels)

    if pred_labels is not None:
        cm.columns = pred_labels
    elif labels is not None:
        cm.columns = labels

    if true_labels is not None:
        cm.index = true_labels
    elif labels is not None:
        cm.index = labels

    if sorted_labels is not None:
        assert set(sorted_labels) == set(labels)
        cm = cm.reindex(index=sorted_labels, columns=sorted_labels)

    fig, ax = plt.subplots()
    res = sns.heatmap(
        cm,
        annot=True,
        annot_kws={"size": plt.rcParams["font.size"]},
        fmt=".0f",
        cmap="Blues",
        cbar=False,
        vmin=0,
    )

    for text in ax.texts:
        text.set_text("{:,d}".format(int(text.get_text())))

    res.invert_yaxis()

    for _, spine in res.spines.items():
        spine.set_visible(False)

    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title(title)

    ax = scitex.plt.ax.extend(ax, x_extend_ratio, y_extend_ratio)
    if cm.shape[0] == cm.shape[1]:
        ax.set_box_aspect(1)
        ax.set_xticklabels(
            ax.get_xticklabels(),
            rotation=label_rotation_xy[0],
            fontdict={"verticalalignment": "top"},
        )
        ax.set_yticklabels(
            ax.get_yticklabels(),
            rotation=label_rotation_xy[1],
            fontdict={"horizontalalignment": "right"},
        )

    bbox = ax.get_position()
    left_orig = bbox.x0
    width_orig = bbox.x1 - bbox.x0
    width_tgt = width_orig * x_extend_ratio
    dx = width_orig - width_tgt

    if colorbar:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        cax = scitex.plt.ax.shift(cax, dx=-dx * 2.54, dy=0)
        fig.add_axes(cax)

        vmax = np.array(cm).max().astype(int)
        norm = matplotlib.colors.Normalize(vmin=0, vmax=vmax)
        cbar = fig.colorbar(
            plt.cm.ScalarMappable(norm=norm, cmap="Blues"),
            cax=cax,
        )
        cbar.locator = ticker.MaxNLocator(nbins=4)
        cbar.update_ticks()
        cbar.outline.set_edgecolor("white")

    if spath is not None:
        scitex.io.save(fig, spath)

    return fig, cm


def calc_bACC_from_cm(cm):
    """
    Calculate balanced accuracy from confusion matrix.

    Parameters
    ----------
    cm : array-like
        Confusion matrix

    Returns
    -------
    float
        Balanced accuracy

    Example
    -------
    cm = np.array([[5, 1], [2, 3]])
    bacc = calc_bACC_from_cm(cm)
    print(bacc)
    """
    with scitex.context.suppress_output():
        try:
            per_class = np.diag(cm) / np.nansum(cm, axis=1)
            bacc = np.nanmean(per_class)
        except:
            bacc = np.nan
        return round(bacc, 3)


def calc_balanced_accuracy_from_cm(cm):
    """
    Calculate balanced accuracy from confusion matrix (snake_case alias).
    
    This is an alias for calc_bACC_from_cm with snake_case naming.
    
    Parameters
    ----------
    cm : array-like
        Confusion matrix
        
    Returns
    -------
    float
        Balanced accuracy
    """
    return calc_bACC_from_cm(cm)


if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt
    import scitex
    import numpy as np
    import sklearn
    from sklearn import datasets, svm
    from sklearn.model_selection import train_test_split

    sys.path.append(".")
    import scitex

    iris = datasets.load_iris()
    X = iris.data
    y = iris.target
    class_names = iris.target_names

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    classifier = svm.SVC(kernel="linear", C=0.01, random_state=42).fit(X_train, y_train)

    y_pred = classifier.predict(X_test)
    cm = sklearn.metrics.confusion_matrix(y_test, y_pred)
    cm **= 3

    fig, cm = conf_mat(
        plt,
        cm,
        pred_labels=["A", "B", "C"],
        true_labels=["a", "b", "c"],
        label_rotation_xy=(60, 60),
        x_extend_ratio=1.0,
        colorbar=True,
    )

    fig.axes[-1] = scitex.plt.ax.sci_note(
        fig.axes[-1],
        fformat="%3.1f",
        y=True,
    )

    plt.show()

# EOF

# #!/usr/bin/env python3
# import matplotlib
# import scitex
# import numpy as np
# import pandas as pd
# import seaborn as sns
# from matplotlib import ticker
# from mpl_toolkits.axes_grid1 import make_axes_locatable
# from sklearn.metrics import balanced_accuracy_score
# from sklearn.metrics import confusion_matrix as sklearn_confusion_matrix


# def conf_mat(
#     plt,
#     cm=None,
#     y_true=None,
#     y_pred=None,
#     y_pred_proba=None,
#     labels=None,
#     sorted_labels=None,
#     pred_labels=None,
#     sorted_pred_labels=None,
#     true_labels=None,
#     sorted_true_labels=None,
#     label_rotation_xy=(15, 15),
#     title="Confuxion Matrix",
#     colorbar=True,
#     x_extend_ratio=1.0,
#     y_extend_ratio=1.0,
#     spath=None,
# ):
#     """
#     Inverse the y-axis and plot the confusion matrix as a heatmap.
#     The predicted labels (in x-axis) is symboled with hat (^).
#     The plt object is passed to adjust the figure size

#     cm = sklearn.metrics.confusion_matrix(y_test, y_pred)


#     cm = np.random.randint(low=0, high=10, size=[3,4])
#     x: predicted labels
#     y: true_labels


#     kwargs:

#         "extend_ratio":
#             Determines how much the axes objects (not the fig object) are extended
#             in the vertical direction.

#     """

#     if (y_pred_proba is not None) and (y_pred is None):
#         y_pred = y_pred_proba.argmax(axis=-1)

#     assert (cm is not None) or ((y_true is not None) and (y_pred is not None))

#     if cm is None:
#         with scitex.context.suppress_output():
#             cm = sklearn_confusion_matrix(y_true, y_pred, labels=labels)
#             # cm = sklearn_confusion_matrix(y_true, y_pred)

#     bacc = calc_bACC_from_cm(cm)

#     title = f"{title} (bACC = {bacc})"

#     # Ensure all labels are present in the confusion matrix
#     if labels is not None:
#         full_cm = np.zeros((len(labels), len(labels)))
#         unique_true = np.unique(y_true)
#         unique_pred = np.unique(y_pred)
#         for i, true_label in enumerate(labels):
#             for j, pred_label in enumerate(labels):
#                 if true_label in unique_true and pred_label in unique_pred:
#                     full_cm[i, j] = cm[
#                         np.where(unique_true == true_label)[0][0],
#                         np.where(unique_pred == pred_label)[0][0],
#                     ]
#         cm = full_cm

#     # Dataframe
#     cm = pd.DataFrame(
#         data=cm,
#     ).copy()

#     # To LaTeX styles
#     if pred_labels is not None:
#         pred_labels = [scitex.str.to_latex_style(l) for l in pred_labels]
#     if true_labels is not None:
#         true_labels = [scitex.str.to_latex_style(l) for l in true_labels]
#     if labels is not None:
#         labels = [scitex.str.to_latex_style(l) for l in labels]
#     if sorted_labels is not None:
#         sorted_labels = [scitex.str.to_latex_style(l) for l in sorted_labels]

#     # Prediction Labels: columns
#     if pred_labels is not None:
#         cm.columns = pred_labels
#     elif (pred_labels is None) and (labels is not None):
#         cm.columns = labels

#     # Ground Truth Labels: index
#     if true_labels is not None:
#         cm.index = true_labels
#     elif (true_labels is None) and (labels is not None):
#         cm.index = labels

#     # Sort based on sorted_labels here
#     if sorted_labels is not None:
#         assert set(sorted_labels) == set(labels)
#         cm = cm.reindex(index=sorted_labels, columns=sorted_labels)

#     # Main
#     fig, ax = plt.subplots()
#     res = sns.heatmap(
#         cm,
#         annot=True,
#         annot_kws={"size": plt.rcParams["font.size"]},
#         fmt=".0f",
#         cmap="Blues",
#         cbar=False,
#         vmin=0,
#     )  # Here, don't plot color bar.

#     # Adds comma separator for the annotated int texts
#     for t in ax.texts:
#         t.set_text("{:,d}".format(int(t.get_text())))

#     # Inverts the y-axis
#     res.invert_yaxis()

#     # Makes the frame visible
#     for _, spine in res.spines.items():
#         spine.set_visible(False)

#     # Labels
#     ax.set_xlabel("Predicted label")
#     ax.set_ylabel("True label")
#     ax.set_title(title)

#     # Appearances
#     ax = scitex.plt.ax.extend(ax, x_extend_ratio, y_extend_ratio)
#     if cm.shape[0] == cm.shape[1]:
#         ax.set_box_aspect(1)
#         ax.set_xticklabels(
#             ax.get_xticklabels(),
#             rotation=label_rotation_xy[0],
#             fontdict={"verticalalignment": "top"},
#         )
#         ax.set_yticklabels(
#             ax.get_yticklabels(),
#             rotation=label_rotation_xy[1],
#             fontdict={"horizontalalignment": "right"},
#         )
#         # The size
#     bbox = ax.get_position()
#     left_orig = bbox.x0
#     width_orig = bbox.x1 - bbox.x0
#     g_x_orig = left_orig + width_orig / 2.0
#     width_tgt = width_orig * x_extend_ratio  # x_extend_ratio
#     dx = width_orig - width_tgt

#     # Adjusts the sizes of the confusion matrix and colorbar
#     if colorbar:
#         divider = make_axes_locatable(ax)  # Gets region from the ax
#         cax = divider.append_axes("right", size="5%", pad=0.1)
#         # cax = divider.new_horizontal(size="5%", pad=1, pack_start=True)
#         cax = scitex.plt.ax.shift(cax, dx=-dx * 2.54, dy=0)
#         fig.add_axes(cax)

#         """
#         axpos = ax.get_position()
#         caxpos = cax.get_position()

#         AddAxesBBoxRect(fig, ax, ec="r")
#         AddAxesBBoxRect(fig, cax, ec="b")

#         fig.text(
#             axpos.x0 + 0.01, axpos.y0 + 0.01, "after colorbar", weight="bold", color="r"
#         )

#         fig.text(
#             caxpos.x1 + 0.01,
#             caxpos.y1 - 0.01,
#             "cax position",
#             va="top",
#             weight="bold",
#             color="b",
#             rotation="vertical",
#         )
#         """

#         # Plots colorbar and adjusts the size
#         vmax = np.array(cm).max().astype(int)
#         norm = matplotlib.colors.Normalize(vmin=0, vmax=vmax)
#         cbar = fig.colorbar(
#             plt.cm.ScalarMappable(norm=norm, cmap="Blues"),
#             cax=cax,
#             # shrink=0.68,
#         )
#         cbar.locator = ticker.MaxNLocator(nbins=4)  # tick_locator
#         cbar.update_ticks()
#         # cbar.outline.set_edgecolor("#f9f2d7")
#         cbar.outline.set_edgecolor("white")

#     if spath is not None:
#         scitex.io.save(fig, spath)

#     return fig, cm


# def calc_bACC_from_cm(cm):
#     with scitex.context.suppress_output():
#         try:
#             per_class = np.diag(cm) / np.nansum(cm, axis=1)
#             bacc = round(np.nanmean(per_class), 3)
#         except:
#             bacc = np.nan
#         return bacc


# # def AddAxesBBoxRect(fig, ax, ec="k"):
# #     from matplotlib.patches import Rectangle

# #     axpos = ax.get_position()
# #     rect = fig.patches.append(
# #         Rectangle(
# #             (axpos.x0, axpos.y0),
# #             axpos.width,
# #             axpos.height,
# #             ls="solid",
# #             lw=2,
# #             ec=ec,
# #             fill=False,
# #             transform=fig.transFigure,
# #         )
# #     )
# #     return rect


# if __name__ == "__main__":

#     import sys

#     import matplotlib.pyplot as plt
#     import scitex
#     import numpy as np
#     import sklearn
#     from sklearn import datasets, svm
#     # from sklearn.metrics import plot_confusion_matrix
#     from sklearn.model_selection import train_test_split

#     sys.path.append(".")
#     import scitex

#     # https://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html#sphx-glr-auto-examples-model-selection-plot-confusion-matrix-py
#     # Imports some data to play with
#     iris = datasets.load_iris()
#     X = iris.data
#     y = iris.target
#     class_names = iris.target_names

#     # Splits the data into a training set and a test set
#     X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

#     # Runs classifier, using a model that is too regularized (C too low) to see
#     # the impact on the results
#     classifier = svm.SVC(kernel="linear", C=0.01).fit(X_train, y_train)

#     ## Checks the confusion_matrix function
#     y_pred = classifier.predict(X_test)
#     cm = sklearn.metrics.confusion_matrix(y_test, y_pred)
#     cm **= 3

#     fig, cm = conf_mat(
#         plt,
#         # y_true=y_test,
#         # y_pred=y_pred,
#         cm,
#         pred_labels=["A", "B", "C"],
#         true_labels=["a", "b", "c"],
#         label_rotation_xy=(60, 60),
#         x_extend_ratio=1.0,
#         colorbar=True,
#     )

#     fig.axes[-1] = scitex.plt.ax.sci_note(
#         fig.axes[-1],
#         fformat="%3.1f",
#         y=True,
#     )

#     plt.show()

#     ## EOF
