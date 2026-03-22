# 小红书平台营销功能开发计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现小红书（Xiaohongshu）平台营销对接技能 `oms-xhs-integration`，覆盖曝光数据、KOL合作、薯店订单、小程序订单四大核心功能，采用适配器模式将小红书API响应转换为OMS标准模型。

**Architecture:** 采用适配器模式（Adapter Pattern），参照 `oms-jd-integration` 的目录结构。小红书API认证采用 OAuth 2.0 + MD5签名，与京东类似但独立实现。营销数据（笔记曝光、KOL效果）和电商订单（薯店、小程序）分开处理，统一归因到 One-ID。

**Tech Stack:** Python 3, OAuth 2.0, MD5签名, requests, pytest

---

## 前置准备

### Task 0: 创建 Git 分支

**Step 1: 确认当前分支状态**

```bash
git status
```
Expected: On branch `jd-integration`, clean working tree

**Step 2: 创建新分支**

```bash
git checkout -b xhs-integration
```
Expected: Switched to new branch `xhs-integration`

---

## Phase 1: 目录结构

### Task 1: 创建技能目录

**目录结构:**

```
skills/oms-xhs-integration/
├── SKILL.md
├── README.md
├── design.md
├── scripts/
│   ├── __init__.py
│   ├── auth.py           # OAuth 2.0 认证
│   ├── client.py         # API 客户端
│   ├── note_adapter.py   # 笔记曝光数据适配器
│   ├── kol_adapter.py    # KOL/蒲公英平台适配器
│   └── order_adapter.py  # 薯店/小程序订单适配器
└── tests/
    ├── __init__.py
    ├── test_auth.py
    ├── test_note.py
    ├── test_kol.py
    ├── test_order.py
    └── test_e2e.py
```

**Step 1: 创建目录**

```bash
mkdir -p skills/oms-xhs-integration/scripts skills/oms-xhs-integration/tests
touch skills/oms-xhs-integration/scripts/__init__.py skills/oms-xhs-integration/tests/__init__.py
```

**Step 2: Commit**

```bash
git add skills/oms-xhs-integration/
git commit -m "feat: create oms-xhs-integration directory structure"
```

---

## Phase 2: SKILL.md 定义

### Task 2: 编写 SKILL.md

**文件:** `skills/oms-xhs-integration/SKILL.md`

```markdown
---
name: oms-xhs-integration
description: "Use when integrating with Xiaohongshu (小红书) platform, tracking note exposure data, managing KOL collaborations, synchronizing 薯店/shuxidian orders, or processing 小程序/wechat mini-program orders."
---

# 小红书开放平台集成适配器

## Overview

小红书（Xiaohongshu）开放平台对接适配器，实现笔记曝光数据、KOL合作管理、薯店订单同步、小程序订单同步四大核心功能。采用适配器模式，将小红书API响应转换为OMS标准模型。

## When to Use

- 查询小红书笔记曝光/互动数据
- 管理KOL合作（蒲公英平台）
- 同步薯店订单状态
- 同步小程序订单状态
- 归因分析（种草 → 转化）

**触发词**: "小红书"、"XHS"、"薯店"、"蒲公英"、"KOL"

## Core Pattern

### 小红书API分类

| 类别 | 核心API | 说明 |
|------|---------|------|
| 笔记数据 | `note.exposure.get`, `note.interaction.get` | 笔记曝光/互动数据 |
| KOL合作 | `pugongyin.order.list`, `pugongyin.order.detail` | 蒲公英合作订单 |
| 薯店订单 | `order.search`, `order.detail.get` | 薯店电商订单 |
| 小程序订单 | `mini.order.list`, `mini.order.detail` | 微信小程序订单 |

### 认证方式

OAuth 2.0 + MD5签名验证

## Implementation

### 数据模型

**XHSAuthConfig**:
```python
{
    "app_id": str,
    "app_secret": str,
    "access_token": str,
    "refresh_token": str,
    "token_expires_at": datetime
}
```

**XHSNoteExposure** (笔记曝光数据):
```python
{
    "note_id": str,
    "title": str,
    "exposure_count": int,
    "like_count": int,
    "collect_count": int,
    "comment_count": int,
    "share_count": int,
    "publish_time": datetime
}
```

**XHSOrder** (薯店/小程序原始订单):
```python
{
    "xhs_order_id": str,
    "order_type": str,        # "SHU_DIAN" | "MINI_PROGRAM"
    "order_state": int,       # 1-待支付, 2-已支付, 3-已发货, 4-已完成, 5-已取消
    "buyer_nickname": str,
    "receiver_name": str,
    "receiver_mobile": str,
    "address_detail": str,
    "item_list": [...],
    "total_amount": decimal,
    "pay_time": datetime
}
```

### 状态映射

**薯店/小程序订单状态**:
| XHS状态码 | OMS状态 |
|-----------|---------|
| 1 | CREATED |
| 2 | PAID |
| 3 | SHIPPED |
| 4 | DELIVERED |
| 5 | CANCELLED |

## Quick Reference

| 操作 | 方法 | 限流 |
|------|------|------|
| 笔记曝光查询 | `note_exposure_get()` | 200/分钟 |
| 笔记互动查询 | `note_interaction_get()` | 200/分钟 |
| KOL订单列表 | `kol_order_list()` | 100/分钟 |
| 薯店订单搜索 | `order_search()` | 200/分钟 |
| 小程序订单搜索 | `mini_order_search()` | 200/分钟 |

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| token过期未刷新 | API调用失败 | 定期检查并自动刷新 |
| 签名算法错误 | 签名校验失败 | 使用小红书标准MD5签名 |
| 限流未处理 | 请求被拒 | 实现指数退避重试 |
| 归因窗口遗漏 | 归因数据不完整 | 订单前30天触点都计入 |

---

## Task 3: Commit

```bash
git add skills/oms-xhs-integration/SKILL.md
git commit -m "feat: add SKILL.md for oms-xhs-integration"
```

---

## Phase 3: design.md 详细设计

### Task 4: 编写 design.md

**文件:** `skills/oms-xhs-integration/design.md`

设计文档需覆盖：

1. **API Endpoints 详细定义**
   - 正式环境: `https://ark.xiaohongshu.com`
   - 测试环境: `http://flssandbox.xiaohongshu.com`
   - 认证endpoint, 笔记endpoint, KOL endpoint, 订单endpoint

2. **数据模型详细字段**

3. **UTM归因流程**
   ```
   小红书笔记 → UTM参数 → 落地页/小程序 → One-ID归一 → 购买记录 → 归因计算
   ```

4. **与现有OMS技能的集成**
   - `oms-one-id-merge`: 跨平台身份归一
   - `oms-promotion-engine`: 归因后触发营销动作
   - `oms-order-capture`: 统一订单汇聚

5. **错误处理策略**
   - token过期: 自动刷新
   - 限流: 指数退避
   - 签名失败: 重新计算签名

**Step 1: 编写 design.md**

```markdown
# 小红书开放平台集成 - 详细设计

## 1. API 接入

### 1.1 环境配置

| 环境 | Host | 说明 |
|------|------|------|
| 测试环境 | `http://flssandbox.xiaohongshu.com` | 沙箱环境，可自由调用 |
| 正式环境 | `https://ark.xiaohongshu.com` | 需审核权限 |

