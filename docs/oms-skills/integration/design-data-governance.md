# 数据治理与隐私合规设计

本文档定义 OMS 系统的数据治理框架和隐私合规规范，确保数据安全与合规使用。

## 1. 数据治理框架

### 1.1 数据分类分级

```
┌─────────────────────────────────────────────────────────────────┐
│                        数据分类分级                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  等级    │ 名称        │ 示例                    │ 保护要求    │
│  ────────┼────────────┼─────────────────────────┼───────────── │
│  L4      │ 极高敏感    │ 支付密码、银行卡号        │ 加密+审计   │
│  L3      │ 高度敏感    │ 手机号、身份证、地址      │ 脱敏+访问控制│
│  L2      │ 中度敏感    │ 购买记录、行为偏好        │ 访问控制    │
│  L1      │ 低度敏感    │ 公开信息、统计数据        │ 基本保护    │
│  L0      │ 非敏感      │ 公开数据                  │ 无特殊要求  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 数据资产目录

| 资产类别 | 数据类型 | 分类等级 | 负责人 |
|----------|----------|----------|--------|
| 身份数据 | 手机号、OpenID、UnionID | L3 | DPO |
| 交易数据 | 订单、支付、退款 | L2 | 业务负责人 |
| 行为数据 | 浏览、点击、收藏 | L2 | 数据负责人 |
| 财务数据 | 分润、结算、凭证 | L3 | 财务负责人 |
| 运营数据 | 营销活动、优惠券 | L1 | 运营负责人 |

## 2. 隐私合规体系

### 2.1 法规对照

| 法规 | 适用范围 | 主要要求 |
|------|----------|----------|
| 《个人信息保护法》 | 中国境内的个人信息处理 | 知情同意、最小必要、目的限制 |
| 《数据安全法》 | 中国境内的数据处理 | 数据分类、安全保护 |
| GDPR | 欧盟用户 | 同意权、删除权、可携带权 |
| CCPA | 加州消费者 | 知情权、选择退出权 |

### 2.2 合规原则

| 原则 | 说明 | 实施措施 |
|------|------|----------|
| 知情同意 | 处理个人信息需用户明确同意 | 隐私协议、授权弹窗 |
| 最小必要 | 只收集处理必要的数据 | 字段审核、数据脱敏 |
| 目的限制 | 数据仅用于声明目的 | 访问审计、用例管控 |
| 安全保障 | 采取必要的安全措施 | 加密、访问控制、监控 |
| 主体权利 | 保障用户的各项权利 | 查询、更正、删除接口 |

## 3. 数据安全措施

### 3.1 传输安全

| 安全措施 | 说明 | 实施标准 |
|----------|------|----------|
| HTTPS | 加密传输 | TLS 1.3 |
| API 签名 | 请求防篡改 | HMAC-SHA256 |
| 证书固定 | 防止中间人攻击 | 证书PIN |

### 3.2 存储安全

| 数据类型 | 存储加密 | 脱敏规则 |
|----------|----------|----------|
| 手机号 | AES-256 | 138****8888 |
| 身份证号 | AES-256 | 110101****1234 |
| 银行卡号 | AES-256 | 不存储，仅存后4位 |
| 详细地址 | AES-256 | 脱敏到街道 |
| 邮箱 | AES-256 | u***@example.com |

### 3.3 访问控制

```python
# 访问控制模型 (RBAC + ABAC)
class AccessControl:
    """
    基于角色的访问控制 + 基于属性的访问控制
    
    角色: 运营、客服、财务、管理员
    属性: 数据分类、渠道、时效
    """
    
    def check_permission(self, user: User, resource: Resource, action: str) -> bool:
        # 1. 检查角色权限
        if not self.role_check(user.role, resource, action):
            return False
        
        # 2. 检查数据属性
        if not self.attribute_check(user, resource):
            return False
        
        # 3. 检查时效
        if not self.time_check(user, resource):
            return False
        
        return True
    
    def role_check(self, role, resource, action):
        permissions = {
            '运营': {'order:read': True, 'order:write': True},
            '客服': {'order:read': True, 'customer:phone': False},
            '财务': {'finance:read': True, 'customer:phone': False},
            '管理员': {'*': True}
        }
        return permissions.get(role, {}).get(f'{resource}:{action}', False)
