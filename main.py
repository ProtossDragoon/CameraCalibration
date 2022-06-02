# 표준 lib
import json
import glob
import os
import logging
import argparse

# 서드파티 lib
import numpy as np
import cv2 as cv


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# - - -
def parse_args():
    parser = argparse.ArgumentParser(description='캘리브레이션 도구')
    parser.add_argument('--imshow', action='store_true', help='체커보드 영상에서 검출된 패턴을 시각화하는 윈도우를 보입니다.')
    parser.add_argument('--folder', default='iphone13pro', help='체커보드 영상들이 포함된 폴더명을 작성합니다. `./data` 의 하위 디렉터리여야만 합니다.')
    parser.add_argument('--ext', default='jpeg', help='이미지파일의 확장자입니다.')
    args = parser.parse_args()
    return args

# - - -
def get_image_path_li(dir, ext):
    path = os.path.join(f'{dir}', f'*.{ext}')
    path_li = glob.glob(path)
    return sorted(path_li)

def get_metadata(dir, json_name):
    p = os.path.join(f'{dir}', f'{json_name}.json')
    with open(p) as f:
        dict = json.load(f)
    return dict

def save_result_image(image, dir, image_name):
    os.makedirs(dir, exist_ok=True)
    cv.imwrite(os.path.join(dir, image_name), image)

def save_result_calibration(dir, dict, json_name='result'):
    p = os.path.join(f'{dir}', f'{json_name}.json')
    with open(p, 'w') as f:
        json.dump(dict, f, cls=NumpyEncoder, indent=4, sort_keys=True)
    return p

# - - -
def get_checkerboard_points_on_world_coordinate(
    checkerboard_number_of_rows:int=None,
    checkerboard_number_of_columns:int=None,
    checkerboard_tile_width:float=1.,
    checkerboard_tile_height:float=1.,
):
    r = checkerboard_number_of_rows
    c = checkerboard_number_of_columns
    frame = np.zeros((r*c,3), np.float32)
    frame[:,:2] = np.mgrid[0:r,0:c].T.reshape(-1,2)
    frame[:, 0] *= checkerboard_tile_height
    frame[:, 1] *= checkerboard_tile_width
    return frame

# - - -
def calibrate(
    checkerboard_points_on_pixel_coordinate:list, 
    checkerboard_points_on_world_coordinate:list,
    image_pixel_width:int,
    image_pixel_height:int
):
    assert (
        len(checkerboard_points_on_pixel_coordinate) 
        == len(checkerboard_points_on_world_coordinate)
    )
    ret = (
        res, 
        camera_matrix,
        distortion_coefficients, 
        rotation_vectors,
        translation_vectors
    ) = cv.calibrateCamera(
        checkerboard_points_on_world_coordinate, 
        checkerboard_points_on_pixel_coordinate, 
        (image_pixel_height, image_pixel_width), 
        None, None
    )
    return ret

# - - -
def main(imshow, folder, ext):
    logging.basicConfig(level=logging.INFO)
    checkerboard_finding_successd = []
    checkerboard_finding_failed = []
    checkerboard_points_on_pixel_coordinate = []
    checkerboard_points_on_world_coordinate = []

    S22 = 's22'
    IPHONE13PRO = 'iphone13pro'

    image_path_li = get_image_path_li(f'./data/{folder}', f'{ext}')
    meta = get_metadata(f'./data/{folder}', 'meta')

    for image_path in image_path_li:
        _, filename = os.path.split(image_path)
        logging.info(f'사진 {image_path} 을 불러오고 있습니다.')
        color_image = cv.imread(image_path)
        gray_image = cv.cvtColor(color_image, cv.COLOR_BGR2GRAY)

        logging.info('촬영된 체커보드에서 코너를 검출하고 있습니다.')
        pattern_shape = (meta['board']['n_cols']-1, meta['board']['n_rows']-1)
        # 코너를 검출하지 못할수도 있기 때문에 빠르게 확인
        res, _ = cv.findChessboardCorners(gray_image, pattern_shape, None, cv.CALIB_CB_FAST_CHECK)
        if res:
            _, corners = cv.findChessboardCorners(gray_image, pattern_shape, None)
            cv.drawChessboardCorners(color_image, pattern_shape, corners, res)
            logging.info('코너를 검출했습니다.')
            checkerboard_finding_successd.append(image_path)
            save_result_image(color_image, f'./results/data/{folder}', f'{filename}')
            logging.info('검출 이미지를 저장했습니다.')
            if imshow:
                logging.info('\'q\' 키를 눌러 다음 이미지를 확인하세요.')
                cv.imshow(f'{filename}', color_image)
                cv.waitKey(0)
                cv.destroyAllWindows()
            checkerboard_points_on_pixel_coordinate.append(corners)
            checkerboard_points_on_world_coordinate.append(
                get_checkerboard_points_on_world_coordinate(
                    pattern_shape[0], pattern_shape[1],
                    meta['board']['width'], meta['board']['height']
                )
            )
        else:
            logging.info('코너 검출에 실패했습니다!')
            checkerboard_finding_failed.append(image_path)

    logging.info(f'체커보드 검출 성공({len(checkerboard_finding_successd)})...')
    logging.info(f'체커보드 검출 실패({len(checkerboard_finding_failed)}):{checkerboard_finding_failed}')
    logging.info('캘리브레이션을 수행하고 있습니다.')
    res, *etc = calibrate(
        checkerboard_points_on_pixel_coordinate,
        checkerboard_points_on_world_coordinate,
        image_pixel_width=gray_image.shape[1], 
        image_pixel_height=gray_image.shape[0]
    )
    if res:
        logging.info('캘리브레이션 성공!')
        d = {}
        for idx, e in enumerate(etc):
            if idx == 0:
                d['camera_matrix'] = e
                logging.info(f'Camera matrix: {e.shape}\n{e}')
            if idx == 1:
                d['distortion_coefficients'] = e
                logging.info(f'Distortion coefficients: {e.shape}\n{e}')
            if idx == 2:
                d['rotation_vectors'] = []
                logging.info(f'Rotation vectors:')
                for image_path, r in zip(checkerboard_finding_successd, e):
                    d['rotation_vectors'].append({f'{image_path}':r})
                    logging.info(f'{image_path}:\n{r}')
            if idx == 3:
                d['translation_vectors'] = []
                logging.info(f'Translation vectors:')
                for image_path, t in zip(checkerboard_finding_successd, e):
                    d['translation_vectors'].append({f'{image_path}':t})
                    logging.info(f'{image_path}:\n{t}')
        p = save_result_calibration(f'./results/data/{folder}', d)
        logging.info(f'캘리브레이션을 결과물을 {p} 에 저장했습니다.')
    else:
        logging.info('캘리브레이션 실패!')
    cv.destroyAllWindows()


if __name__ == '__main__':
    args = parse_args()
    main(args.imshow, args.folder, args.ext)