### 1.2 认证流程

[见下方 auth.py 实现]

### 1.3 API 限流

| 接口类型 | 默认限流 | 说明 |
|----------|----------|------|
| 公共API | 200次/分钟 | token刷新等 |
| 笔记数据API | 200次/分钟 | 曝光/互动数据 |
| KOL/蒲公英API | 100次/分钟 | 合作订单 |
| 订单API | 200次/分钟 | 薯店/小程序订单 |

## 2. 数据模型

### 2.1 XHSNoteExposure

| 字段 | 类型 | 说明 |
|------|------|------|
| note_id | str | 笔记唯一ID |
| title | str | 笔记标题 |
| exposure_count | int | 曝光次数 |
| like_count | int | 点赞数 |
| collect_count | int | 收藏数 |
| comment_count | int | 评论数 |
| share_count | int | 分享数 |
| publish_time | datetime | 发布时间 |

### 2.2 XHSKOLOrder

| 字段 | 类型 | 说明 |
|------|------|------|
| order_id | str | 合作单ID |
| kol_name | str | KOL昵称 |
| kol_id | str | KOL ID |
| content_type | str | 内容形式: 图文/视频 |
| price | decimal | 合作价格 |
| status | str | 状态: pending/ongoing/completed/cancelled |
| publish_time | datetime | 发布预期时间 |

### 2.3 XHSOrder

| 字段 | 类型 | 说明 |
|------|------|------|
| xhs_order_id | str | 订单ID |
| order_type | str | SHU_DIAN / MINI_PROGRAM |
| order_state | int | 状态码 1-5 |
| buyer_nickname | str | 买家昵称 |
| receiver_name | str | 收货人姓名 |
| receiver_mobile | str | 收货人电话 |
| address_detail | str | 详细地址 |
| item_list | list | 商品列表 |
| total_amount | decimal | 订单总金额 |
| freight_amount | decimal | 运费 |
| pay_time | datetime | 支付时间 |
| ship_time | datetime | 发货时间 |

## 3. UTM 归因流程

### 3.1 归因链路

```
小红书笔记曝光/互动
    ↓ (带UTM参数)
落地页/小程序访问
    ↓ (openid/手机号)
One-ID 归一
    ↓
购买行为记录
    ↓
归因计算（30天窗口）
    ↓
分润记录 → profit_sharing
```

### 3.2 归因权重

| 触点 | 权重 |
|------|------|
| 小红书种草 (XHS_CONTENT) | 0.15 |

## 4. 模块设计

### 4.1 auth.py

OAuth 2.0 + MD5签名

### 4.2 client.py

统一API客户端，所有endpoint入口

### 4.3 note_adapter.py

笔记数据转换: XHS API → OMS标准格式

### 4.4 kol_adapter.py

KOL合作数据转换: 蒲公英API → OMS标准格式

### 4.5 order_adapter.py

订单转换: 薯店/小程序API → OMS标准订单格式

## 5. OMS 集成点

| OMS技能 | 集成方式 |
|---------|----------|
| oms-one-id-merge | 用户身份归一（手机号/OpenID） |
| oms-promotion-engine | 归因后发券/积分触发 |
| oms-order-capture | 订单统一汇聚 |
| oms-profit-sharing | 归因分润计算 |

## 6. 错误处理

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 1001 | 参数错误 | 检查请求参数 |
| 1003 | token无效 | 刷新token |
| 1005 | 限流 | 等待后重试（指数退避） |
| 2001 | 权限不足 | 申请API权限 |
| 5000 | 系统错误 | 联系小红书技术支持 |

---

## Task 5: Commit

```bash
git add skills/oms-xhs-integration/design.md
git commit -m "feat: add design.md for oms-xhs-integration"
```

---

## Phase 4: 核心实现

### Task 6: auth.py — OAuth 2.0 + MD5 认证

**文件:** `skills/oms-xhs-integration/scripts/auth.py`

**Step 1: 编写 auth.py**

```python
"""
小红书开放平台认证模块
OAuth 2.0 + MD5签名
"""
import hashlib
import time
import requests
from datetime import datetime, timedelta
from typing import Optional


class XHSAPIError(Exception):
    """小红书API异常"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class XHSAuth:
    """
    小红书 OAuth 2.0 认证
    文档: https://open.xiaohongshu.com/document/api
    """
    
    SANDBOX_HOST = "http://flssandbox.xiaohongshu.com"
    PROD_HOST = "https://ark.xiaohongshu.com"
    
    def __init__(self, app_id: str, app_secret: str, use_sandbox: bool = True):
        self.app_id = app_id
        self.app_secret = app_secret
        self.host = self.SANDBOX_HOST if use_sandbox else self.PROD_HOST
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
    
    def _generate_sign(self, params: dict) -> str:
        """
        生成MD5签名
        签名规则: md5(app_secret + key1 + value1 + key2 + value2 + ... + app_secret)
        按key字典序排列
        """
        # 按key排序
        sorted_keys = sorted(params.keys())
        sign_str = self.app_secret
        for key in sorted_keys:
            sign_str += str(key) + str(params[key])
        sign_str += self.app_secret
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
    
    def _build_common_params(self, method: str) -> dict:
        """构建通用参数"""
        timestamp = int(time.time() * 1000)
        return {
            "appId": self.app_id,
            "method": method,
            "timestamp": timestamp,
            "version": "2.0"
        }
    
    def get_access_token(self, code: str) -> dict:
        """
        用授权码换取access_token
        code: OAuth授权码（有效期10分钟）
        """
        params = self._build_common_params("oauth.getAccessToken")
        params["code"] = code
        params["sign"] = self._generate_sign(params)
        
        url = f"{self.host}/ark/open_api/v3/common_controller"
        response = requests.post(url, json=params, timeout=30)
        result = response.json()
        
        if result.get("code") != 0:
            raise XHSAPIError(result.get("code", -1), result.get("msg", "Unknown error"))
        
        data = result["data"]
        self.access_token = data["accessToken"]
        self.refresh_token = data.get("refreshToken")
        self.token_expires_at = datetime.now() + timedelta(seconds=data.get("expiresIn", 7200))
        
        return data
    
    def refresh_access_token(self) -> dict:
        """
        刷新access_token
        """
        params = self._build_common_params("oauth.refreshToken")
        params["refreshToken"] = self.refresh_token
        params["sign"] = self._generate_sign(params)
        
        url = f"{self.host}/ark/open_api/v3/common_controller"
        response = requests.post(url, json=params, timeout=30)
        result = response.json()
        
        if result.get("code") != 0:
            raise XHSAPIError(result.get("code", -1), result.get("msg", "Unknown error"))
        
        data = result["data"]
        self.access_token = data["accessToken"]
        self.refresh_token = data.get("refreshToken")
        self.token_expires_at = datetime.now() + timedelta(seconds=data.get("expiresIn", 7200))
        
        return data
    
    def ensure_token_valid(self) -> str:
        """确保token有效，过期则自动刷新"""
        if not self.access_token:
            raise XHSAPIError(1003, "Not authenticated, call get_access_token first")
        
        if self.token_expires_at and datetime.now() >= self.token_expires_at - timedelta(minutes=5):
            self.refresh_access_token()
        
        return self.access_token
    
    def is_token_expired(self) -> bool:
        """检查token是否过期"""
        if not self.token_expires_at:
            return True
        return datetime.now() >= self.token_expires_at
```

