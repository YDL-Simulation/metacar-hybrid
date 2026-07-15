## 改动说明

请说明本次改动解决的问题、接口影响和兼容性考虑。

## 验证结果

- [ ] `python scripts/check_public_repository.py`
- [ ] `python -m pytest`
- [ ] `python -m build`
- [ ] `python -m twine check --strict dist/*`
- [ ] `python scripts/check_release_artifacts.py dist/*`
- [ ] `sphinx-build -W -E -b html docs docs/_build/html`

## 公开边界

- [ ] 不包含完整 `examples/main_hybrid.py`
- [ ] 不包含内部轨迹、地图、场景数据、实验结果或运行日志
- [ ] 不包含内部转弯策略、调度参数和调试阈值
- [ ] 不包含密钥、令牌、账号或内部服务地址
- [ ] 如果同步了上游，已更新 `UPSTREAM.md` 的标签、提交哈希和兼容性结果