```

## 4. 数据脱敏规范

### 4.1 脱敏规则表

| 数据类型 | 脱敏方式 | 示例 |
|----------|----------|------|
| 手机号 | 中间加密 | 138****8888 |
| 身份证 | 前后保留 | 110101****1234 |
| 姓名 | 仅保留首字 | 张* |
| 银行卡 | 仅保留后4位 | ****1234 |
| 邮箱 | 用户名加密 | u***@example.com |
| 地址 | 脱敏到街道 | 北京市朝阳区**街道 |
| 金额 | 保留区间 | 500-1000元 |

### 4.2 脱敏流程

```python
class DataMasking:
    """数据脱敏处理"""
    
    def mask_phone(self, phone: str) -> str:
        """手机号脱敏: 13812345678 → 138****8888"""
        if not phone or len(phone) < 7:
            return phone
        return phone[:3] + '****' + phone[-4:]
    
    def mask_id_card(self, id_card: str) -> str:
        """身份证脱敏: 110101199001011234 → 110101****1234"""
        if not id_card or len(id_card) < 10:
            return id_card
        return id_card[:6] + '****' + id_card[-4:]
    
    def mask_address(self, address: str, keep_level: int = 2) -> str:
        """
        地址脱敏
        
        Args:
            address: 完整地址
            keep_level: 保留层级 (1=省, 2=市/区)
        """
        parts = address.split(' ')
        if len(parts) <= keep_level:
            return address
        masked = ' '.join(parts[:keep_level]) + ' **'
        return masked
```

## 5. 同意授权管理

### 5.1 授权场景

| 场景 | 所需授权 | 授权方式 |
|------|----------|----------|
| 基础服务 | 服务必需 | 静默同意 |
| 营销推送 | 营销通知 | 明确授权 |
| 精准推荐 | 个性化推荐 | 明确授权 |
| 跨平台归因 | 数据共享 | 明确授权 |

### 5.2 授权状态机

```
┌─────────┐  用户同意  ┌─────────┐  用户撤回  ┌─────────┐
│ PENDING │────────→│ GRANTED │────────→│ REVOKED │
└─────────┘          └─────────┘          └─────────┘
     │                    │                    │
     │                    │ 重新同意           │ 重新同意
     │                    ▼                    ▼
     │              ┌─────────┐          ┌─────────┐
     └────────────→│ GRANTED │←─────────│ PENDING │
                    └─────────┘          └─────────┘
```

### 5.3 授权查询

```python
class ConsentManager:
    """用户授权管理"""
    
    def check_consent(self, one_id: str, purpose: str) -> bool:
        """
        检查用户是否已授权
        
        Args:
            one_id: 用户One-ID
            purpose: 授权目的 (marketing/precision_recommend/attribution)
        
        Returns:
            True=已授权, False=未授权
        """
        consent = self.consent_db.find_one(
            one_id=one_id,
            purpose=purpose,
            status='GRANTED',
            expired_at__gt=datetime.now()
        )
        return consent is not None
    
    def grant_consent(self, one_id: str, purpose: str, channel: str):
        """用户授权"""
        self.consent_db.create({
            'one_id': one_id,
            'purpose': purpose,
            'channel': channel,
            'status': 'GRANTED',
            'granted_at': datetime.now(),
            'expired_at': datetime.now() + timedelta(days=365)
        })
    
    def revoke_consent(self, one_id: str, purpose: str):
        """用户撤回授权"""
        self.consent_db.update(
            one_id=one_id,
            purpose=purpose,
            status='REVOKED',
            revoked_at=datetime.now()
        )
```

## 6. 数据主体权利

### 6.1 权利类型

| 权利 | 说明 | 实现方式 |
|------|------|----------|
| 知情权 | 了解数据处理情况 | 隐私协议、设置页面 |
| 查询权 | 查询个人数据 | 数据导出API |
| 更正权 | 修正错误数据 | 数据更正API |
| 删除权 | 删除个人数据 | 账号注销API |
| 限制权 | 限制数据处理 | 退出营销API |
| 便携权 | 导出个人数据 | 数据下载服务 |

### 6.2 用户数据接口

```python
class DataSubjectRights:
    """数据主体权利接口"""
    
    def query_data(self, one_id: str) -> dict:
        """
        查询用户所有数据
        实现: 知情权、查询权
        """
        return {
            'identities': self.get_identities(one_id),
            'orders': self.get_orders(one_id),
            'behaviors': self.get_behaviors(one_id),
            'preferences': self.get_preferences(one_id),
            'consents': self.get_consents(one_id)
        }
    
    def export_data(self, one_id: str, format: str = 'json') -> bytes:
        """
        导出用户数据
        实现: 便携权
        """
        data = self.query_data(one_id)
        if format == 'json':
            return json.dumps(data, ensure_ascii=False)
        elif format == 'csv':
            return self.to_csv(data)
    
    def delete_data(self, one_id: str, scope: str = 'all'):
        """
        删除用户数据
        实现: 删除权
        
        Args:
            scope: all=全部删除, partial=保留必要数据
        """
        if scope == 'all':
            # 全量删除（法律保留除外）
            self.delete_identities(one_id)
            self.delete_orders(one_id)
            self.delete_behaviors(one_id)
            self.delete_profile(one_id)
        else:
            # 保留订单等必要数据
            self.delete_behaviors(one_id)
            self.delete_profile(one_id)
