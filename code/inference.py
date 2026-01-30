import json, os, sys, logging, io
import boto3
import numpy as np
import torch
import torch.nn.functional as F
import rasterio
from rasterio.windows import Window
from rasterio.enums import Resampling
import rasterio.warp
import cv2
from ultralytics import YOLO
from tqdm import tqdm

# 로거 및 기본 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 모델별 파라미터 및 고정값
MARIDA_MEAN = np.array([0.04484, 0.040945, 0.035334, 0.026897, 0.025076, 0.030968, 0.036087, 0.031758, 0.036754, 0.020314, 0.012555])
MARIDA_STD = np.array([0.007779, 0.009267, 0.010079, 0.010695, 0.010957, 0.018102, 0.022499, 0.021355, 0.024844, 0.014343, 0.008926])
TARGET_ORDER = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B11', 'B12']
BLOCK_SIZE = 1024


# --- SageMaker 핸들러 ---

def model_fn(model_dir):
    logger.info("모든 모델 로딩 시작...")
    models = {}
    from unet import UNet # code/unet.py 에서 클래스 가져오기
    unet_model = UNet(input_bands=11, output_classes=11, hidden_channels=16)
    unet_model.load_state_dict(torch.load(os.path.join(model_dir, "model.pth"), map_location=DEVICE), strict=False)
    models['unet'] = unet_model.to(DEVICE).eval()
    models['yolo_ship'] = YOLO(os.path.join(model_dir, "yolo_ship.pt"))
    models['yolo_debris'] = YOLO(os.path.join(model_dir, "yolo_debris.pt"))
    logger.info("모든 모델 로딩 완료.")
    return models

def input_fn(request_body, request_content_type):
    if request_content_type == 'application/json':
        data = json.loads(request_body)
        job_id = data.get('job_id')
        if not job_id: raise ValueError("요청에 'job_id'가 없습니다.")
        return job_id
    raise ValueError(f"지원하지 않는 Content-Type: {request_content_type}")

def predict_fn(job_id, models):
    logger.info(f"분석 시작: Job ID = {job_id}")
    BUCKET = 'jeju-guardian-satellite-data'
    PREFIX = f'input/{job_id}'
    WORK_DIR = f'/tmp/{job_id}'
    BANDS_DIR = os.path.join(WORK_DIR, 'bands')
    os.makedirs(BANDS_DIR, exist_ok=True)
    
    # 1. S3에서 밴드 파일 다운로드
    s3_client = boto3.client('s3')
    list_response = s3_client.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)
    for obj in list_response.get('Contents', []):
        if obj['Key'].endswith('.jp2'):
            local_path = os.path.join(BANDS_DIR, os.path.basename(obj['Key']))
            s3_client.download_file(BUCKET, obj['Key'], local_path)
    logger.info(f"밴드 파일 다운로드 완료.")

    # 2. 밴드 병합
    stacked_tif_path = os.path.join(WORK_DIR, 'input_stack.tif')
    stack_bands(BANDS_DIR, stacked_tif_path, TARGET_ORDER)
    logger.info(f"밴드 병합 완료.")
    
    all_detections = []
    with rasterio.open(stacked_tif_path) as src:
        all_detections.extend(run_unet_inference(src, models['unet']))
        all_detections.extend(run_yolo_inference(src, models['yolo_ship'], 'ship', 0.3))
        all_detections.extend(run_yolo_inference(src, models['yolo_debris'], 'debris', 0.1))

    logger.info(f"전체 분석 완료. 총 {len(all_detections)}개 객체 탐지.")
    return all_detections

def output_fn(detections, content_type):
    return json.dumps({"detections": detections}), content_type


# --- 분석 헬퍼 함수 (노트북 코드 통합) ---

def get_lat_lon(global_x, global_y, src):
    try:
        x_crs, y_crs = src.xy(global_y, global_x)
        lon, lat = rasterio.warp.transform(src.crs, {'init': 'epsg:4326'}, [x_crs], [y_crs])
        return lat[0], lon[0]
    except Exception: return 0.0, 0.0