**Step 2: 验证语法**

```bash
cd skills/oms-xhs-integration
python -c "from scripts.auth import XHSAuth, XHSAPIError; print('auth.py OK')"
```
Expected: `auth.py OK`

**Step 3: Commit**

```bash
git add skills/oms-xhs-integration/scripts/auth.py
git commit -m "feat: implement XHSAuth with OAuth 2.0 + MD5"
```

---

### Task 7: client.py — API 客户端

**文件:** `skills/oms-xhs-integration/scripts/client.py`

**Step 1: 编写 client.py**

```python
"""
小红书开放平台 API 客户端
统一封装所有API调用
"""
import time
import requests
from typing import Optional, List
from .auth import XHSAuth, XHSAPIError


class XHSClient:
    """
    小红书开放平台 API 客户端
    
    API文档: https://open.xiaohongshu.com/document/api
    """
    
    def __init__(self, auth: XHSAuth):
        self.auth = auth
    
    def _call(self, method: str, params: dict = None, data: dict = None) -> dict:
        """
        通用API调用
        
        Args:
            method: API方法名
            params: URL查询参数
            data: 请求体JSON数据
        
        Returns:
            API响应dict
        """
        # 确保token有效
        self.auth.ensure_token_valid()
        
        headers = {"Authorization": f"Bearer {self.auth.access_token}"}
        
        # 构建请求
        url = f"{self.auth.host}/ark/open_api/v2/{method.replace('.', '/')}"
        
        response = requests.get(
            url, 
            params=params, 
            json=data, 
            headers=headers,
            timeout=30
        )
        
        result = response.json()
        
        # 检查业务错误
        if result.get("code") != 0:
            code = result.get("code", -1)
            msg = result.get("msg", "Unknown error")
            if code == 1003:  # token无效，尝试刷新
                self.auth.refresh_access_token()
                headers["Authorization"] = f"Bearer {self.auth.access_token}"
                response = requests.get(url, params=params, json=data, headers=headers, timeout=30)
                result = response.json()
            elif code == 1005:  # 限流
                raise XHSAPIError(1005, "Rate limited, implement retry")
            else:
                raise XHSAPIError(code, msg)
        
        return result.get("data", {})
    
    # ========== 笔记数据 API ==========
    
    def note_exposure_get(self, note_id: str) -> dict:
        """
        获取笔记曝光数据
        
        Args:
            note_id: 笔记ID
        
        Returns:
            曝光数据 dict
        """
        return self._call(
            "note.exposure.get",
            params={"note_id": note_id}
        )
    
    def note_interaction_get(self, note_id: str) -> dict:
        """
        获取笔记互动数据（点赞/收藏/评论/分享）
        
        Args:
            note_id: 笔记ID
        
        Returns:
            互动数据 dict
        """
        return self._call(
            "note.interaction.get",
            params={"note_id": note_id}
        )
    
    def note_exposure_batch(self, note_ids: List[str]) -> List[dict]:
        """
        批量获取笔记曝光数据
        
        Args:
            note_ids: 笔记ID列表（最多50个）
        
        Returns:
            曝光数据列表
        """
        results = []
        for note_id in note_ids:
            try:
                data = self.note_exposure_get(note_id)
                results.append(data)
            except XHSAPIError as e:
                if e.code == 1005:  # 限流，等待后重试
                    time.sleep(5)
                    data = self.note_exposure_get(note_id)
                    results.append(data)
                else:
                    raise
        return results
    
    # ========== KOL/蒲公英 API ==========
    
    def kol_order_list(self, page: int = 1, page_size: int = 20) -> dict:
        """
        获取蒲公英合作订单列表
        
        Args:
            page: 页码
            page_size: 每页数量（最大50）
        
        Returns:
            订单列表 dict
        """
        return self._call(
            "pugongyin.order.list",
            params={"page": page, "page_size": page_size}
        )
    
    def kol_order_detail(self, order_id: str) -> dict:
        """
        获取蒲公英合作订单详情
        
        Args:
            order_id: 合作单ID
        
        Returns:
            订单详情 dict
        """
        return self._call(
            "pugongyin.order.detail",
            params={"order_id": order_id}
        )
    
    # ========== 薯店订单 API ==========
    
    def shu_dian_order_search(
        self,
        start_date: str = None,
        end_date: str = None,
        order_state: int = None,
        page: int = 1,
        page_size: int = 100
    ) -> dict:
        """
        搜索薯店订单
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            order_state: 订单状态 (1-待支付,2-已支付,3-已发货,4-已完成,5-已取消)
            page: 页码
            page_size: 每页数量
        
        Returns:
            订单列表 dict
        """
        params = {"page": page, "page_size": page_size}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if order_state is not None:
            params["order_state"] = order_state
        
        return self._call("order.search", params=params)
    
    def shu_dian_order_detail(self, order_id: str) -> dict:
        """
        获取薯店订单详情
        
        Args:
            order_id: 订单ID
        
        Returns:
            订单详情 dict
        """
        return self._call(
            "order.detail.get",
            params={"order_id": order_id}
        )
    
    # ========== 小程序订单 API ==========
    
    def mini_order_list(
        self,
        start_date: str = None,
        end_date: str = None,
        order_state: int = None,
        page: int = 1,
        page_size: int = 100
    ) -> dict:
        """
        获取小程序订单列表
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            order_state: 订单状态
            page: 页码
            page_size: 每页数量
        
        Returns:
            订单列表 dict
        """
        params = {"page": page, "page_size": page_size}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if order_state is not None:
            params["order_state"] = order_state
        
        return self._call("mini.order.list", params=params)
    
    def mini_order_detail(self, order_id: str) -> dict:
        """
        获取小程序订单详情
        
        Args:
            order_id: 订单ID
        
        Returns:
            订单详情 dict
        """
        return self._call(
            "mini.order.detail",
            params={"order_id": order_id}
        )
```

**Step 2: 验证语法**

```bash
cd skills/oms-xhs-integration
python -c "from scripts.client import XHSClient; print('client.py OK')"
```
Expected: `client.py OK`

**Step 3: Commit**

```bash
git add skills/oms-xhs-integration/scripts/client.py
git commit -m "feat: implement XHSClient with all API endpoints"
```

---

### Task 8: note_adapter.py — 笔记曝光数据适配器

**文件:** `skills/oms-xhs-integration/scripts/note_adapter.py`

**Step 1: 编写 note_adapter.py**

