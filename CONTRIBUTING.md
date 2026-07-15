# 贡献指南

MetaCar Hybrid 对外仓库只包含可公开的 SDK、基础示例、文档和测试。
内部轨迹跟踪、转弯策略、调试参数和完整场景测试代码不属于本仓库的贡献范围。

## 开发环境

```bash
python -m venv .venv
python -m pip install -e ".[test,examples]" build twine
```

## 提交前检查

```bash
python -m pytest
python -m build
python -m twine check --strict dist/*
python scripts/check_release_artifacts.py dist/*
```

Pull Request 应说明：

1. 改动解决了什么问题。
2. 是否影响原版 `set_vehicle_control()` 兼容性。
3. 是否改动 `HybridControl` 消息格式。
4. 已运行哪些测试和实际场景验证。

## 同步上游

同步 `YDL-Simulation/autodrive_api_python` 后，请在 `UPSTREAM.md` 中记录上游标签、
提交哈希和兼容性测试结果。