def stack_bands(input_folder, output_filename, target_order):
    all_files = os.listdir(input_folder)
    file_map = {band: os.path.join(input_folder, f) for band in target_order for f in all_files if f.endswith(f'{band}.jp2')}
    if len(file_map) != 11: raise FileNotFoundError("11개 밴드 파일을 모두 찾지 못했습니다.")

    with rasterio.open(file_map['B02']) as src:
        ref_meta = src.meta.copy()
        ref_width, ref_height = src.width, src.height
    ref_meta.update(count=11, driver='GTiff', tiled=True, blockxsize=256, blockysize=256)

    with rasterio.open(output_filename, 'w', **ref_meta) as dst:
        for col_off in tqdm(range(0, ref_width, BLOCK_SIZE), desc="Stacking Bands"):
            for row_off in range(0, ref_height, BLOCK_SIZE):
                width, height = min(BLOCK_SIZE, ref_width - col_off), min(BLOCK_SIZE, ref_height - row_off)
                window = Window(col_off, row_off, width, height)
                for i, band_name in enumerate(target_order):
                    with rasterio.open(file_map[band_name]) as src:
                        if src.width != ref_width:
                            scale_x, scale_y = src.width / ref_width, src.height / ref_height
                            src_window = Window(col_off * scale_x, row_off * scale_y, width * scale_x, height * scale_y)
                            data = src.read(1, window=src_window, out_shape=(height, width), resampling=Resampling.bilinear)
                        else:
                            data = src.read(1, window=window)
                        dst.write(data, window=window, indexes=i + 1)

def run_unet_inference(src, model):
    logger.info("U-Net 추론 시작...")
    detections = []
    h, w = src.height, src.width
    win = 512
    for y in range(0, h, win):
        for x in range(0, w, win):
            cw, ch = min(win, w - x), min(win, h - y)
            if cw < 64 or ch < 64: continue
            
            window = rasterio.windows.Window(x, y, cw, ch)
            img_raw = src.read(window=window)
            img_norm = img_raw.astype(np.float32) / 10000.0
            img_std = (img_norm - MARIDA_MEAN.reshape(-1, 1, 1)) / (MARIDA_STD.reshape(-1, 1, 1) + 1e-8)
            
            ph, pw = (32 - ch%32)%32, (32 - cw%32)%32
            img_pad = np.pad(img_std, ((0,0),(0,ph),(0,pw)), 'constant')
            t = torch.from_numpy(img_pad).float().unsqueeze(0).to(DEVICE)
            
            with torch.no_grad():
                out = model(t)
                probs = F.softmax(out, dim=1).squeeze().cpu().numpy()[:, :ch, :cw]

            targets = [(4, "ship"), (0, "debris")] # ID_SHIP, ID_DEBRIS
            for cid, label in targets:
                mask = (probs[cid] > 0.05).astype(np.uint8)
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for c in cnts:
                    if cv2.contourArea(c) < 3: continue
                    M = cv2.moments(c);
                    if M["m00"] == 0: continue
                    cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                    lat, lon = get_lat_lon(x + cx, y + cy, src)
                    detections.append({"class": f"unet_{label}", "lat": lat, "lon": lon, "conf": probs[cid, cy, cx]})
    return detections

def run_yolo_inference(src, model, object_type, conf_thresh):
    logger.info(f"YOLO ({object_type}) 추론 시작...")
    detections = []
    h, w = src.height, src.width
    win = 640
    for y_off in range(0, h, win):
        for x_off in range(0, w, win):
            cw, ch = min(win, w - x_off), min(win, h - y_off)
            if cw < 64 or ch < 64: continue
            
            img_bands = src.read([4, 3, 2], window=rasterio.windows.Window(x_off, y_off, cw, ch))
            img_16bit = img_bands.transpose(1, 2, 0).astype(np.float32)
            img_8bit = np.clip((img_16bit / 3000.0) * 255.0, 0, 255).astype(np.uint8)
            img_bgr = cv2.cvtColor(img_8bit, cv2.COLOR_RGB2BGR)

            results = model(img_bgr, conf=conf_thresh, verbose=False)
            if results[0].boxes is not None:
                for box in results[0].boxes.data.cpu().numpy():
                    x1, y1, x2, y2, conf, cls_id = box
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                    lat, lon = get_lat_lon(x_off + cx, y_off + cy, src)
                    detections.append({"class": f"yolo_{object_type}", "lat": lat, "lon": lon, "conf": conf})
    return detections