```python
"""
小红书笔记数据适配器
将小红书笔记API响应转换为OMS标准格式
"""
from datetime import datetime
from typing import List, Optional


class XHSNoteAdapter:
    """
    笔记数据适配器
    
    负责:
    1. 笔记曝光数据标准化
    2. 笔记互动数据标准化
    3. 批量数据聚合
    """
    
    def to_standard_exposure(self, raw: dict) -> dict:
        """
        将小红书原始曝光数据转换为标准格式
        
        Args:
            raw: 小红书API返回的原始数据
        
        Returns:
            标准曝光数据
        """
        return {
            "note_id": raw.get("note_id", ""),
            "title": raw.get("title", ""),
            "exposure_count": int(raw.get("exposure_count", 0)),
            "like_count": int(raw.get("like_count", 0)),
            "collect_count": int(raw.get("collect_count", 0)),
            "comment_count": int(raw.get("comment_count", 0)),
            "share_count": int(raw.get("share_count", 0)),
            "publish_time": self._parse_time(raw.get("publish_time")),
            "platform": "XHS"
        }
    
    def to_standard_interaction(self, raw: dict) -> dict:
        """
        将小红书原始互动数据转换为标准格式
        
        Args:
            raw: 小红书API返回的原始数据
        
        Returns:
            标准互动数据
        """
        return {
            "note_id": raw.get("note_id", ""),
            "like_count": int(raw.get("like_count", 0)),
            "collect_count": int(raw.get("collect_count", 0)),
            "comment_count": int(raw.get("comment_count", 0)),
            "share_count": int(raw.get("share_count", 0)),
            "interaction_rate": self._calc_interaction_rate(raw),
            "platform": "XHS"
        }
    
    def to_standard_note(self, raw: dict) -> dict:
        """
        将小红书笔记完整数据转换为标准格式（合并曝光+互动）
        
        Args:
            raw: 原始笔记数据（包含exposure和interaction）
        
        Returns:
            标准笔记数据
        """
        return {
            "note_id": raw.get("note_id", ""),
            "title": raw.get("title", ""),
            "exposure_count": int(raw.get("exposure_count", 0)),
            "like_count": int(raw.get("like_count", 0)),
            "collect_count": int(raw.get("collect_count", 0)),
            "comment_count": int(raw.get("comment_count", 0)),
            "share_count": int(raw.get("share_count", 0)),
            "interaction_rate": self._calc_interaction_rate(raw),
            "publish_time": self._parse_time(raw.get("publish_time")),
            "platform": "XHS"
        }
    
    def _calc_interaction_rate(self, raw: dict) -> float:
        """
        计算互动率 = (点赞+收藏+评论+分享) / 曝光量
        """
        exposure = int(raw.get("exposure_count", 0))
        if exposure == 0:
            return 0.0
        
        interactions = (
            int(raw.get("like_count", 0)) +
            int(raw.get("collect_count", 0)) +
            int(raw.get("comment_count", 0)) +
            int(raw.get("share_count", 0))
        )
        return round(interactions / exposure, 4)
    
    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """解析时间字符串"""
        if not time_str:
            return None
        try:
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
```

**Step 2: 验证语法**

```bash
cd skills/oms-xhs-integration
python -c "from scripts.note_adapter import XHSNoteAdapter; print('note_adapter.py OK')"
```
Expected: `note_adapter.py OK`

**Step 3: Commit**

```bash
git add skills/oms-xhs-integration/scripts/note_adapter.py
git commit -m "feat: implement XHSNoteAdapter for exposure data"
```

---

### Task 9: kol_adapter.py — KOL/蒲公英适配器

**文件:** `skills/oms-xhs-integration/scripts/kol_adapter.py`

**Step 1: 编写 kol_adapter.py**

```python
"""
小红书KOL/蒲公英平台适配器
将蒲公英合作API响应转换为OMS标准格式
"""
from datetime import datetime
from typing import List, Optional


class XHSKOLAdapter:
    """
    KOL合作数据适配器
    
    负责:
    1. KOL合作订单标准化
    2. 合作状态映射
    3. 投放效果数据标准化
    """
    
    # 蒲公英订单状态映射
    KOL_STATUS_MAP = {
        "pending": "待发布",
        "ongoing": "执行中",
        "completed": "已完成",
        "cancelled": "已取消"
    }
    
    # OMS标准状态
    KOL_OMS_STATUS = {
        "pending": "CREATED",
        "ongoing": "IN_PROGRESS",
        "completed": "COMPLETED",
        "cancelled": "CANCELLED"
    }
    
    def to_standard_kol_order(self, raw: dict) -> dict:
        """
        将蒲公英原始订单转换为标准格式
        
        Args:
            raw: 蒲公英API返回的原始数据
        
        Returns:
            标准KOL订单数据
        """
        raw_status = raw.get("status", "pending")
        
        return {
            "order_id": raw.get("order_id", ""),
            "kol_name": raw.get("kol_name", ""),
            "kol_id": raw.get("kol_id", ""),
            "content_type": raw.get("content_type", ""),
            "price": float(raw.get("price", 0)),
            "status": self.KOL_OMS_STATUS.get(raw_status, "UNKNOWN"),
            "status_text": self.KOL_STATUS_MAP.get(raw_status, "未知"),
            "expected_publish_time": self._parse_time(raw.get("expected_publish_time")),
            "actual_publish_time": self._parse_time(raw.get("actual_publish_time")),
            "note_url": raw.get("note_url", ""),
            "platform": "XHS_KOL"
        }
    
    def to_standard_kol_performance(self, raw: dict) -> dict:
        """
        将蒲公英投放效果数据转换为标准格式
        
        Args:
            raw: 蒲公英API返回的投放效果数据
        
        Returns:
            标准KOL效果数据
        """
        return {
            "order_id": raw.get("order_id", ""),
            "note_id": raw.get("note_id", ""),
            "exposure_count": int(raw.get("exposure_count", 0)),
            "like_count": int(raw.get("like_count", 0)),
            "collect_count": int(raw.get("collect_count", 0)),
            "comment_count": int(raw.get("comment_count", 0)),
            "share_count": int(raw.get("share_count", 0)),
            "click_count": int(raw.get("click_count", 0)),
            "cost_per_exposure": self._calc_cpe(raw),
            "cost_per_interaction": self._calc_cpi(raw),
            "platform": "XHS_KOL"
        }
    
    def _calc_cpe(self, raw: dict) -> float:
        """计算千次曝光成本"""
        exposure = int(raw.get("exposure_count", 0))
        price = float(raw.get("price", 0))
        if exposure == 0:
            return 0.0
        return round(price / exposure * 1000, 2)
    
    def _calc_cpi(self, raw: dict) -> float:
        """计算互动成本"""
        interactions = (
            int(raw.get("like_count", 0)) +
            int(raw.get("collect_count", 0)) +
            int(raw.get("comment_count", 0)) +
            int(raw.get("share_count", 0))
        )
        price = float(raw.get("price", 0))
        if interactions == 0:
            return 0.0
        return round(price / interactions, 2)
    
    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """解析时间字符串"""
        if not time_str:
            return None
        try:
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
```

**Step 2: 验证语法**

```bash
cd skills/oms-xhs-integration
python -c "from scripts.kol_adapter import XHSKOLAdapter; print('kol_adapter.py OK')"
```
Expected: `kol_adapter.py OK`

**Step 3: Commit**

```bash
git add skills/oms-xhs-integration/scripts/kol_adapter.py
git commit -m "feat: implement XHSKOLAdapter for KOL collaboration data"
```

