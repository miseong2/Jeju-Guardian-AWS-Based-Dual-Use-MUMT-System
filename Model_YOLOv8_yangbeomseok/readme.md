# 🛰️ YOLOv8 학습 샘플

이 프로젝트는 AI 허브의 광학 위성 영상 데이터를 활용하여 해상 선박을 정밀하게 탐지하고, 선박의 크기에 따라 대형(Ship-L)과 소형(Ship-S)으로 분류하는 고성능 객체 탐지 시스템입니다.

## 🚀 Key Features
- **OBB(Oriented Bounding Box) 적용**: 선박의 회전 각도에 최적화된 회전 박스 탐지 기술을 적용하여 밀집된 항구 내에서도 개별 선박을 정밀하게 식별합니다.
- **Resource-Efficient Training**: GPU가 없는 환경에서 Intel i7-12700 CPU 최적화를 통해 50 Epoch 학습을 완수하고 mAP 0.9 이상의 높은 성능을 달성했습니다.
- **Real-world Validation**: 학습 데이터 외에 구글 어스(Google Earth) 실전 데이터를 활용하여 모델의 범용성을 검증했습니다.

## 📊 Performance Metric (mAP@0.5)
- **All Classes**: 0.902 (90.2%)
- **Ship-Small**: 0.915
- **Ship-Large**: 0.890
- **Inference Speed**: 86.9ms/image (CPU)

<img width="2400" height="1200" alt="Image" src="https://github.com/user-attachments/assets/9b4dc79b-ae32-467d-9502-dd4819f51362" />
<img width="2250" height="1500" alt="Image" src="https://github.com/user-attachments/assets/ad5ae080-28f2-400e-9696-203588fcbe0c" />

## 📁 Directory Structure
- `Ship-Detection-AI/`: 데이터 전처리(`data_process.py`) 및 학습(`train.py`) 소스 코드
- `Runs/`: 학습 성적표(PR Curve) 및 최적 가중치(`best.pt`)
- `yolo_ship_dataset/`: 모델 학습을 위한 YAML 설정 파일

## 🛠️ Tech Stack
- **Model**: YOLOv8-OBB (Nano)
- **Framework**: PyTorch, Ultralytics
- **Environment**: Python 3.11, CPU-based Optimization

## 🚢 Detection Samples (Example)
![Detection Result](https://github.com/miseong2/Jeju-Guardian-AWS-Based-Dual-Use-MUMT-System/raw/main/Ship-Detection-AI/result_sample.png)
> *Note: 구글 어스를 통한 실제 항구 데이터 탐지 결과 (텍스트 라벨 제외 시각화)*

---
**Contact**: 국립한국해양대학교 인공지능공학부 범석 (beomseok@kmou.ac.kr)
