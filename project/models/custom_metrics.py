from tensorflow.keras import backend as K

def f1_score(y_true, y_pred):
    """
    Hàm tính toán F1 Score cho phân đoạn ảnh.

    Args:
    y_true: Mảng numpy chứa nhãn thực tế.
    y_pred: Mảng numpy chứa dự đoán.

    Returns:
    f1: Giá trị F1 Score.
    """
    # Chuyển đổi tensor thành vector
    y_true = K.flatten(y_true)
    y_pred = K.flatten(y_pred)

    # Tính toán TP, FP, FN
    true_positives = K.sum(y_true * y_pred)
    predicted_positives = K.sum(y_pred)
    possible_positives = K.sum(y_true)

    # Tính toán Precision và Recall
    precision = true_positives / (predicted_positives + K.epsilon())
    recall = true_positives / (possible_positives + K.epsilon())

    # Tính toán F1 Score
    f1 = 2 * (precision * recall) / (precision + recall + K.epsilon())

    return f1


def iou_score(y_true, y_pred):
    """
    Hàm tính toán IoU (Intersection over Union) cho phân đoạn ảnh.

    Args:
    y_true: Mảng numpy chứa nhãn thực tế.
    y_pred: Mảng numpy chứa dự đoán.

    Returns:
    iou: Giá trị IoU.
    """
    # Chuyển đổi tensor thành vector
    y_true = K.flatten(y_true)
    y_pred = K.flatten(y_pred)

    # Tính toán các giá trị giao (intersection) và hợp (union)
    intersection = K.sum(y_true * y_pred)
    union = K.sum(y_true) + K.sum(y_pred) - intersection

    # Tính toán IoU
    iou = intersection / (union + K.epsilon())

    return iou