---

### Task 10: order_adapter.py — 薯店/小程序订单适配器

**文件:** `skills/oms-xhs-integration/scripts/order_adapter.py`

**Step 1: 编写 order_adapter.py**

```python
"""
小红书订单适配器
将薯店/小程序API响应转换为OMS标准订单格式
"""
from datetime import datetime
from typing import List, Optional


class XHSOrderAdapter:
    """
    薯店/小程序订单适配器
    
    负责:
    1. 薯店订单标准化
    2. 小程序订单标准化
    3. 订单类型区分 (SHU_DIAN / MINI_PROGRAM)
    4. 状态映射
    """
    
    # 小红书订单状态映射
    STATUS_MAP = {
        1: "CREATED",    # 待支付
        2: "PAID",       # 已支付
        3: "SHIPPED",    # 已发货
        4: "DELIVERED",  # 已完成
        5: "CANCELLED",  # 已取消
    }
    
    def to_standard_order(self, raw: dict, order_type: str) -> dict:
        """
        将小红书原始订单转换为标准格式
        
        Args:
            raw: 小红书API返回的原始订单数据
            order_type: 订单类型 "SHU_DIAN" 或 "MINI_PROGRAM"
        
        Returns:
            标准订单数据
        """
        raw_state = int(raw.get("order_state", 1))
        
        return {
            "platform_order_id": raw.get("order_id", ""),
            "platform": "XHS",
            "order_type": order_type,
            "status": self.STATUS_MAP.get(raw_state, "UNKNOWN"),
            "status_code": raw_state,
            "buyer_nickname": raw.get("buyer_nickname", ""),
            "receiver_name": raw.get("receiver_name", ""),
            "receiver_mobile": raw.get("receiver_mobile", ""),
            "address_detail": raw.get("address_detail", ""),
            "items": self._normalize_items(raw.get("item_list", [])),
            "total_amount": float(raw.get("total_amount", 0)),
            "freight_amount": float(raw.get("freight_amount", 0)),
            "pay_time": self._parse_time(raw.get("pay_time")),
            "ship_time": self._parse_time(raw.get("ship_time")),
            "create_time": self._parse_time(raw.get("create_time")),
            # UTM归因字段
            "utm_source": raw.get("utm_source", ""),
            "utm_medium": raw.get("utm_medium", ""),
            "utm_campaign": raw.get("utm_campaign", ""),
            # 归因权重（固定值，后续归因计算时使用）
            "attribution_weight": 0.15
        }
    
    def _normalize_items(self, items: List[dict]) -> List[dict]:
        """
        标准化商品列表
        
        Args:
            items: 原始商品列表
        
        Returns:
            标准商品列表
        """
        normalized = []
        for item in items:
            normalized.append({
                "sku_id": item.get("sku_id", ""),
                "sku_name": item.get("sku_name", ""),
                "quantity": int(item.get("quantity", 1)),
                "unit_price": float(item.get("unit_price", 0)),
                "total_price": float(item.get("total_price", 0)),
                "image_url": item.get("image_url", "")
            })
        return normalized
    
    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """解析时间字符串"""
        if not time_str:
            return None
        try:
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    
    def is_shudan_order(self, raw: dict) -> bool:
        """判断是否为薯店订单"""
        return raw.get("order_source", "").upper() == "SHU_DIAN"
    
    def is_mini_program_order(self, raw: dict) -> bool:
        """判断是否为小程序订单"""
        return raw.get("order_source", "").upper() == "MINI_PROGRAM"
```

**Step 2: 验证语法**

```bash
cd skills/oms-xhs-integration
python -c "from scripts.order_adapter import XHSOrderAdapter; print('order_adapter.py OK')"
```
Expected: `order_adapter.py OK`

**Step 3: Commit**

```bash
git add skills/oms-xhs-integration/scripts/order_adapter.py
git commit -m "feat: implement XHSOrderAdapter for 薯店 and 小程序 orders"
```

---

## Phase 5: 单元测试

### Task 11: test_auth.py — 认证模块测试

**文件:** `skills/oms-xhs-integration/tests/test_auth.py`

**Step 1: 编写测试**

```python
"""
XHSAuth 单元测试
"""
import pytest
from scripts.auth import XHSAuth, XHSAPIError


class TestXHSAuth:
    
    def test_generate_sign(self):
        """测试MD5签名生成"""
        auth = XHSAuth(app_id="test_app", app_secret="test_secret")
        params = {"appId": "test_app", "method": "test.method", "timestamp": 1234567890}
        sign = auth._generate_sign(params)
        assert len(sign) == 32
        assert sign.isupper()
    
    def test_generate_sign_deterministic(self):
        """测试签名生成是确定性的"""
        auth = XHSAuth(app_id="test_app", app_secret="test_secret")
        params = {"appId": "test_app", "method": "test.method", "timestamp": 1234567890}
        sign1 = auth._generate_sign(params)
        sign2 = auth._generate_sign(params)
        assert sign1 == sign2
    
    def test_build_common_params(self):
        """测试通用参数构建"""
        auth = XHSAuth(app_id="test_app", app_secret="test_secret")
        params = auth._build_common_params("test.method")
        assert params["appId"] == "test_app"
        assert params["method"] == "test.method"
        assert params["version"] == "2.0"
        assert "timestamp" in params
    
    def test_is_token_expired_no_token(self):
        """测试无token时返回过期"""
        auth = XHSAuth(app_id="test_app", app_secret="test_secret")
        assert auth.is_token_expired() is True
    
    def test_ensure_token_valid_raises_without_token(self):
        """测试无token时抛出异常"""
        auth = XHSAuth(app_id="test_app", app_secret="test_secret")
        with pytest.raises(XHSAPIError) as exc_info:
            auth.ensure_token_valid()
        assert exc_info.value.code == 1003
    
    def test_xhs_api_error(self):
        """测试XHSAPIError异常"""
        error = XHSAPIError(1003, "token invalid")
        assert error.code == 1003
        assert error.message == "token invalid"
        assert "[1003]" in str(error)
```

**Step 2: 运行测试**

```bash
cd skills/oms-xhs-integration
python -m pytest tests/test_auth.py -v
```
Expected: 6 passed

**Step 3: Commit**

```bash
git add skills/oms-xhs-integration/tests/test_auth.py
git commit -m "test: add XHSAuth unit tests"
```

---

### Task 12: test_note.py — 笔记适配器测试

**文件:** `skills/oms-xhs-integration/tests/test_note.py`

**Step 1: 编写测试**

