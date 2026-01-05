import json
import os
from tqdm import tqdm

def transform_to_yolo_obb(json_path, output_path):
    """
    AI Hub Polygon(JSON) data -> YOLOv8-OBB(TXT) 8-point format
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    yolo_labels = []
    
    # AI Hub Feature parsing
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        label = props.get('object_class')
        
        # Class mapping (0: Ship-L, 1: Ship-S)
        if label in ['ship-L', 'ship-S']:
            cls_id = 0 if label == 'ship-L' else 1
            
            # Extract 4 vertices for OBB
            coords = feature.get('geometry', {}).get('coordinates', [[]])[0]
            
            # Flatten 4 points into 8 values (x1 y1 x2 y2 x3 y3 x4 y4)
            points = []
            for p in coords[:4]:
                points.extend([str(p[0]), str(p[1])])
            
            if len(points) == 8:
                yolo_labels.append(f"{cls_id} " + " ".join(points))

    if yolo_labels:
        with open(output_path, 'w') as f:
            f.write("\n".join(yolo_labels))
        return True
    return False

def main():
    # Path configuration
    source_dir = './raw_labels'  # AI Hub JSON folder
    target_dir = './yolo_labels' # Output TXT folder
    
    os.makedirs(target_dir, exist_ok=True)

    files = [f for f in os.listdir(source_dir) if f.endswith('.json')]
    
    for filename in tqdm(files, desc="Processing Labels"):
        src_path = os.path.join(source_dir, filename)
        dst_path = os.path.join(target_dir, filename.replace('.json', '.txt'))
        transform_to_yolo_obb(src_path, dst_path)

if __name__ == "__main__":
    main()
