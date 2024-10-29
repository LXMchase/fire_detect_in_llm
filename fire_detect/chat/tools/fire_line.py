# -*- coding: utf-8 -*-
import cv2
import numpy as np
from skimage.filters import threshold_multiotsu
from sklearn.cluster import KMeans
import os

def process_image_otsu(image_path, histogram_folder='', width=50):
    """
    处理单张图像，检测火焰并绘制燃烧线。

    :param image_path: (str) 要处理的图像的路径。
    :param histogram_folder: (str) 保存直方图的文件夹路径，默认为空字符串。
    :param width: (int) 判断有效火焰区域所需的最小宽度，默认为50。
    :return: (np.ndarray) 处理后的图像，包括绘制的燃烧线。
    """
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray_image = image_rgb[:, :, 1]
    thresholds = threshold_multiotsu(gray_image, classes=4)
    regions = np.digitize(gray_image, bins=thresholds)
    # 要提取的类（例如类2）
    class_to_extract = 3

    # 创建一个掩码，提取指定类的区域
    mask = (regions == class_to_extract)

    # 创建一个全黑的图像
    extracted_region = np.zeros_like(gray_image)

    # 将提取的区域赋值到黑图像中
    extracted_region[mask] = gray_image[mask]

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(extracted_region)

    min_area = width**2  # 设定最小的区域面积
    large_regions_mask = np.zeros_like(extracted_region)

    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            large_regions_mask[labels == i] = 255

    output_image = image.copy()

    coordinates = []

    for j in range(large_regions_mask.shape[1]):
        for i in range(large_regions_mask.shape[0] - 1, -1, -1):
            if large_regions_mask[i, j] == 255:
                if i < large_regions_mask.shape[0] - 1 and large_regions_mask[i + 1, j] == 0:
                    y = large_regions_mask.shape[0] - 1 - i  # 转换 y 坐标
                    coordinates.append((j, y))  # Store (x, y) coordinates
                break

    # 将 coordinates 转换为 NumPy 数组
    coordinates_np = np.array(coordinates)

    # 只使用 y 坐标进行聚类
    y_coords = coordinates_np[:, 1].reshape(-1, 1)  # 提取 y 坐标并调整形状

    # 使用 KMeans 进行聚类
    kmeans = KMeans(n_clusters=1)
    kmeans.fit(y_coords)

    # 获取聚类标签和中心
    labels = kmeans.labels_
    cluster_center = kmeans.cluster_centers_[0]

    # 计算每个点与聚类中心的距离
    distances = np.abs(y_coords - cluster_center).flatten()

    mean_distance = np.mean(distances)
    std_distance = np.std(distances)
    threshold = mean_distance + 0.1 * std_distance  # 使用均值加0.1倍标准差

    # 提取非离群点
    inliers = coordinates_np[distances <= threshold]

    # 在图像上绘制剩余的点
    for (x, y) in inliers:
        cv2.circle(output_image, (x, large_regions_mask.shape[0] - 1 - y), 1, (0, 0, 255), -1)

    # 将提取的区域转换为三维数组
    extracted_region_colored = cv2.cvtColor(extracted_region, cv2.COLOR_GRAY2BGR)

    # 水平堆叠
    combined_image = np.hstack((extracted_region_colored, output_image))
    # 定义保存路径
    combined_image_path = os.path.join('../../media', 'combined_image.png')

    # 保存合成图像
    combined_image.save(combined_image_path)
    return combined_image