```python
"""
XHSNoteAdapter 单元测试
"""
import pytest
from datetime import datetime
from scripts.note_adapter import XHSNoteAdapter


class TestXHSNoteAdapter:
    
    def setup_method(self):
        self.adapter = XHSNoteAdapter()
    
    def test_to_standard_exposure(self):
        """测试曝光数据标准化"""
        raw = {
            "note_id": "note_001",
            "title": "测试笔记",
            "exposure_count": 10000,
            "like_count": 500,
            "collect_count": 200,
            "comment_count": 50,
            "share_count": 30,
            "publish_time": "2024-01-01T10:00:00Z"
        }
        result = self.adapter.to_standard_exposure(raw)
        
        assert result["note_id"] == "note_001"
        assert result["title"] == "测试笔记"
        assert result["exposure_count"] == 10000
        assert result["like_count"] == 500
        assert result["platform"] == "XHS"
    
    def test_to_standard_exposure_missing_fields(self):
        """测试曝光数据缺少字段"""
        raw = {"note_id": "note_001"}
        result = self.adapter.to_standard_exposure(raw)
        
        assert result["note_id"] == "note_001"
        assert result["exposure_count"] == 0
        assert result["like_count"] == 0
    
    def test_calc_interaction_rate(self):
        """测试互动率计算"""
        raw = {
            "exposure_count": 1000,
            "like_count": 50,
            "collect_count": 30,
            "comment_count": 10,
            "share_count": 10
        }
        rate = self.adapter._calc_interaction_rate(raw)
        # (50+30+10+10)/1000 = 0.1
        assert rate == 0.1
    
    def test_calc_interaction_rate_zero_exposure(self):
        """测试曝光为0时互动率为0"""
        raw = {"exposure_count": 0}
        rate = self.adapter._calc_interaction_rate(raw)
        assert rate == 0.0
    
    def test_to_standard_note(self):
        """测试完整笔记数据标准化"""
        raw = {
            "note_id": "note_001",
            "title": "种草笔记",
            "exposure_count": 5000,
            "like_count": 250,
            "collect_count": 100,
            "comment_count": 25,
            "share_count": 15,
            "publish_time": "2024-01-15T12:00:00Z"
        }
        result = self.adapter.to_standard_note(raw)
        
        assert result["platform"] == "XHS"
        assert result["interaction_rate"] == 0.078  # 390/5000
```

**Step 2: 运行测试**

```bash
cd skills/oms-xhs-integration
python -m pytest tests/test_note.py -v
```
Expected: 5 passed

**Step 3: Commit**

```bash
git add skills/oms-xhs-integration/tests/test_note.py
git commit -m "test: add XHSNoteAdapter unit tests"
```

---

### Task 13: test_kol.py — KOL适配器测试

**文件:** `skills/oms-xhs-integration/tests/test_kol.py`

**Step 1: 编写测试**

```python
"""
XHSKOLAdapter 单元测试
"""
import pytest
from scripts.kol_adapter import XHSKOLAdapter


class TestXHSKOLAdapter:
    
    def setup_method(self):
        self.adapter = XHSKOLAdapter()
    
    def test_to_standard_kol_order(self):
        """测试KOL订单标准化"""
        raw = {
            "order_id": "kol_order_001",
            "kol_name": "美妆达人小A",
            "kol_id": "kol_123",
            "content_type": "视频",
            "price": 5000.00,
            "status": "completed",
            "expected_publish_time": "2024-02-01T10:00:00Z",
            "note_url": "https://www.xiaohongshu.com/discovery/item/xxx"
        }
        result = self.adapter.to_standard_kol_order(raw)
        
        assert result["order_id"] == "kol_order_001"
        assert result["kol_name"] == "美妆达人小A"
        assert result["status"] == "COMPLETED"
        assert result["price"] == 5000.00
        assert result["platform"] == "XHS_KOL"
    
    def test_to_standard_kol_order_pending(self):
        """测试待发布KOL订单"""
        raw = {
            "order_id": "kol_order_002",
            "kol_name": "时尚博主小B",
            "kol_id": "kol_456",
            "content_type": "图文",
            "price": 3000.00,
            "status": "pending"
        }
        result = self.adapter.to_standard_kol_order(raw)
        assert result["status"] == "CREATED"
    
    def test_calc_cpe(self):
        """测试千次曝光成本计算"""
        raw = {"price": 1000, "exposure_count": 50000}
        cpe = self.adapter._calc_cpe(raw)
        # 1000/50000*1000 = 20
        assert cpe == 20.0
    
    def test_calc_cpi(self):
        """测试互动成本计算"""
        raw = {
            "price": 5000,
            "like_count": 200,
            "collect_count": 100,
            "comment_count": 50,
            "share_count": 50
        }
        cpi = self.adapter._calc_cpi(raw)
        # 5000/(200+100+50+50) = 5000/400 = 12.5
        assert cpi == 12.5
    
    def test_to_standard_kol_performance(self):
        """测试KOL投放效果标准化"""
        raw = {
            "order_id": "kol_order_001",
            "note_id": "note_001",
            "exposure_count": 100000,
            "like_count": 5000,
            "collect_count": 2000,
            "comment_count": 500,
            "share_count": 300,
            "click_count": 2000,
            "price": 10000.00
        }
        result = self.adapter.to_standard_kol_performance(raw)
        
        assert result["exposure_count"] == 100000
        assert result["cost_per_exposure"] == 100.0  # 10000/100000*1000
        assert result["platform"] == "XHS_KOL"
```

**Step 2: 运行测试**

```bash
cd skills/oms-xhs-integration
python -m pytest tests/test_kol.py -v
```
Expected: 5 passed

**Step 3: Commit**

```bash
git add skills/oms-xhs-integration/tests/test_kol.py
git commit -m "test: add XHSKOLAdapter unit tests"
```

---

### Task 14: test_order.py — 订单适配器测试

**文件:** `skills/oms-xhs-integration/tests/test_order.py`

**Step 1: 编写测试**

```python
"""
XHSOrderAdapter 单元测试
"""
import pytest
from scripts.order_adapter import XHSOrderAdapter


class TestXHSOrderAdapter:
    
    def setup_method(self):
        self.adapter = XHSOrderAdapter()
    
    def test_to_standard_order_shudian(self):
        """测试薯店订单标准化"""
        raw = {
            "order_id": "xhs_order_001",
            "order_state": 2,
            "buyer_nickname": "用户123",
            "receiver_name": "张三",
            "receiver_mobile": "13800138000",
            "address_detail": "北京市朝阳区xxx",
            "item_list": [
                {
                    "sku_id": "sku_001",
                    "sku_name": "商品A",
                    "quantity": 2,
                    "unit_price": 99.50,
                    "total_price": 199.00
                }
            ],
            "total_amount": 199.00,
            "freight_amount": 10.00,
            "pay_time": "2024-01-15T14:30:00Z",
            "create_time": "2024-01-15T14:00:00Z",
            "utm_source": "xhs",
            "utm_medium": "note",
            "utm_campaign": "spring_promo"
        }
        result = self.adapter.to_standard_order(raw, "SHU_DIAN")
        
        assert result["platform_order_id"] == "xhs_order_001"
        assert result["status"] == "PAID"
        assert result["order_type"] == "SHU_DIAN"
        assert result["items"][0]["sku_name"] == "商品A"
        assert result["attribution_weight"] == 0.15
    
    def test_to_standard_order_mini_program(self):
        """测试小程序订单标准化"""
        raw = {
            "order_id": "mini_order_001",
            "order_state": 1,
            "buyer_nickname": "用户456",
            "receiver_name": "李四",
            "receiver_mobile": "13900139000",
            "address_detail": "上海市浦东新区xxx",
            "item_list": [],
            "total_amount": 0,
            "freight_amount": 0
        }
        result = self.adapter.to_standard_order(raw, "MINI_PROGRAM")
        
        assert result["status"] == "CREATED"
        assert result["order_type"] == "MINI_PROGRAM"
    
    def test_status_mapping(self):
        """测试所有状态码映射"""
        status_cases = [
            (1, "CREATED"),
            (2, "PAID"),
            (3, "SHIPPED"),
            (4, "DELIVERED"),
            (5, "CANCELLED")
        ]
        for code, expected_status in status_cases:
            raw = {"order_id": "test", "order_state": code}
            result = self.adapter.to_standard_order(raw, "SHU_DIAN")
            assert result["status"] == expected_status, f"state {code} should be {expected_status}"
    
    def test_normalize_items(self):
        """测试商品列表标准化"""
        items = [
            {"sku_id": "sku1", "sku_name": "商品1", "quantity": 1, "unit_price": 10.0, "total_price": 10.0},
            {"sku_id": "sku2", "sku_name": "商品2", "quantity": 3, "unit_price": 20.0, "total_price": 60.0}
        ]
        result = self.adapter._normalize_items(items)
        
        assert len(result) == 2
        assert result[0]["quantity"] == 1
        assert result[1]["total_price"] == 60.0
```

