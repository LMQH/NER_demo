"""
环境配置加载模块
根据域名自动加载对应的配置文件
"""
import logging
import os
import platform
import socket
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import dotenv_values

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("Env_Loader")


def get_local_ip() -> Optional[str]:
    """
    获取本地IP地址
    
    Returns:
        本地IP地址或None
    """
    try:
        # 方法1: 通过连接外部地址获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logger.warning(f"获取本地IP地址失败: {e}")
        return None


def get_current_domain() -> Optional[str]:
    """
    获取当前域名或IP地址
    
    优先级：
    1. 环境变量 HTTP_HOST 或 SERVER_NAME（Web应用）
    2. 环境变量 HOSTNAME
    3. socket.gethostname()
    4. 本地IP地址
    5. 从请求头获取（如果可用）
    
    Returns:
        当前域名或IP地址或None
    """
    # 优先从环境变量获取（适用于Web应用）
    domain = os.getenv('HTTP_HOST') or os.getenv('SERVER_NAME') or os.getenv('HOSTNAME')
    if domain:
        logger.info(f"从环境变量获取域名: {domain}")
        return domain
    
    # 尝试从socket获取主机名
    try:
        hostname = socket.gethostname()
        logger.info(f"从socket获取主机名: {hostname}")
        return hostname
    except Exception as e:
        logger.warning(f"获取主机名失败: {e}")
    
    # 如果无法获取域名，尝试获取本地IP地址
    local_ip = get_local_ip()
    if local_ip:
        logger.info(f"获取本地IP地址: {local_ip}")
        return local_ip
    
    return None


def load_env_file(env_file: str) -> Dict[str, Any]:
    """
    加载.env文件并返回配置字典
    
    Args:
        env_file: .env文件路径
        
    Returns:
        配置字典
    """
    if not Path(env_file).exists():
        logger.warning(f"配置文件不存在: {env_file}")
        return {}
    
    try:
        config = dotenv_values(env_file)
        logger.info(f"成功加载配置文件: {env_file}")
        return config
    except Exception as e:
        logger.error(f"加载配置文件失败 {env_file}: {e}")
        return {}


def load_config() -> Dict[str, Any]:
    """
    根据域名加载对应的配置文件
    
    逻辑：
    1. 获取当前域名
    2. 读取 dev.env 和 show.env 获取域名列表
    3. 根据域名匹配决定加载哪个配置文件
    
    Returns:
        配置字典
    """
    try:
        project_root = Path(__file__).parent.parent
        current_domain = get_current_domain()
        
        if not current_domain:
            logger.warning("无法获取当前域名，使用默认配置 dev.env")
            config_file = project_root / "dev.env"
            return load_env_file(str(config_file))
        
        # 读取 dev.env 获取开发环境域名列表
        dev_env_file = project_root / "dev.env"
        dev_config = load_env_file(str(dev_env_file))
        dev_domains = dev_config.get('DEV_DOMAINS', '').split(',')
        dev_domains = [d.strip() for d in dev_domains if d.strip()]
        
        # 读取 show.env 获取生产环境域名列表
        show_env_file = project_root / "show.env"
        show_config = load_env_file(str(show_env_file))
        show_domains = show_config.get('SHOW_DOMAINS', '').split(',')
        show_domains = [d.strip() for d in show_domains if d.strip()]
        
        logger.info(f"当前域名: {current_domain}")
        logger.info(f"开发环境域名列表: {dev_domains}")
        logger.info(f"生产环境域名列表: {show_domains}")
        
        # 检查是否在生产环境域名列表中（优先匹配）
        for domain in show_domains:
            if domain and domain.strip():
                domain = domain.strip()
                # 精确匹配或包含匹配
                is_match = (
                    domain == current_domain or 
                    domain in current_domain or 
                    current_domain in domain
                )
                # 如果是IP地址，进行精确匹配
                if not is_match:
                    try:
                        # 检查是否为IP地址格式
                        import ipaddress
                        domain_ip = ipaddress.ip_address(domain)
                        current_ip = ipaddress.ip_address(current_domain)
                        is_match = domain_ip == current_ip
                    except (ValueError, AttributeError):
                        # 不是有效的IP地址，继续其他匹配方式
                        pass
                
                if is_match:
                    logger.info(f"当前域名/IP {current_domain} 在生产环境域名列表中，加载 show.env")
                    return load_env_file(str(show_env_file))
        
        # 检查是否在开发环境域名列表中
        for domain in dev_domains:
            if domain and domain.strip():
                domain = domain.strip()
                # 精确匹配或包含匹配，或特殊处理 localhost 和 IP地址
                is_match = (
                    domain == current_domain or 
                    domain in current_domain or 
                    current_domain in domain or
                    (domain == 'localhost' and current_domain in ['localhost', '127.0.0.1']) or
                    (domain == '127.0.0.1' and current_domain in ['localhost', '127.0.0.1'])
                )
                # 如果是IP地址，进行精确匹配
                if not is_match:
                    try:
                        # 检查是否为IP地址格式
                        import ipaddress
                        domain_ip = ipaddress.ip_address(domain)
                        current_ip = ipaddress.ip_address(current_domain)
                        is_match = domain_ip == current_ip
                    except (ValueError, AttributeError):
                        # 不是有效的IP地址，继续其他匹配方式
                        pass
                
                if is_match:
                    logger.info(f"当前域名/IP {current_domain} 在开发环境域名列表中，加载 dev.env")
                    return load_env_file(str(dev_env_file))
        
        # 默认使用开发环境配置
        logger.info(f"当前域名 {current_domain} 未匹配到任何环境，默认使用 dev.env")
        return load_env_file(str(dev_env_file))
        
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        # 返回空字典或默认配置
        project_root = Path(__file__).parent.parent
        return load_env_file(str(project_root / "dev.env"))


if __name__ == "__main__":
    config = load_config()
    print(f"配置类型: {type(config)}")
    print("配置内容:")
    for key, value in config.items():
        print(f"  {key} = {value}")

