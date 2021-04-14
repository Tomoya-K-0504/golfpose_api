from pathlib import Path
import time

import cv2
import numpy as np
import tensorflow as tf

import posenet


def set_window():
    cv2.namedWindow('swing', cv.WINDOW_NORMAL)
    cv2.resizeWindow('swing', 550, 900)
    cv2.moveWindow('swing', 600, 30)


def init_video_write(cap, video_path):
    ret, frame = cap.read()
    w, h = frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 30.0
    out_file = '/'.join(video_path.split('/')[:-1]) + '/output_' + video_path.split('/')[-1]
    dst = cv2.VideoWriter(out_file, fourcc, fps, (w, h))
    return dst


def process(video_path):
    cap = cv2.VideoCapture(video_path)
    dst = init_video_write(cap, video_path)
    keypoint_list = []

    with tf.Session() as sess:
        model_cfg, model_outputs = posenet.load_model(101, sess)
        output_stride = model_cfg['output_stride']

        # cap.set(3, args.cam_width)
        # cap.set(4, args.cam_height)

        scale_factor = 0.7125

        start = time.time()
        frame_count = 0
        while True:
            res, img = cap.read()
            if not res:
                break
            input_image, display_image, output_scale = posenet.read_cap(
                img, scale_factor=scale_factor, output_stride=output_stride)

            heatmaps_result, offsets_result, displacement_fwd_result, displacement_bwd_result = sess.run(
                model_outputs,
                feed_dict={'image:0': input_image}
            )

            pose_scores, keypoint_scores, keypoint_coords = posenet.decode_multi.decode_multiple_poses(
                heatmaps_result.squeeze(axis=0),
                offsets_result.squeeze(axis=0),
                displacement_fwd_result.squeeze(axis=0),
                displacement_bwd_result.squeeze(axis=0),
                output_stride=output_stride,
                max_pose_detections=10,
                min_pose_score=0.15)

            keypoint_coords *= output_scale
            keypoint_list.append(keypoint_coords[0])

            # TODO this isn't particularly fast, use GL for drawing and display someday...
            overlay_image = posenet.draw_skel_and_kp(
                display_image, pose_scores, keypoint_scores, keypoint_coords,
                min_pose_score=0.15, min_part_score=0.1)

#             cv2.imshow('posenet', overlay_image)
            dst.write(overlay_image)
            frame_count += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    print('Average FPS: ', frame_count / (time.time() - start))
                
    dst.release()
    cap.release()
    cv2.destroyAllWindows()
    np.save(Path('/'.join(video_path.split('/')[:-1])) / 'keypoints.npy', np.stack(keypoint_list))
    return str(Path('/'.join(video_path.split('/')[:-1])) / 'keypoints.npy')


if __name__ == "__main__":
    video_path = '/Users/koiketomoya/workspace/playground/golf_pose/app/short_video.mp4'
    print(process(video_path))