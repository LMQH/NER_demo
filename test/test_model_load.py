"""
测试模型加载脚本
用于验证模型是否能正确加载和初始化
"""
import sys
import os
from pathlib import Path

# 获取项目根目录（test目录的父目录）
project_root = Path(__file__).parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

def test_model_loading():
    """测试模型加载"""
    print("=" * 60)
    print("开始测试模型加载")
    print("=" * 60)
    
    try:
        # 1. 测试配置加载
        print("\n[步骤1] 测试配置管理器...")
        from src.config_manager import ConfigManager
        config_manager = ConfigManager()
        model_path = config_manager.get_model_path()
        print(f"[OK] 配置加载成功")
        print(f"  模型路径: {model_path}")
        
        # 2. 检查模型路径是否存在
        print("\n[步骤2] 检查模型路径...")
        model_path_obj = Path(model_path)
        if not model_path_obj.exists():
            print(f"[ERROR] 模型路径不存在: {model_path}")
            return False
        print(f"[OK] 模型路径存在: {model_path_obj.absolute()}")
        
        # 3. 检查必要的模型文件
        print("\n[步骤3] 检查模型文件...")
        required_files = [
            'config.json',
            'configuration.json',
            'pytorch_model.bin',
            'vocab.txt'
        ]
        missing_files = []
        for file in required_files:
            file_path = model_path_obj / file
            if file_path.exists():
                print(f"  [OK] {file}")
            else:
                print(f"  [MISSING] {file} (缺失)")
                missing_files.append(file)
        
        if missing_files:
            print(f"\n警告: 缺少以下文件: {', '.join(missing_files)}")
        
        # 4. 测试模型初始化
        print("\n[步骤4] 测试模型初始化...")
        from src.siamese_uie_model import SiameseUIEModel
        print(f"正在初始化模型，这可能需要一些时间...")
        ner_model = SiameseUIEModel(model_path)
        print(f"[OK] 模型初始化成功！")
        
        # 5. 测试简单的实体抽取
        print("\n[步骤5] 测试实体抽取功能...")
        test_text = "1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。"
        test_schema = {
            '人物': None,
            '地理位置': None,
            '组织机构': None
        }
        print(f"测试文本: {test_text}")
        print(f"测试Schema: {test_schema}")
        
        result = ner_model.extract_entities(test_text, test_schema)
        if 'error' in result:
            print(f"[ERROR] 实体抽取失败: {result['error']}")
            return False
        else:
            print(f"[OK] 实体抽取成功")
            print(f"  抽取结果: {result.get('entities', {})}")
        
        print("\n" + "=" * 60)
        print("[OK] 所有测试通过！模型加载和初始化正常")
        print("=" * 60)
        return True
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] 文件未找到错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_loading()
    sys.exit(0 if success else 1)

