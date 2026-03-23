"""
内容生成器 - 生成标题、正文和脚本
"""

import random
from typing import List, Dict, Any


class ContentGenerator:
    """爆款内容生成器"""
    
    TITLE_TEMPLATES = {
        "viral": [
            "{topic}的{num}个惊人秘密",
            "关于{topic}你不知道的事",
            "为什么{topic}让所有人疯狂？",
            "{topic}，原来我们都错了！",
            "揭秘{topic}背后的真相",
            "{topic}，99%的人都不知道",
        ],
        "question": [
            "{topic}真的有用吗？",
            "如何选择{topic}？",
            "{topic}值不值得买？",
            "为什么{topic}这么火？",
            "{topic}到底好不好？",
        ],
        "list": [
            "{topic}的{num}种用法",
            "{num}个{topic}选购技巧",
            "盘点{num}款热门{topic}",
            "{num}个你必须知道的{topic}知识",
            "{topic}排行榜TOP{num}",
        ],
        "story": [
            "我因为{topic}而改变",
            "一个关于{topic}的故事",
            "从{topic}开始的人生转折",
            "遇见{topic}之后",
        ],
        "benefit": [
            "用{topic}省下的{num}个方法",
            "{topic}让你省下一大笔",
            "{topic}带来的{num}大好处",
            "为什么聪明人都选择{topic}？",
        ],
    }
    
    BODY_TEMPLATES = {
        "product": """# {topic}

## 产品亮点

{topic}是一款值得推荐的产品，具有以下特点：

1. **品质保证** - 精选材料，精工细作
2. **性价比** - 同价位中的优质选择
3. **用户口碑** - 众多用户的真实好评

## 使用体验

使用{topic}后，你会发现生活变得更加便利。

## 购买建议

如果你正在寻找{topic}，这款产品值得考虑。
""",
        "activity": """# {topic}活动来袭！

## 活动详情

🎉 好消息！{topic}活动正式开始啦！

## 活动亮点

- 优惠力度空前
- 限时限量抢购
- 多重好礼相送

## 参与方式

立即参与{topic}活动，享受专属福利！
""",
        "story": """# 我与{topic}的故事

## 初识{topic}

第一次接触{topic}是在...

## 使用历程

从开始使用到现在，{topic}给我带来了很多改变。

## 心得体会

如果你也在考虑{topic}，希望我的分享对你有帮助。
""",
    }
    
    def __init__(self):
        """初始化生成器"""
        pass
    
    def generate_title(self, topic: str, style: str = "viral") -> List[str]:
        """
        生成标题列表
        
        Args:
            topic: 主题关键词
            style: 风格类型 (viral|question|list|story|benefit)
            
        Returns:
            标题字符串列表
        """
        templates = self.TITLE_TEMPLATES.get(style, self.TITLE_TEMPLATES["viral"])
        titles = []
        
        for template in templates[:5]:  # 最多返回5个
            num = random.randint(3, 10)
            title = template.format(topic=topic, num=num)
            titles.append(title)
        
        return titles
    
    def generate_body(self, topic: str, format: str = "product", style: str = "casual") -> str:
        """
        生成正文内容
        
        Args:
            topic: 主题
            format: 格式类型 (product|activity|story)
            style: 风格 (casual|professional|funny)
            
        Returns:
            Markdown格式内容
        """
        template = self.BODY_TEMPLATES.get(format, self.BODY_TEMPLATES["product"])
        return template.format(topic=topic)
    
    def generate_script(self, topic: str, duration: int = 60, style: str = "viral") -> Dict[str, Any]:
        """
        生成短视频脚本
        
        Args:
            topic: 视频主题
            duration: 时长(秒)
            style: 风格
            
        Returns:
            包含scenes、narration、duration的JSON
        """
        scene_duration = min(5, duration // 4)
        
        scenes = [
            {
                "scene_number": 1,
                "timestamp": f"0-{scene_duration}",
                "duration": scene_duration,
                "type": "hook",
                "visual": f"特写镜头，展示{topic}",
                "narration": f"你知道吗？关于{topic}，90%的人都不知道这个秘密！",
                "caption": "开场钩子",
                "bgm": "紧张节奏"
            },
            {
                "scene_number": 2,
                "timestamp": f"{scene_duration}-{scene_duration * 2}",
                "duration": scene_duration,
                "type": "content",
                "visual": f"产品展示或使用{topic}的场景",
                "narration": f"今天我要和大家分享{topic}的几个关键点...",
                "caption": "内容主体",
                "bgm": "轻快背景"
            },
            {
                "scene_number": 3,
                "timestamp": f"{scene_duration * 2}-{scene_duration * 3}",
                "duration": scene_duration,
                "type": "value",
                "visual": "对比展示或效果呈现",
                "narration": f"使用{topic}之后，效果真的很明显！",
                "caption": "价值展示",
                "bgm": "轻快背景"
            },
            {
                "scene_number": 4,
                "timestamp": f"{scene_duration * 3}-{duration}",
                "duration": duration - scene_duration * 3,
                "type": "cta",
                "visual": "行动引导画面",
                "narration": f"如果你也想尝试{topic}，点击链接了解更多！",
                "caption": "行动引导",
                "bgm": "高潮收尾"
            }
        ]
        
        return {
            "metadata": {
                "topic": topic,
                "duration": duration,
                "style": style,
                "target_platform": "douyin"
            },
            "scenes": scenes,
            "hooks": [
                f"关于{topic}，90%的人都不知道！",
                f"{topic}的真相，今天大揭秘！",
                f"别再被{topic}骗了！"
            ],
            "call_to_action": f"点击了解更多关于{topic}的信息！",
            "hashtags": [f"#{topic}", "#好物推荐", "#实用分享"]
        }