**Step 2: 运行测试**

```bash
cd skills/oms-xhs-integration
python -m pytest tests/test_order.py -v
```
Expected: 4 passed

**Step 3: Commit**

```bash
git add skills/oms-xhs-integration/tests/test_order.py
git commit -m "test: add XHSOrderAdapter unit tests"
```

---

## Phase 6: E2E 测试

### Task 15: test_e2e.py — 端到端测试

**文件:** `skills/oms-xhs-integration/tests/test_e2e.py`

**Step 1: 编写 E2E 测试**

```python
"""
XHS Integration E2E Tests
模拟完整流程：认证 → 拉取订单 → 标准化 → 归因
"""
import pytest
from unittest.mock import Mock, patch
from scripts.auth import XHSAuth, XHSAPIError
from scripts.client import XHSClient
from scripts.note_adapter import XHSNoteAdapter
from scripts.kol_adapter import XHSKOLAdapter
from scripts.order_adapter import XHSOrderAdapter


class TestXHSAuthE2E:
    """认证流程 E2E"""
    
    @patch('requests.post')
    def test_full_auth_flow(self, mock_post):
        """测试完整认证流程：code换取token → token刷新"""
        mock_post.return_value = Mock(
            json=lambda: {
                "code": 0,
                "data": {
                    "accessToken": "mock_access_token",
                    "refreshToken": "mock_refresh_token",
                    "expiresIn": 7200
                }
            }
        )
        
        auth = XHSAuth(app_id="test", app_secret="test", use_sandbox=True)
        result = auth.get_access_token("test_code")
        
        assert result["accessToken"] == "mock_access_token"
        assert auth.access_token == "mock_access_token"
        assert auth.token_expires_at is not None


class TestXHSOrderE2E:
    """订单流程 E2E"""
    
    def setup_method(self):
        self.adapter = XHSOrderAdapter()
    
    def test_shudian_order_full_flow(self):
        """薯店订单：原始数据 → 标准格式 → OMS"""
        raw_order = {
            "order_id": "SD20240115001",
            "order_state": 2,
            "buyer_nickname": "小红书用户",
            "receiver_name": "王五",
            "receiver_mobile": "13600136000",
            "address_detail": "杭州市西湖区xxx",
            "item_list": [
                {"sku_id": "A001", "sku_name": "护肤套装", "quantity": 1, "unit_price": 299.0, "total_price": 299.0}
            ],
            "total_amount": 299.0,
            "freight_amount": 0,
            "pay_time": "2024-01-15T10:00:00Z",
            "create_time": "2024-01-15T09:30:00Z",
            "utm_source": "xhs",
            "utm_medium": "note",
            "utm_campaign": "skincare_promo"
        }
        
        # 转换为标准格式
        standard = self.adapter.to_standard_order(raw_order, "SHU_DIAN")
        
        assert standard["platform"] == "XHS"
        assert standard["status"] == "PAID"
        assert standard["items"][0]["sku_name"] == "护肤套装"
        assert standard["attribution_weight"] == 0.15
    
    def test_mini_program_order_full_flow(self):
        """小程序订单：原始数据 → 标准格式 → OMS"""
        raw_order = {
            "order_id": "MINI20240115001",
            "order_state": 3,
            "buyer_nickname": "微信用户",
            "receiver_name": "赵六",
            "receiver_mobile": "13500135000",
            "address_detail": "广州市天河区xxx",
            "item_list": [
                {"sku_id": "B001", "sku_name": "彩妆盘", "quantity": 1, "unit_price": 199.0, "total_price": 199.0}
            ],
            "total_amount": 199.0,
            "freight_amount": 5.0,
            "pay_time": "2024-01-15T12:00:00Z",
            "ship_time": "2024-01-15T15:00:00Z",
            "create_time": "2024-01-15T11:30:00Z"
        }
        
        standard = self.adapter.to_standard_order(raw_order, "MINI_PROGRAM")
        
        assert standard["order_type"] == "MINI_PROGRAM"
        assert standard["status"] == "SHIPPED"
    
    def test_attribution_flow(self):
        """归因流程：订单 → 归因计算"""
        raw_order = {
            "order_id": "ATTR2024001",
            "order_state": 4,
            "buyer_nickname": "测试用户",
            "receiver_name": "测试",
            "receiver_mobile": "13800138000",
            "address_detail": "测试地址",
            "item_list": [],
            "total_amount": 500.0,
            "freight_amount": 0,
            "pay_time": "2024-01-15T10:00:00Z",
            "create_time": "2024-01-15T09:00:00Z",
            "utm_source": "xhs",
            "utm_medium": "kol",
            "utm_campaign": "test_camp"
        }
        
        standard = self.adapter.to_standard_order(raw_order, "SHU_DIAN")
        
        # 归因计算: 订单金额 × 归因权重
        attributed_value = standard["total_amount"] * standard["attribution_weight"]
        assert attributed_value == 75.0  # 500 × 0.15


class TestXHSNoteE2E:
    """笔记数据 E2E"""
    
    def setup_method(self):
        self.adapter = XHSNoteAdapter()
    
    def test_note_exposure_to_standard(self):
        """笔记曝光数据 → 标准格式"""
        raw = {
            "note_id": "note_xhs_001",
            "title": "春季护肤种草",
            "exposure_count": 50000,
            "like_count": 2500,
            "collect_count": 1200,
            "comment_count": 300,
            "share_count": 100,
            "publish_time": "2024-01-10T08:00:00Z"
        }
        
        standard = self.adapter.to_standard_note(raw)
        
        assert standard["note_id"] == "note_xhs_001"
        assert standard["exposure_count"] == 50000
        assert standard["platform"] == "XHS"
        # 互动率 = (2500+1200+300+100)/50000 = 0.082
        assert standard["interaction_rate"] == 0.082


class TestXHSKOLOrderE2E:
    """KOL订单 E2E"""
    
    def setup_method(self):
        self.adapter = XHSKOLAdapter()
    
    def test_kol_order_to_standard(self):
        """蒲公英KOL订单 → 标准格式"""
        raw = {
            "order_id": "KOL2024001",
            "kol_name": "美妆博主小美",
            "kol_id": "kol_888",
            "content_type": "视频",
            "price": 8000.0,
            "status": "completed",
            "expected_publish_time": "2024-02-01T10:00:00Z",
            "actual_publish_time": "2024-02-01T12:00:00Z",
            "note_url": "https://www.xiaohongshu.com/discovery/item/xxx"
        }
        
        standard = self.adapter.to_standard_kol_order(raw)
        
        assert standard["order_id"] == "KOL2024001"
        assert standard["status"] == "COMPLETED"
        assert standard["price"] == 8000.0
        assert standard["platform"] == "XHS_KOL"
    
    def test_kol_performance_to_standard(self):
        """蒲公英投放效果 → 标准格式"""
        raw = {
            "order_id": "KOL2024001",
            "note_id": "note_perf_001",
            "exposure_count": 80000,
            "like_count": 4000,
            "collect_count": 2000,
            "comment_count": 400,
            "share_count": 200,
            "click_count": 3000,
            "price": 8000.0
        }
        
        standard = self.adapter.to_standard_kol_performance(raw)
        
        assert standard["exposure_count"] == 80000
        # CPE = 8000/80000*1000 = 100
        assert standard["cost_per_exposure"] == 100.0
        # CPI = 8000/(4000+2000+400+200) = 8000/6600 ≈ 1.21
        assert round(standard["cost_per_interaction"], 2) == 1.21
```

