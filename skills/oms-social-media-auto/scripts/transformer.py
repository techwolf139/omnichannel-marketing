"""
内容转换器
将统一内容模型转换为各平台特定格式
"""
import json
import sys
from typing import Dict, List, Optional


class ContentTransformer:
    """
    内容转换器
    
    负责将统一内容模型转换为各平台特定格式
    处理长度限制、话题格式、特殊字符等适配
    """
    
    # 平台限制配置
    PLATFORM_LIMITS = {
        "zhihu": {
            "title_max": 100,
            "body_max": None,
            "images_max": None,
            "topic_format": "#{topic}#"
        },
        "weibo": {
            "body_max": 5000,
            "images_max": 18,
            "topic_format": "#{topic}#"
        },
        "xhs": {
            "title_max": 20,
            "body_max": 1000,
            "images_max": 18,
            "topic_format": "#{topic}"
        },
        "twitter": {
            "body_max": 280,
            "body_max_premium": 4000,
            "images_max": 4,
            "topic_format": "#{topic}"
        }
    }
    
    def transform(self, content: dict, platform: str) -> dict:
        """
        将统一内容转换为平台特定格式
        
        Args:
            content: 统一内容模型
            platform: 目标平台标识
        
        Returns:
            平台特定格式内容
        """
        if platform not in self.PLATFORM_LIMITS:
            raise ValueError(f"Unsupported platform: {platform}")
        
        limits = self.PLATFORM_LIMITS[platform]
        result = {
            "content_id": content.get("content_id"),
            "platform": platform
        }
        
        # 处理标题
        title = content.get("title", "")
        if title and limits.get("title_max"):
            title = self.truncate(title, limits["title_max"])
        result["title"] = title
        
        # 处理正文
        body = content.get("body", "")
        if limits.get("body_max"):
            body = self.truncate(body, limits["body_max"])
        result["body"] = body
        
        # 处理媒体
        media = content.get("media", [])
        if limits.get("images_max"):
            media = media[:limits["images_max"]]
        result["media"] = media
        
        # 处理话题
        topics = content.get("topics", [])
        result["topics"] = [
            self.format_topic(topic, limits.get("topic_format", "#{topic}"))
            for topic in topics
        ]
        
        # 处理提及
        result["mentions"] = content.get("mentions", [])
        
        return result
    
    def truncate(self, text: str, max_length: int) -> str:
        """
        按长度限制截断文本
        
        Args:
            text: 原始文本
            max_length: 最大长度
        
        Returns:
            截断后的文本
        """
        if not text or len(text) <= max_length:
            return text
        
        # 保留最后3个字符用于省略号
        truncated = text[:max_length - 3].rstrip()
        return truncated + "..."
    
    def format_topic(self, topic: str, format_str: str) -> str:
        """
        格式化话题标签
        
        Args:
            topic: 话题名称
            format_str: 格式模板，如 "#{topic}#"
        
        Returns:
            格式化后的话题标签
        """
        # 移除已有的话题符号避免重复
        topic = topic.strip("#")
        return format_str.replace("{topic}", topic)
    
    def check_limits(self, content: dict, platform: str) -> Dict[str, any]:
        """
        检查内容是否符合平台限制
        
        Args:
            content: 统一内容模型
            platform: 目标平台标识
        
        Returns:
            检查结果，包含is_valid和violations
        """
        if platform not in self.PLATFORM_LIMITS:
            return {
                "is_valid": False,
                "violations": [f"Unsupported platform: {platform}"]
            }
        
        limits = self.PLATFORM_LIMITS[platform]
        violations = []
        
        # 检查标题
        title = content.get("title", "")
        if title and limits.get("title_max") and len(title) > limits["title_max"]:
            violations.append(
                f"Title exceeds {limits['title_max']} characters"
            )
        
        # 检查正文
        body = content.get("body", "")
        if limits.get("body_max") and len(body) > limits["body_max"]:
            violations.append(
                f"Body exceeds {limits['body_max']} characters"
            )
        
        # 检查媒体数量
        media = content.get("media", [])
        if limits.get("images_max") and len(media) > limits["images_max"]:
            violations.append(
                f"Media count exceeds {limits['images_max']}"
            )
        
        return {
            "is_valid": len(violations) == 0,
            "violations": violations
        }


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing input file"}, ensure_ascii=False))
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(json.dumps({"error": f"Failed to read input: {str(e)}"}, ensure_ascii=False))
        sys.exit(1)
    
    action = data.get("action")
    transformer = ContentTransformer()
    
    if action == "transform":
        result = transformer.transform(
            content=data.get("content", {}),
            platform=data.get("platform", "")
        )
    elif action == "check_limits":
        result = transformer.check_limits(
            content=data.get("content", {}),
            platform=data.get("platform", "")
        )
    else:
        result = {"error": f"Unknown action: {action}"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
