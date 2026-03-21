#!/usr/bin/env python3
"""
OMS Skills 测试框架
支持自动化测试所有OMS技能脚本
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 技能脚本配置
SKILLS = {
    "oms-inventory-realtime": {
        "script": "inventory_query.py",
        "actions": ["query", "check_overselling", "pre_reserve", "release"]
    },
    "oms-inventory-ringfence": {
        "script": "ringfence_manager.py", 
        "actions": ["set_ringfence", "release_ringfence", "check", "store_check"]
    },
    "oms-order-capture": {
        "script": "order_processor.py",
        "actions": ["normalize", "detect_scalper", "deduplicate"]
    },
    "oms-one-id-merge": {
        "script": "one_id_manager.py",
        "actions": ["identify", "merge", "resolve_conflict", "build_profile"]
    },
    "oms-order-routing": {
        "script": "order_router.py",
        "actions": ["route", "split"]
    },
    "oms-promotion-engine": {
        "script": "promotion_calculator.py",
        "actions": ["calculate_discount", "issue_coupon", "calculate_points"]
    },
    "oms-profit-sharing": {
        "script": "profit_calculator.py",
        "actions": ["calculate_commission", "distribute_profit", "generate_settlement"]
    },
    "oms-reconciliation": {
        "script": "reconciliation.py",
        "actions": ["reconcile", "generate_voucher", "export_report"]
    },
    "oms-returns-crosschannel": {
        "script": "return_handler.py",
        "actions": ["check_eligibility", "process_refund", "process_exchange", "crosschannel_return"]
    },
    "oms-returns-logistics": {
        "script": "return_logistics.py",
        "actions": ["track", "quality_check", "classify_defect", "recycle"]
    }
}


# 测试用例数据
TEST_CASES = {
    "oms-inventory-realtime": {
        "query": {
            "sku_id": "SKU001",
            "warehouse": "SH"
        },
        "check_overselling": {
            "sku_id": "SKU001",
            "quantity": 100
        },
        "pre_reserve": {
            "sku_id": "SKU001",
            "quantity": 10,
            "order_id": "ORD_TEST_001",
            "timeout_minutes": 15
        }
    },
    "oms-inventory-ringfence": {
        "set_ringfence": {
            "sku_id": "SKU001",
            "channel": "douyin",
            "quantity": 50,
            "reason": "直播间专供"
        },
        "check": {
            "sku_id": "SKU001",
            "channel": "douyin",
            "quantity": 10
        }
    },
    "oms-order-capture": {
        "normalize": {
            "order": {
                "order_id": "ORD_TEST_001",
                "source_order_id": "TB123456",
                "channel": "taobao",
                "phone": "13800138000",
                "receiver_address": "上海市浦东新区张江路100号",
                "items": [{"sku_code": "SKU001", "num": 2, "price": 99.00}],
                "goods_amount": 198.00,
                "shipping_fee": 10.00,
                "discount_amount": 20.00,
                "total_amount": 188.00,
                "created_time": "2024-01-20T10:00:00"
            }
        },
        "detect_scalper": {
            "order": {
                "order_id": "ORD_TEST_002",
                "phone": "17012345678",
                "receiver_address": "上海市 ***",
                "items": [{"sku_id": "SKU001", "quantity": 10}],
                "customer": {"phone": "17012345678"}
            }
        }
    },
    "oms-one-id-merge": {
        "identify": {
            "identifier": {"type": "phone", "value": "13800138000"}
        },
        "build_profile": {
            "one_id": "OID_TEST_001"
        }
    },
    "oms-order-routing": {
        "route": {
            "order": {
                "order_id": "ORD_TEST_001",
                "customer_lat": 31.2304,
                "customer_lon": 121.4737
            },
            "warehouses": [
                {"id": "WH001", "name": "上海仓", "lat": 31.2304, "lon": 121.4737},
                {"id": "WH002", "name": "武汉仓", "lat": 30.5928, "lon": 114.3055}
            ],
            "stores": [
                {"id": "STORE001", "name": "浦东店", "lat": 31.2304, "lon": 121.4737}
            ]
        },
        "split": {
            "order": {"order_id": "ORD_TEST_002"},
            "items": [
                {"sku_id": "SKU001", "quantity": 2, "preferred_warehouse": "WH001"}
            ],
            "warehouses": [
                {"id": "WH001", "name": "上海仓", "lat": 31.2304, "lon": 121.4737}
            ]
        }
    },
    "oms-promotion-engine": {
        "calculate_discount": {
            "order": {
                "order_id": "ORD_TEST_001",
                "goods_amount": 200.00,
                "items": [{"sku_id": "SKU001", "price": 100.00, "quantity": 2}]
            },
            "promotions": [
                {
                    "promo_id": "P001",
                    "type": "COUPON",
                    "discount_type": "FIXED",
                    "discount_value": 20,
                    "min_amount": 100,
                    "start_time": "2024-01-01",
                    "end_time": "2024-12-31",
                    "remaining_quota": 1000
                }
            ]
        }
    },
    "oms-profit-sharing": {
        "calculate_commission": {
            "order": {
                "order_id": "ORD_TEST_001",
                "order_amount": 188.00,
                "source_channel": "taobao",
                "category": "ELECTRONICS"
            },
            "commission_rules": {
                "channels": {
                    "taobao": {
                        "categories": {
                            "ELECTRONICS": {
                                "commission_rate": 0.05,
                                "platform_fee_rate": 0.02
                            }
                        }
                    }
                }
            }
        }
    },
    "oms-reconciliation": {
        "reconcile": {
            "platform_bills": [
                {"channel": "taobao", "order_id": "ORD001", "amount": 100.00},
                {"channel": "taobao", "order_id": "ORD002", "amount": 200.00}
            ],
            "system_bills": [
                {"channel": "taobao", "order_id": "ORD001", "amount": 100.00},
                {"channel": "taobao", "order_id": "ORD002", "amount": 180.00}
            ]
        }
    },
    "oms-returns-crosschannel": {
        "check_eligibility": {
            "order": {
                "order_id": "ORD_TEST_001",
                "created_at": "2024-01-20T10:00:00",
                "max_return_days": 7,
                "items": [{"sku_id": "SKU001", "final_price": 99.00}],
                "return_status": None
            },
            "return_request": {}
        },
        "process_refund": {
            "return_request": {
                "refund_method": "ORIGINAL",
                "include_shipping": False,
                "coupon_returned": True
            },
            "order": {
                "order_id": "ORD_TEST_001",
                "items": [
                    {"sku_id": "SKU001", "final_price": 99.00}
                ],
                "shipping_fee": 10.00
            }
        },
        "process_exchange": {
            "return_request": {
                "target_sku": "SKU002",
                "price_difference": 0
            },
            "order": {
                "order_id": "ORD_TEST_001",
                "items": [
                    {"sku_id": "SKU001", "final_price": 99.00}
                ]
            }
        },
        "crosschannel_return": {
            "return_request": {
                "return_id": "RET001",
                "original_channel": "taobao",
                "return_channel": "jd",
                "customer_location": {}
            },
            "warehouses": [
                {"id": "WH001", "name": "上海仓"}
            ]
        }
    },
    "oms-returns-logistics": {
        "track": {
            "tracking_number": "RTN123456789"
        },
        "quality_check": {
            "check_request": {
                "return_id": "RET001",
                "sku_id": "SKU001",
                "quantity": 1
            }
        }
    }
}


class OMSTestRunner:
    def __init__(self, skills_dir: str = None):
        self.skills_dir = Path(skills_dir) if skills_dir else Path(__file__).parent
        self.results = []
    
    def run_single_test(self, skill_name: str, action: str, test_data: dict) -> dict:
        """运行单个测试"""
        skill_config = SKILLS.get(skill_name)
        if not skill_config:
            return {"success": False, "error": f"Skill {skill_name} not found"}
        
        # 技能脚本在 skills 子目录中
        script_candidates = [
            self.skills_dir / skill_name / "scripts" / skill_config["script"],
            self.skills_dir / skill_name / skill_config["script"]
        ]
        
        script_path = None
        for p in script_candidates:
            if p.exists():
                script_path = p
                break
        
        if script_path is None:
            return {"success": False, "error": f"Script not found: {script_candidates}"}
        
        if not script_path.exists():
            return {"success": False, "error": f"Script not found: {script_path}"}
        
        # 准备输入数据
        input_data = {"action": action, **test_data}
        
        # 写入临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(input_data, f, ensure_ascii=False)
            input_file = f.name
        
        try:
            result = subprocess.run(
                ["python3", str(script_path), input_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            try:
                json_output = json.loads(output)
                success = result.returncode == 0 and "error" not in json_output
            except:
                success = False
                json_output = {"raw_output": output, "error": "Failed to parse JSON"}
            
            return {
                "success": success,
                "skill": skill_name,
                "action": action,
                "returncode": result.returncode,
                "output": json_output,
                "stderr": result.stderr[:500] if result.stderr else ""
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "skill": skill_name,
                "action": action,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "skill": skill_name,
                "action": action,
                "error": str(e)
            }
        finally:
            import os
            os.unlink(input_file)
    
    def run_all_tests(self) -> dict:
        """运行所有测试"""
        print("=" * 70)
        print("OMS Skills 自动化测试")
        print("=" * 70)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        total_tests = 0
        passed_tests = 0
        failed_tests = []
        
        for skill_name, config in SKILLS.items():
            print(f"\n📦 测试技能: {skill_name}")
            print("-" * 50)
            
            for action in config["actions"]:
                test_data = TEST_CASES.get(skill_name, {}).get(action, {})
                if not test_data:
                    test_data = {}  # 使用空数据测试
                
                result = self.run_single_test(skill_name, action, test_data)
                total_tests += 1
                
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                print(f"  {action}: {status}")
                
                if result["success"]:
                    passed_tests += 1
                else:
                    failed_tests.append({
                        "skill": skill_name,
                        "action": action,
                        "error": result.get("error", result.get("stderr", "Unknown"))
                    })
        
        print("\n" + "=" * 70)
        print("测试结果汇总")
        print("=" * 70)
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {total_tests - passed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests:
            print("\n❌ 失败详情:")
            for f in failed_tests:
                print(f"  - {f['skill']}.{f['action']}: {f['error']}")
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "pass_rate": f"{passed_tests/total_tests*100:.1f}%",
            "failed_tests": failed_tests
        }
    
    def run_skill_tests(self, skill_name: str) -> dict:
        """测试指定技能"""
        if skill_name not in SKILLS:
            return {"error": f"Skill {skill_name} not found"}
        
        print(f"\n📦 测试技能: {skill_name}")
        print("-" * 50)
        
        config = SKILLS[skill_name]
        results = []
        
        for action in config["actions"]:
            test_data = TEST_CASES.get(skill_name, {}).get(action, {})
            result = self.run_single_test(skill_name, action, test_data)
            results.append(result)
            
            status = "✅" if result["success"] else "❌"
            print(f"  {action}: {status}")
        
        passed = sum(1 for r in results if r["success"])
        print(f"\n通过: {passed}/{len(results)}")
        
        return {"skill": skill_name, "results": results}
    
    def run_action_tests(self, action_chain: list) -> dict:
        """
        测试技能链 - 模拟完整业务流程
        action_chain: [{"skill": "xxx", "action": "yyy", "input": {...}}]
        """
        print("\n🔗 测试技能链")
        print("-" * 50)
        
        results = []
        
        for i, step in enumerate(action_chain):
            skill = step.get("skill")
            action = step.get("action")
            input_data = step.get("input", {})
            
            print(f"\n[Step {i+1}] {skill}.{action}")
            
            result = self.run_single_test(skill, action, input_data)
            results.append(result)
            
            if result["success"]:
                print(f"  ✅ 成功")
                # 将输出传递给下一步（可选）
            else:
                print(f"  ❌ 失败: {result.get('error', 'Unknown')}")
                break
        
        return {"chain_results": results}


def main():
    runner = OMSTestRunner()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--skill" and len(sys.argv) > 2:
            # 测试指定技能
            runner.run_skill_tests(sys.argv[2])
        elif sys.argv[1] == "--chain":
            # 测试技能链 - 从文件读取
            with open(sys.argv[2], 'r') as f:
                chain = json.load(f)
            runner.run_action_tests(chain)
        elif sys.argv[1] == "--example":
            # 运行示例流程测试
            example_chain = [
                {"skill": "oms-order-capture", "action": "normalize", "input": {"order": {
                    "order_id": "ORD_TEST", "source_order_id": "TB123",
                    "channel": "taobao", "phone": "13800138000",
                    "receiver_address": "上海浦东", "items": [{"sku_code": "SKU001", "num": 1, "price": 100}],
                    "goods_amount": 100, "shipping_fee": 10, "discount_amount": 0, "total_amount": 110
                }}},
                {"skill": "oms-inventory-realtime", "action": "check_overselling", "input": {
                    "sku_id": "SKU001", "quantity": 1
                }},
                {"skill": "oms-promotion-engine", "action": "calculate_discount", "input": {
                    "order": {"order_id": "ORD_TEST", "goods_amount": 100, "items": []},
                    "promotions": [{"promo_id": "P1", "type": "COUPON", "discount_type": "FIXED",
                                   "discount_value": 10, "min_amount": 50, "start_time": "2024-01-01",
                                   "end_time": "2024-12-31", "remaining_quota": 100}]
                }}
            ]
            runner.run_action_tests(example_chain)
        else:
            print("用法:")
            print("  python test_framework.py --all        # 运行所有测试")
            print("  python test_framework.py --skill <name>  # 测试指定技能")
            print("  python test_framework.py --chain <file>  # 测试技能链")
            print("  python test_framework.py --example       # 运行示例流程")
    else:
        # 运行所有测试
        runner.run_all_tests()


if __name__ == "__main__":
    main()