```

## 7. 数据生命周期

### 7.1 数据保留期

| 数据类型 | 保留期 | 删除规则 |
|----------|--------|----------|
| 行为日志 | 2年 | 到期或用户删除 |
| 订单数据 | 5年 | 法律保留 |
| 财务数据 | 10年 | 法定保留 |
| 身份数据 | 永久 | 账户存续期间 |
| 授权记录 | 5年 | 到期自动删除 |

### 7.2 数据删除流程

```python
class DataLifecycleManager:
    """数据生命周期管理"""
    
    def schedule_deletion(self, one_id: str, reason: str):
        """用户注销，调度数据删除"""
        # 1. 检查法律保留要求
        legal_holds = self.check_legal_holds(one_id)
        
        # 2. 执行删除
        deletion_job = {
            'one_id': one_id,
            'reason': reason,
            'delete_at': datetime.now() + timedelta(days=30),  # 30天冷静期
            'legal_holds': legal_holds,
            'status': 'pending'
        }
        self.deletion_jobs.create(deletion_job)
    
    def execute_deletion(self, job_id: str):
        """执行删除任务"""
        job = self.deletion_jobs.get(job_id)
        
        # 1. 删除可删除数据
        if not job.legal_holds:
            self.delete_all_data(job.one_id)
        else:
            # 保留法律保留数据
            self.delete_non_legal_data(job.one_id)
        
        # 2. 记录删除凭证
        self.deletion_records.create({
            'job_id': job_id,
            'deleted_at': datetime.now(),
            'deleted_by': 'system'
        })
        
        # 3. 更新状态
        self.deletion_jobs.update(job_id, status='completed')
```

## 8. 安全审计

### 8.1 审计日志

```sql
CREATE TABLE audit_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    event_type VARCHAR(64) NOT NULL COMMENT '事件类型',
    operator_id VARCHAR(64) COMMENT '操作人ID',
    operator_type VARCHAR(32) COMMENT '操作人类型:user/system/admin',
    resource_type VARCHAR(64) COMMENT '资源类型',
    resource_id VARCHAR(64) COMMENT '资源ID',
    action VARCHAR(32) NOT NULL COMMENT '操作:read/write/delete',
    data_before TEXT COMMENT '操作前数据(脱敏)',
    data_after TEXT COMMENT '操作后数据(脱敏)',
    ip_address VARCHAR(64) COMMENT 'IP地址',
    user_agent VARCHAR(256) COMMENT 'UserAgent',
    result VARCHAR(16) COMMENT '结果:success/fail',
    error_msg TEXT COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_operator (operator_id, created_at),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_event_type (event_type, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 8.2 审计事件类型

| 事件类型 | 说明 | 风险等级 |
|----------|------|----------|
| IDENTITY_QUERY | 身份查询 | 中 |
| IDENTITY_MERGE | 身份合并 | 高 |
| ORDER_EXPORT | 订单导出 | 高 |
| CUSTOMER_PHONE_VIEW | 手机号查看 | 高 |
| DATA_DELETE | 数据删除 | 高 |
| CONSENT_REVOKE | 授权撤回 | 中 |
| LOGIN_SUCCESS | 登录成功 | 低 |
| LOGIN_FAIL | 登录失败 | 中 |

### 8.3 告警规则

```yaml
alert_rules:
  - name: 批量手机号查询
    condition: count(operator_id, 1h) > 100 AND resource_type == "phone"
    severity: high
    action: 暂停操作并告警
  
  - name: 异常数据导出
    condition: data_volume > 10000 AND action == "export"
    severity: high
    action: 告警并人工审核
  
  - name: 频繁登录失败
    condition: count(operator_id, 10m) > 5 AND result == "fail"
    severity: medium
    action: 临时锁定账户
```

## 9. 合规检查清单

| 检查项 | 周期 | 负责人 |
|--------|------|--------|
| 隐私协议更新 | 每年 | DPO |
| 数据分类分级审查 | 每季度 | 数据负责人 |
| 权限梳理 | 每季度 | 安全团队 |
| 审计日志审查 | 每月 | 合规团队 |
| 漏洞扫描 | 每月 | 安全团队 |
| 数据删除记录检查 | 每月 | DPO |
| 第三方数据共享审查 | 每次 | DPO |
