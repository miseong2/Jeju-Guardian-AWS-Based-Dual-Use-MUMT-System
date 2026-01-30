import sagemaker
from sagemaker.pytorch import PyTorchModel
from sagemaker import get_execution_role
import tarfile
import os

ENDPOINT_NAME = 'Jeju-Guardian-Smart-Endpoint'
INSTANCE_TYPE = 'ml.g4dn.xlarge'

def main():
    sagemaker_session = sagemaker.Session()
    role = get_execution_role()
    bucket = sagemaker_session.default_bucket()
    prefix = 'Jeju-Guardian/model-artifacts'
    
    print(f"SageMaker Role: {role}\nSageMaker Bucket: {bucket}/{prefix}")

    # 배포할 모든 파일을 model.tar.gz로 압축
    source_dir = 'code'
    model_files = ['model.pth', 'yolo_ship.pt', 'yolo_debris.pt']
    output_filename = 'model.tar.gz'

    print(f"\n'{output_filename}' 생성 중...")
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
        for model_file in model_files:
            if os.path.exists(model_file):
                tar.add(model_file)
                print(f" - {model_file} 추가됨")
            else:
                raise FileNotFoundError(f"모델 파일 '{model_file}'이 없습니다!")
    
    model_artifact_s3_path = sagemaker_session.upload_data(path=output_filename, key_prefix=prefix)
    print(f"\n모델 아티팩트 S3 업로드 완료: {model_artifact_s3_path}")

    pytorch_model = PyTorchModel(
        model_data=model_artifact_s3_path,
        role=role,
        entry_point='inference.py',
        source_dir='code',
        framework_version='2.0.1', # 최신 안정 버전 권장
        py_version='py310'
    )

    print(f"\n'{ENDPOINT_NAME}' 엔드포인트 배포를 시작합니다 (약 5-10분 소요)...")
    predictor = pytorch_model.deploy(
        initial_instance_count=1,
        instance_type=INSTANCE_TYPE,
        endpoint_name=ENDPOINT_NAME,
        # 기존 엔드포인트가 있으면 업데이트 (무중단 배포)
        update_endpoint=True
    )
    print(f"\n✅ 배포 성공! 엔드포인트 '{predictor.endpoint_name}'가 활성화되었습니다.")

if __name__ == "__main__":
    main()