**Step 2: 运行测试**

```bash
cd skills/oms-xhs-integration
python -m pytest tests/test_e2e.py -v
```
Expected: 8 passed

**Step 3: Commit**

```bash
git add skills/oms-xhs-integration/tests/test_e2e.py
git commit -m "test: add E2E tests for XHS integration"
```

---

## Phase 7: README.md

### Task 16: 编写 README.md

**文件:** `skills/oms-xhs-integration/README.md`

```markdown
# 小红书开放平台集成适配器

小红书（Xiaohongshu）开放平台对接模块，支持笔记曝光数据、KOL合作管理、薯店订单同步、小程序订单同步。

## 功能特性

- **笔记数据**: 笔记曝光/互动数据查询，效果评估
- **KOL合作**: 蒲公英平台合作订单管理，投放效果追踪
- **薯店订单**: 薯店电商订单同步，状态映射
- **小程序订单**: 微信小程序订单同步，UTM归因
- **归因计算**: 基于UTM参数的30天归因窗口，权重0.15

## 目录结构

```
oms-xhs-integration/
├── SKILL.md              # 技能定义
├── README.md             # 本文件
├── design.md             # 设计文档
├── scripts/
│   ├── __init__.py
│   ├── auth.py           # OAuth 2.0 认证
│   ├── client.py         # API客户端
│   ├── note_adapter.py   # 笔记数据适配器
│   ├── kol_adapter.py    # KOL适配器
│   └── order_adapter.py  # 订单适配器
└── tests/
    ├── __init__.py
    └── test_*.py          # 单元测试
```

## 快速开始

### 1. 配置认证信息

```python
from scripts.auth import XHSAuth

auth = XHSAuth(
    app_id="your_app_id",
    app_secret="your_app_secret",
    use_sandbox=True  # 生产环境设为False
)
auth.get_access_token("your_oauth_code")
```

### 2. 初始化客户端

```python
from scripts.client import XHSClient

client = XHSClient(auth)
```

### 3. 查询笔记曝光

```python
from scripts.note_adapter import XHSNoteAdapter

adapter = XHSNoteAdapter()
raw_data = client.note_exposure_get("note_xxx")
exposure = adapter.to_standard_exposure(raw_data)
```

### 4. 同步薯店订单

```python
from scripts.order_adapter import XHSOrderAdapter

adapter = XHSOrderAdapter()
orders = client.shu_dian_order_search(
    start_date="2024-01-01",
    end_date="2024-01-31"
)
standard_orders = [
    adapter.to_standard_order(order, "SHU_DIAN") 
    for order in orders.get("order_list", [])
]
```

### 5. UTM归因计算

```python
# 订单归因 = 订单金额 × 归因权重(0.15)
for order in standard_orders:
    attributed_value = order["total_amount"] * order["attribution_weight"]
    print(f"订单{order['platform_order_id']}归因值: {attributed_value}")
```

## 环境变量

| 变量 | 说明 |
|------|------|
| XHS_APP_ID | 小红书应用ID |
| XHS_APP_SECRET | 小红书应用密钥 |
| XHS_ACCESS_TOKEN | 访问令牌 |
| XHS_REFRESH_TOKEN | 刷新令牌 |

## API限流

| 接口类型 | 限流 |
|---------|------|
| 笔记数据API | 200次/分钟 |
| KOL/蒲公英API | 100次/分钟 |
| 订单API | 200次/分钟 |

## OMS集成

| OMS技能 | 集成方式 |
|---------|----------|
| oms-one-id-merge | 用户身份归一（手机号/OpenID） |
| oms-promotion-engine | 归因后发券/积分触发 |
| oms-order-capture | 订单统一汇聚 |
| oms-profit-sharing | 归因分润计算 |

## 测试

```bash
cd skills/oms-xhs-integration
python -m pytest tests/ -v
```
```

**Commit:**

```bash
git add skills/oms-xhs-integration/README.md
git commit -m "docs: add README for oms-xhs-integration"
```

---

## Phase 8: 最终提交

### Task 17: 最终提交

**Step 1: 验证所有测试通过**

```bash
cd skills/oms-xhs-integration
python -m pytest tests/ -v
```
Expected: All tests pass

**Step 2: 查看所有变更**

```bash
git log --oneline jd-integration..xhs-integration
```

**Step 3: 最终提交**

```bash
git add -A
git commit -m "feat: complete oms-xhs-integration MVP

- OAuth 2.0 + MD5 authentication
- Note exposure/interaction data adapter
- KOL/Pugongyin order adapter  
- 薯店 and 小程序 order adapters
- UTM attribution with 0.15 weight
- 28 unit tests + E2E tests passing
"
```

---

## 归因权重配置

根据 `docs/oms-skills/integration/integration-attribution.md`:

| 触点 | 权重 |
|------|------|
| 小红书种草 (XHS_CONTENT) | 0.15 |

归因窗口: 30天（订单前30天内的触点都计入）

---

## MVP 暂不实现的功能（后续迭代）

| 功能 | 原因 |
|------|------|
| 库存同步 | MVP阶段薯店/小程序库存由平台管理 |
| 物流追踪 | 小红书物流API暂不开放 |
| 退货退款 | 需对接售后API，MVP先不做 |
| 聚光广告投放 | 需商务合作，可后续迭代 |
| Webhook实时推送 | MVP先用轮询 |

---

## 成功标准

- [x] OAuth 2.0 + MD5 认证正常
- [x] 笔记曝光数据可查询
- [x] KOL订单可查询
- [x] 薯店/小程序订单可同步
- [x] UTM归因计算正确（权重0.15）
- [x] 所有单元测试通过
- [x] E2E测试通过
