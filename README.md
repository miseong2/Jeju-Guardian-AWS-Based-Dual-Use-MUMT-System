# 🛡️ Jeju Guardian: AWS-based Dual-Use MUMT System
> **AWS 기반 지능형 유무인 복합 체계: 해양 안보 및 환경 위기 통합 대응 솔루션**

[![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Unity](https://img.shields.io/badge/Unity-000000?style=for-the-badge&logo=unity&logoColor=white)](https://unity.com/)
[![NVIDIA](https://img.shields.io/badge/NVIDIA-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://www.nvidia.com/)

## 🌊 Overview
**Jeju Guardian**은 제주 해역의 불법 어선(Security)과 해양 쓰레기(Environment) 문제를 단일 플랫폼으로 해결하는 **민군 겸용 자율 관제 솔루션**입니다. AWS 클라우드 인프라와 MARL(다중 에이전트 강화학습)을 결합하여, 하드웨어 변경 없이 소프트웨어 전환만으로 미션을 수행하는 혁신적인 MUM-T(유무인 복합 체계)를 지향합니다.

---

## ✨ Key Strategy: Problem Isomorphism
* **탐지의 동형성**: 레이더 반사 면적이 작은 목선과 부유 쓰레기를 식별하는 동일한 신호처리 로직 적용.
* **제어의 동형성**: 적을 차단하는 기동(Blocking)과 쓰레기를 포집하는 기동(Corraling)을 동일한 동역학 모델 위에서 구현.

---

## 👥 Core Team & Roles (Guardians)

### 👑 양범석 (Project Manager & Lead Developer)
* **핵심 임무**: Unity 3D 디지털 트윈 구축 및 Full-Cycle 통합 관제 웹 개발
* **상세 과업**: 
    * **고정밀 시뮬레이션**: DWP2 에셋 기반 실해역 물리 환경 구축 및 3-DOF USV 동역학 구현.
    * **임무 최적화**: Dec-POMDP 프레임워크 상에서 가변 보상 함수($R_{total}$) 및 가중치($\omega$) 조절 알고리즘 설계.
    * **통합 대시보드**: 지도 기반 UI 상에 USV 좌표, 상태 로그, 실시간 영상 스트리밍 시각화.
* **Mission**: Unity 3D 강화학습 모델 개발 및 시스템 통합 웹 애플리케이션 완성.

### 👁️ 김미성 (AI & Vision Specialist)
* **핵심 임무**: YOLOv8 모델 최적화 및 엣지 배포
* **상세 과업**:
    * **객체 탐지**: 위성 이미지 및 USV 카메라 피드를 활용한 Dark Fleet 및 해양 쓰레기 식별 모델 학습.
    * **모델 최적화**: Amazon SageMaker 관리 및 Jetson Orin Nano용 TensorRT 가속화 수행.
    * **데이터 처리**: 탐지 객체의 정밀 좌표 추출 및 시스템 피드백 루프 구축.
* **Mission**: 공개 위성 데이터를 활용한 베이스라인 측정 후, 제공 데이터 기반의 고정밀 탐지 모델 완성.

### ☁️ 송한결 (Cloud & Data Engineer)
* **핵심 임무**: AWS 기반 Event-Driven 데이터 파이프라인 구축
* **상세 과업**: 
    * **데이터 전처리**: AWS Ground Station 수신 데이터(HDF5)의 GeoTIFF 포맷 변환 자동화.
    * **워크플로우 설계**: EventBridge & Lambda 연동을 통한 분석 파이프라인 자동 트리거 시스템 구축.
    * **실시간 통신**: AWS IoT Core(MQTT) 기반 관제 센터-엣지 기기 간 초고속 데이터 송수신 관리.
* **Mission**: 프로젝트 활용 AWS 서비스 조사 및 기술 공유, 전반적인 클라우드 아키텍처 안정화.

### 🚤 한정훈 (Embedded & System Integrator)
* **핵심 임무**: Edge 실행 환경 및 MUM-T 통신 프로토콜 구현
* **상세 과업**: 
    * **엣지 컴퓨팅**: Jetson Orin Nano 상에 AWS IoT Greengrass 인프라 구축 및 로컬 제어 루프 확보.
    * **표준 프로토콜**: STANAG 4586 기반 유무인 협업 통신 지원 및 자율 기동 로직 실장.
    * **경로 가시화**: A* 알고리즘 결과값을 웹 관제 UI 상의 Waypoint 경로로 렌더링 지원.
* **Mission**: Jetson Orin Nano 하드웨어 셋팅 및 자율 운항 경로 생성 알고리즘 검증.

---

## 🛠 Tech Stack
* **Cloud**: AWS (Ground Station, S3, SageMaker, IoT Core, Greengrass, Lambda)
* **Intelligence**: YOLOv8, MARL, A* Pathfinding
* **Frameworks**: Unity 3D (ML-Agents), React/Node.js, TensorRT
* **Hardware**: NVIDIA Jetson Orin Nano

---
© 2026 Team Guardians. National Korea Maritime & Ocean University.
