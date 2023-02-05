import numpy as np
import matplotlib.pyplot as plt
import lane_detection as LD
import cv2

steer_list=np.arange(-2,3,1)

def poly_eval(coeffs, x):
    y = 0
    for i, c in enumerate(coeffs):
        y += c * x ** i
    return y
def pure_pursuit(coeffs, current_pos, lookahead_distance, num_points=100):
    # Generate the path by evaluating the polynomial
    x = np.linspace(0, 10, num_points)
    y = poly_eval(coeffs, -1*x+1080)
    path = np.column_stack((x, y))

    # Find the closest point on the path to the current position
    dists = np.linalg.norm(path - current_pos, axis=1)
    closest_index = np.argmin(dists)

    # Find the point on the path lookahead_distance ahead of the closest point
    lookahead_index = closest_index + int(lookahead_distance / dists[closest_index])
    lookahead_index = np.clip(lookahead_index, 0, len(path) - 1)
    lookahead_point = path[lookahead_index, :]

    # Compute the steering angle to steer towards the lookahead point
    steering_angle = np.arctan2(lookahead_point[1] - current_pos[1],
                                lookahead_point[0] - current_pos[0])
    steering_angle = steering_angle * 180 / np.pi
    return steering_angle


if __name__ == '__main__':
    lane_detection = LD.libLANE()
    image = cv2.imread('./record/30_11-52-16.jpg')
    result, path_coeffs = lane_detection.add_lane(image,2)
    path_coeffs = path_coeffs[::-1]

    cv2.imshow('re', result)
    cv2.waitKey(0)

    current_pos = np.array([0, poly_eval(path_coeffs, 1080)])
    lookahead_distance = 1

    # steering_angle = pure_pursuit(path_coeffs, current_pos, lookahead_distance)
    # print(steering_angle)

    # Plot
    # plt.figure(figsize=(9,16))
    x = np.linspace(0, 1080, 100)
    # x = -1 * np.linspace(0, 1080, 100) + 1080
    y = poly_eval(path_coeffs, -1*x+1080)
    plt.plot(x, y, '-k')
    plt.plot(current_pos[0], current_pos[1], 'ro')
    plt.show()
