# 카메라 캘리브레이션 도구

OpenCV 기반의 카메라 캘리브레이션 도구입니다.

## 환경 구축

`python >= 3.8.9`

### 소스 다운로드

```bash
cd ~
mkdir dev && cd dev
git clone https://github.com/ProtossDragoon/CameraCalibration.git
```

### 가상환경 사용

가상환경 사용을 권장합니다.
```bash
mkdir venv
python3 -m venv venv/CameraCalibration
source venv/CameraCalibration/bin/activate
```

### 의존성 설치

의존성을 설치합니다.
```bash
cd CameraCalibration
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## 실행

### 빠른 실행

```bash
python3 main.py
```

하나의 영상마다 체커보드 검출 결과를 확인하고 싶은 경우 다음 커맨드를 실행합니다.
```bash
python3 main.py --imshow
```

프로젝트 폴더에는 기본적으로 Samsung Galaxy S22 로 촬영한 영상이 `./data/s22` 에 포함되어 있습니다. 이 폴더 내의 영상들은 매우 고해상도이므로 충분한 시간이 필요합니다.
```bash
python3 main.py --folder s22
```

여러 가지 옵션을 함께 사용할 수 있습니다.
```bash
python3 main.py --folder s22  --imshow
```

### 개인 데이터셋에서 실행

개인적으로 촬영한 영상들을 사용하고자 한다면, 다음 구조를 따라야 합니다. 아래 예시는 영상파일 확장자가 png 인 경우입니다. 물론 꼭 png 파일 형식일 필요는 없습니다. 주의해야 하는 경우는 다음과 같습니다.
- 하나, 모든 파일들은 data 폴더 내의 임의의 폴더 *(아래 예시에서는  `mynewfolder`)* 에 존재해야 합니다.
- 둘, 하나의 폴더 내의 모든 영상 파일들은 동일한 확장자를 가지고 있어야 합니다. *(아래 예시에서는  `png`)*
- 셋, 반드시 하나의 데이터 폴더는 `meta.json` 파일을 포함해야 합니다.
- 넷, 반드시 하나의 데이터 폴더 안에는 동일한 크기의 캘리브레이션 보드를 사용해야 합니다.
- 다섯, 반드시 하나의 데이터 폴더 안에는 동일한 캘리브레이션 보드를 사용한 영상들만 포함되어야 합니다.
- 여섯, 영상에서 캘리브레이션 보드의 일부가 잘려 있다면 해당 영상은 캘리브레이션에 반영되지 않습니다.
```python
├── data
│   ├── s22         # 기본 제공 데이터
│   ├── iphone13pro # 기본 제공 데이터
│   └── mynewfolder # 내가 준비한 커스텀 데이터
│       ├── your_image_1.png
│       ├── your_image_2.png
│       ├── your_image_3.png
│       ├── ... .png
│       └── meta.json # 반드시 작성해야 합니다
├── .gitignore
├── README.md
├── requirements.txt
└── ...
```

모두 준비되었다면 다음 커맨드를 실행시켜 주세요. 폴더명과 확장자명을 입력합니다.
```bash
python3 main.py --folder mynewfoler --ext png
```

## 결과

### 해석값

캘리브레이션 결과는 `/results/?/result.json` 에 작성됩니다.
```json
{
    // 3x3 카메라 행렬 값입니다.
    "camera_matrix": [  
        [
            2649.709918689493,
            0.0,
            2002.7645909877156
        ],
        [
            0.0,
            2657.693991678388,
            1495.2436863517078
        ],
        [
            0.0,
            0.0,
            1.0
        ]
    ],
    
    // 왜곡 계수입니다.
    "distortion_coefficients": [
        [
            0.11885108419782317,
            -0.25574773705723225,
            -0.0017853412358027896,
            0.0004818148578685535,
            0.24677351076478649
        ]
    ],

    // 하나의 영상마다 각각 rotation 값을 연산합니다.
    // 캘리브레이션에 사용된 영상에 대응되는 값입니다.
    "rotation_vectors": [
        {
            "./data/s22/2022-06-01-13-49-21_001.jpeg": [
                [
                    0.3012948960067235
                ],
                [
                    -0.041529633298368736
                ],
                [
                    0.25841686651373963
                ]
            ]
        },
        ...
    ]
    ...

    // 하나의 영상마다 각각 translation 값을 연산합니다.
    // 캘리브레이션에 사용된 영상에 대응되는 값입니다.
    "translation_vectors": [
        {
            "./data/s22/2022-06-01-13-49-21_001.jpeg": [
                [
                    -63.44776067646983
                ],
                [
                    -125.50650277054721
                ],
                [
                    389.8281745178708
                ]
            ]
        },
    ...
    ]
}
```

### 테스트 환경

- [x] Apple MacBook Pro 2022 16inch (Apple M1 Pro)
